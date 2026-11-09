import time
import sys
import json
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

CACHE_TOKEN_FILE = Path.home() / ".kipapp" / "session_token.json"

def get_browser_data_dir(custom_path: str = "") -> Path:
    if custom_path:
        p = Path(custom_path).expanduser().resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p
    cwd_dir = Path.cwd() / "browser_data"
    if cwd_dir.exists():
        return cwd_dir
    script_dir = Path(__file__).parent / "browser_data"
    if script_dir.exists():
        return script_dir
    home_dir = Path.home() / ".kipapp" / "browser_data"
    home_dir.mkdir(parents=True, exist_ok=True)
    return home_dir

def main():
    user_data_dir = get_browser_data_dir()
    print("=" * 60)
    print("Membuka browser untuk login KIPApp BPS...")
    print(f"Profil browser disimpan di: {user_data_dir.resolve()}")
    print("=" * 60)

    captured_token = None

    with sync_playwright() as p:
        # Launch persistent context agar session/cookies tetap tersimpan
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )

        def on_req(r):
            nonlocal captured_token
            if "x-auth" in r.headers:
                captured_token = r.headers["x-auth"]

        context.on("request", on_req)

        page = context.pages[0] if context.pages else context.new_page()
        page.on("request", on_req)
        
        print("\nMembuka https://kipapp.bps.go.id ...")
        page.goto("https://kipapp.bps.go.id", wait_until="networkidle")

        print("\n>>> SILAKAN LOGIN DI JENDELA BROWSER YANG TERBUKA <<<")
        print("Sistem akan otomatis mendeteksi ketika Anda berhasil login...")
        print("(Browser akan otomatis tertutup dan sesi disimpan setelah login terdeteksi)\n")

        last_url = ""
        start_time = time.time()
        timeout = 600 # 10 menit
        login_detected = False

        try:
            while time.time() - start_time < timeout:
                try:
                    # Periksa setiap tab yang aktif
                    for pg in context.pages:
                        if pg.is_closed():
                            continue
                        cur_url = pg.url
                        
                        # Cek apakah URL menunjukkan berhasil login ke KIPApp
                        is_kipapp = "kipapp.bps.go.id" in cur_url
                        is_login_page = any(k in cur_url.lower() for k in ["auth/login", "sso", "login"])
                        
                        # Deteksi menu utama / pelaksanaan-aksi / home
                        has_menu = False
                        try:
                            has_menu = pg.locator(".ant-menu, a[href*='pelaksanaan-aksi'], button:has-text('Tambah')").count() > 0
                        except Exception:
                            pass
                        
                        if is_kipapp and (not is_login_page or has_menu):
                            if any(k in cur_url for k in ["#/home", "#/pelaksanaan-aksi", "#/skp", "#/kegiatan"]) or has_menu:
                                print(f"\n[{time.strftime('%H:%M:%S')}] Login berhasil terdeteksi pada URL: {cur_url}")
                                login_detected = True
                                
                                # Navigasi singkat atau tunggu sebentar untuk memastikan request x-auth terpancar
                                if not captured_token:
                                    try:
                                        pg.goto("https://kipapp.bps.go.id/#/pelaksanaan-aksi", wait_until="commit")
                                        time.sleep(2)
                                    except Exception:
                                        pass
                                break

                    if login_detected:
                        time.sleep(1.5)
                        break

                    # Monitor perubahan URL di halaman utama
                    if not page.is_closed():
                        current_url = page.url
                        if current_url != last_url:
                            print(f"[{time.strftime('%H:%M:%S')}] URL: {current_url}")
                            last_url = current_url
                            screenshot_path = Path(__file__).parent / "current_page.png"
                            try:
                                page.screenshot(path=str(screenshot_path))
                            except Exception:
                                pass

                    time.sleep(1.5)
                except Exception as inner_e:
                    if "Target closed" in str(inner_e) or "has been closed" in str(inner_e):
                        print("Browser telah ditutup oleh pengguna.")
                        break
                    time.sleep(1.5)

        except KeyboardInterrupt:
            print("\nProses dihentikan oleh pengguna.")
        finally:
            print("\nMenyimpan sesi browser...")
            context.close()
            print("Sesi browser berhasil disimpan di ./browser_data!")

            # Jika berhasil menangkap token x-auth, simpan langsung ke cache
            if captured_token:
                try:
                    CACHE_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
                    nip_lama = None
                    try:
                        raw_jwt = captured_token.replace("Bearer ", "").strip()
                        parts = raw_jwt.split(".")
                        if len(parts) >= 2:
                            payload_b64 = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
                            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
                            nip_lama = payload.get("nip") or payload.get("nip-lama")
                    except Exception:
                        pass

                    with open(CACHE_TOKEN_FILE, "w", encoding="utf-8") as f:
                        json.dump({
                            "token": captured_token,
                            "nip_lama": nip_lama,
                            "timestamp": time.time()
                        }, f, indent=2)
                    print(f"[API] Token sesi ({captured_token[:20]}...) berhasil disimpan ke cache.")
                except Exception as ce:
                    print(f"[WARNING] Gagal menulis cache token: {ce}")

            if login_detected:
                print("=" * 60)
                print(">>> LOGIN BERHASIL & SESI AKTIF TERSIMPAN! <<<")
                print("Browser telah ditutup otomatis. Anda siap menggunakan REST API.")
                print("=" * 60)

if __name__ == "__main__":
    main()
