import time
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

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

        page = context.pages[0] if context.pages else context.new_page()
        
        print("\nMembuka https://kipapp.bps.go.id ...")
        page.goto("https://kipapp.bps.go.id", wait_until="networkidle")

        print("\n>>> SILAKAN LOGIN DI JENDELA BROWSER YANG TERBUKA <<<")
        print("Sistem sedang memantau status login dan halaman yang Anda buka...")
        print("(Setelah Anda login dan membuka halaman kegiatan, script akan mencatat struktur halamannya)\n")

        last_url = ""
        # Monitor selama 10 menit atau sampai user selesai
        start_time = time.time()
        timeout = 600 # 10 menit
        
        try:
            while time.time() - start_time < timeout:
                try:
                    current_url = page.url
                    if current_url != last_url:
                        print(f"[{time.strftime('%H:%M:%S')}] URL berubah: {current_url}")
                        last_url = current_url
                        
                        # Simpan screenshot berkala saat URL berubah
                        screenshot_path = Path(__file__).parent / "current_page.png"
                        page.screenshot(path=str(screenshot_path))
                    
                    time.sleep(2)
                except Exception as inner_e:
                    # Mungkin halaman ditutup oleh user
                    if "Target closed" in str(inner_e) or "has been closed" in str(inner_e):
                        print("Browser telah ditutup oleh pengguna.")
                        break
                    time.sleep(2)

        except KeyboardInterrupt:
            print("\nProses dihentikan oleh pengguna.")
        finally:
            print("\nMenyimpan sesi browser...")
            context.close()
            print("Sesi browser berhasil disimpan di ./browser_data!")

if __name__ == "__main__":
    main()
