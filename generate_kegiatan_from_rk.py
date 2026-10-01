import json
import time
import random
import datetime
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

def get_browser_data_dir(custom_path: str = "") -> Path:
    """
    Menemukan direktori browser_data secara dinamis:
    1. Jika ditentukan lewat parameter custom_path
    2. Jika ada folder browser_data di project folder pengguna saat ini (Path.cwd())
    3. Jika ada folder browser_data di samping skrip
    4. Default ke ~/.kipapp/browser_data (persisten antar seluruh project pengguna)
    """
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

def clean_rk_topic(rk_text: str) -> str:
    """
    Ekstrak topik inti dari kalimat Rencana Kinerja BPS
    Contoh: 'Terlaksanakannya kegiatan pengolahan yang berkualitas dan tepat waktu'
            -> 'pengolahan'
    """
    text = rk_text.strip()
    lower = text.lower()
    
    # Hilangkan prefix umum pada SKP BPS
    prefixes = [
        "terlaksanakannya kegiatan pengelolaan ",
        "terlaksananya kegiatan pengelolaan ",
        "terlaksanakannya kegiatan pengembangan ",
        "terlaksananya kegiatan pengembangan ",
        "terlaksanakannya kegiatan pembinaan ",
        "terlaksananya kegiatan pembinaan ",
        "terlaksanakannya kegiatan ",
        "terlaksananya kegiatan ",
        "terlaksanakannya tata kelola ",
        "terlaksananya tata kelola ",
        "terlaksanakannya pengelolaan ",
        "terlaksananya pengelolaan ",
        "terlaksanakannya ",
        "terlaksananya ",
        "tersedianya laporan monitoring kegiatan ",
        "tersedianya laporan monitoring ",
        "tersedianya laporan ",
        "tersedianya dokumen ",
        "tersedianya data ",
        "tersedianya publikasi ",
        "tersedianya ",
        "meningkatnya kualitas ",
        "meningkatnya ",
    ]
    for p in prefixes:
        if lower.startswith(p):
            text = text[len(p):].strip()
            lower = text.lower()
            break
            
    # Hilangkan suffix umum
    suffixes = [
        " yang berkualitas dan tepat waktu",
        " yang berkualitas & tepat waktu",
        " yang berkualitas",
        " yang tepat waktu",
        " yang tertib",
        " yang akuntabel",
        " secara optimal",
    ]
    for s in suffixes:
        if lower.endswith(s):
            text = text[:-len(s)].strip()
            lower = text.lower()
            break
            
    return text if text else rk_text

def get_distinctive_keyword(rk_text: str) -> str:
    """
    Mengambil potongan kata kunci pembeda (2-4 kata) dari RK
    untuk dicocokkan pada dropdown select KIPApp
    """
    topic = clean_rk_topic(rk_text)
    words = [w for w in topic.split() if len(w) > 2]
    if len(words) >= 3:
        return " ".join(words[:3])
    elif words:
        return " ".join(words)
    return rk_text[:30]

def dynamic_generate_activities_for_topic(topic: str) -> list[tuple[str, str]]:
    """
    Menghasilkan 4 variasi tahapan kegiatan kerja realistis untuk topik RK apa pun
    """
    return [
        (
            f"Koordinasi teknis dan penyiapan bahan pelaksanaan {topic}",
            f"Tersusunnya bahan kerja dan kesepakatan teknis pelaksanaan {topic}"
        ),
        (
            f"Pelaksanaan dan pengolahan data/dokumen terkait {topic}",
            f"Terselesaikannya tahapan pelaksanaan {topic} sesuai standar operasional"
        ),
        (
            f"Pemeriksaan kelengkapan, validasi anomali, dan verifikasi {topic}",
            f"Terverifikasinya kelengkapan dan akurasi hasil {topic}"
        ),
        (
            f"Penyusunan laporan progres dan evaluasi hasil pelaksanaan {topic}",
            f"Tersusunnya laporan evaluasi dan dokumentasi capaian {topic}"
        )
    ]

import re

def get_period_dates(periode_str: str, tahun: int = None) -> tuple[str, str, str]:
    """
    Menormalkan nama triwulan dan menghitung rentang tanggal default (start, end)
    Contoh: 'Triwulan 1' -> ('Triwulan I', '2026-01-01', '2026-03-31')
    """
    p = str(periode_str).strip().lower()
    if tahun is None or not str(tahun).isdigit():
        tahun = datetime.date.today().year
        for token in p.split():
            if token.isdigit() and len(token) == 4:
                tahun = int(token)
    else:
        tahun = int(tahun)

    if re.search(r'\b(tw|triwulan)?\s*(iv|4)\b', p):
        return "Triwulan IV", f"{tahun}-10-01", f"{tahun}-12-31"
    elif re.search(r'\b(tw|triwulan)?\s*(iii|3)\b', p):
        return "Triwulan III", f"{tahun}-07-01", f"{tahun}-09-30"
    elif re.search(r'\b(tw|triwulan)?\s*(ii|2)\b', p):
        return "Triwulan II", f"{tahun}-04-01", f"{tahun}-06-30"
    elif re.search(r'\b(tw|triwulan)?\s*(i|1)\b', p):
        return "Triwulan I", f"{tahun}-01-01", f"{tahun}-03-31"
    elif "tahunan" in p:
        return "Tahunan", f"{tahun}-01-01", f"{tahun}-12-31"
        
    return periode_str, f"{tahun}-04-01", f"{tahun}-06-30"

def fetch_user_rencana_kinerja(periode_keyword: str = "Triwulan II", tahun: str = "", browser_data: str = "") -> list[str]:
    """
    Membaca seluruh opsi butir Rencana Kinerja (SKP) pengguna yang aktif.
    Mengutamakan REST API langsung untuk kecepatan milidetik, dengan fallback ke Playwright browser.
    """
    norm_periode, _, _ = get_period_dates(periode_keyword, int(tahun) if str(tahun).isdigit() else None)
    
    # 1. Coba via REST API KIPApp terlebih dahulu (Super Cepat ~0.2 detik)
    try:
        from kipapp_api import KipappAPI
        api = KipappAPI(browser_data=browser_data)
        th = int(tahun) if str(tahun).isdigit() else 2026
        skp = api.get_skp_by_periode(norm_periode, tahun=th)
        if skp:
            skpid = str(skp.get("id"))
            rks = api.get_rencana_kinerja(skpid)
            rk_texts = [r.get("rencanakinerja", "").strip() for r in rks if r.get("rencanakinerja")]
            if rk_texts:
                print(f"\n[1/2] Berhasil membaca {len(rk_texts)} butir Rencana Kinerja aktif via REST API ({norm_periode}).")
                return rk_texts
    except Exception as api_err:
        print(f"[API] Fallback ke browser otomasi: {api_err}")

    # 2. Fallback via Playwright Browser Otomasi
    user_data_dir = get_browser_data_dir(browser_data)
    print(f"\n[1/2] Menghubungkan ke KIPApp via browser untuk membaca Rencana Kinerja ({norm_periode})...")
    print(f"      Profil Browser: {user_data_dir}")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://kipapp.bps.go.id/#/pelaksanaan-aksi", wait_until="networkidle")
        time.sleep(2)
        page.evaluate("() => document.querySelectorAll('.ant-modal-wrap, .ant-modal-mask').forEach(e => e.remove())")
        
        # Pilih Tahun jika ada
        if tahun:
            tahun_dropdown = page.locator(".ant-select").nth(1)
            tahun_dropdown.click(force=True)
            time.sleep(0.8)
            opt_tahun = page.locator(f".ant-select-dropdown li:has-text('{tahun}')").first
            if opt_tahun.is_visible():
                opt_tahun.click(force=True)
                time.sleep(1.5)

        # Pilih Periode SKP
        skp_dropdown = page.locator(".ant-select").nth(2)
        skp_dropdown.click(force=True)
        time.sleep(1)
        target = page.locator(f".ant-select-dropdown li:has-text('{norm_periode}')").first
        if not target.is_visible():
            target = page.locator(f".ant-select-dropdown li:has-text('{periode_keyword}')").first

        if target.is_visible():
            target.click(force=True)
            time.sleep(2)
        else:
            print(f"[WARNING] Periode '{norm_periode}' (atau '{periode_keyword}') tidak ditemukan di dropdown.")
            
        # Buka modal Add
        add_btn = page.locator("button:has-text('+ Add'), button:has-text('Add')").first
        add_btn.click()
        time.sleep(1.5)
        
        modal = page.locator(".ant-modal-content")
        modal.locator(".ant-select:has-text('Pilih rencana kinerja SKP')").first.click(force=True)
        time.sleep(1)
        
        raw_options = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden) li.ant-select-dropdown-menu-item:not(.ant-select-dropdown-menu-item-group)").all_text_contents()
        modal.locator("button:has-text('Cancel')").first.click()
        ctx.close()
        
        rk_list = []
        for opt in raw_options:
            clean = opt.strip()
            # Filter baris gabungan/header/periode
            if "\n" in clean or "Triwulan" in clean or not clean:
                continue
            rk_list.append(clean)
            
        print(f"[2/2] Berhasil mengambil {len(rk_list)} butir Rencana Kinerja aktif milik pengguna:")
        for i, rk in enumerate(rk_list, 1):
            print(f"  {i}. {rk}")
            
        return rk_list

def generate_activities_for_rk_list(
    rk_list: list[str],
    start_date: str = "2026-04-01",
    end_date: str = "2026-06-30",
    drive_url: str = "",
    activities_per_rk: int = 2,
    custom_templates_file: str = ""
):
    """
    Menyusun kegiatan harian realistis dari daftar Rencana Kinerja dinamis
    dan menyebarkannya ke hari kerja (Senin - Jumat) di rentang tanggal.
    """
    if not rk_list:
        print("[ERROR] Daftar Rencana Kinerja kosong. Gunakan --fetch-rk atau masukkan via --rk.")
        return None

    # Load custom templates jika ada
    custom_templates = {}
    if custom_templates_file and Path(custom_templates_file).exists():
        with open(custom_templates_file, "r", encoding="utf-8") as f:
            custom_templates = json.load(f)

    # Kumpulkan hari kerja (Senin - Jumat)
    cur = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)
    workdays = []
    while cur <= end:
        if cur.weekday() < 5:  # 0-4 = Senin-Jumat
            workdays.append(cur.strftime("%Y-%m-%d"))
        cur += datetime.timedelta(days=1)

    generated = []
    used_dates = set()

    for rk in rk_list:
        topic = clean_rk_topic(rk)
        keyword = get_distinctive_keyword(rk)
        
        # Cek apakah ada custom template yang cocok
        templates = None
        for k, v in custom_templates.items():
            if k.lower() in rk.lower() or k.lower() in topic.lower():
                templates = v
                break
                
        if not templates:
            templates = dynamic_generate_activities_for_topic(topic)

        # Ambil sejumlah kegiatan yang diminta
        selected_templates = templates[:activities_per_rk]
        for keg, cap in selected_templates:
            avail_dates = [d for d in workdays if d not in used_dates]
            if not avail_dates:
                avail_dates = workdays
            chosen_date = random.choice(avail_dates)
            used_dates.add(chosen_date)

            generated.append({
                "tanggal": chosen_date,
                "rencana_kinerja_keyword": keyword,
                "rencana_kinerja_full": rk,
                "kegiatan": keg,
                "progres": 100,
                "capaian": cap,
                "link_dukung": drive_url,
                "masuk_capaian_skp": True
            })

    generated.sort(key=lambda x: x["tanggal"])

    out_file = Path("kegiatan_auto_generated.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(generated, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Berhasil membuat {len(generated)} kegiatan untuk {len(rk_list)} butir Rencana Kinerja!")
    print(f"📁 File disimpan di: {out_file.resolve()}")
    return out_file

def main():
    parser = argparse.ArgumentParser(description="Generator Kegiatan KIPApp Dinamis dari Rencana Kinerja Pengguna")
    parser.add_argument("--fetch-rk", action="store_true", help="Ambil daftar RK otomatis langsung dari akun KIPApp yang login")
    parser.add_argument("--periode", "-p", default="Triwulan II", help="Periode SKP target (contoh: 'Triwulan I', 'Triwulan 3', 'TW IV', 'Tahunan')")
    parser.add_argument("--tahun", "-t", default="", help="Tahun anggaran/SKP (contoh: 2026)")
    parser.add_argument("--rk", help="Daftar butir RK manual (pisahkan dengan titik koma ';')")
    parser.add_argument("--rk-file", help="Path ke file JSON/TXT daftar RK pengguna")
    parser.add_argument("--start-date", default=None, help="Tanggal awal periode (YYYY-MM-DD, otomatis jika dikosongkan)")
    parser.add_argument("--end-date", default=None, help="Tanggal akhir periode (YYYY-MM-DD, otomatis jika dikosongkan)")
    parser.add_argument("--drive-url", "-d", default="", help="Default URL Google Drive bukti dukung")
    parser.add_argument("--count", "-c", type=int, default=2, help="Jumlah kegiatan per butir RK (default: 2)")
    parser.add_argument("--templates", help="Path ke file JSON custom templates (opsional)")
    parser.add_argument("--browser-data", default="", help="Lokasi kustom direktori browser_data (opsional)")

    args = parser.parse_args()

    # Hitung normalisasi periode dan tanggal default
    norm_periode, def_start, def_end = get_period_dates(args.periode, args.tahun)
    start_date = args.start_date if args.start_date else def_start
    end_date = args.end_date if args.end_date else def_end

    print(f"Periode Terpilih: {norm_periode} ({start_date} s.d {end_date})")

    rk_list = []
    if args.fetch_rk:
        rk_list = fetch_user_rencana_kinerja(norm_periode, tahun=args.tahun, browser_data=args.browser_data)
    elif args.rk:
        rk_list = [item.strip() for item in args.rk.split(";") if item.strip()]
    elif args.rk_file and Path(args.rk_file).exists():
        with open(args.rk_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                rk_list = data
            elif isinstance(data, dict):
                rk_list = list(data.values())
    else:
        # Default: Coba fetch otomatis dari KIPApp pengguna aktif
        print("Tidak ada input RK yang diberikan. Mencoba mengambil otomatis dari akun KIPApp...")
        try:
            rk_list = fetch_user_rencana_kinerja(norm_periode, tahun=args.tahun, browser_data=args.browser_data)
        except Exception as e:
            print(f"[ERROR] Gagal mengambil RK dari browser: {e}")
            print("Gunakan opsi --rk \"Rencana 1; Rencana 2\" atau --rk-file <path_file.json>")
            return

    if rk_list:
        generate_activities_for_rk_list(
            rk_list=rk_list,
            start_date=start_date,
            end_date=end_date,
            drive_url=args.drive_url,
            activities_per_rk=args.count,
            custom_templates_file=args.templates or ""
        )

if __name__ == "__main__":
    main()
