import json
import time
import random
import datetime
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

USER_DATA_DIR = Path(__file__).parent / "browser_data"

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

def fetch_user_rencana_kinerja(periode_keyword: str = "Triwulan II") -> list[str]:
    """
    Membuka KIPApp secara otomatis via persistent browser session
    dan membaca seluruh opsi butir Rencana Kinerja (SKP) pengguna yang aktif.
    """
    print(f"\n[1/2] Menghubungkan ke KIPApp untuk membaca Rencana Kinerja ({periode_keyword})...")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(USER_DATA_DIR),
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://kipapp.bps.go.id/#/pelaksanaan-aksi", wait_until="networkidle")
        time.sleep(2)
        page.evaluate("() => document.querySelectorAll('.ant-modal-wrap, .ant-modal-mask').forEach(e => e.remove())")
        
        # Pilih Periode SKP
        skp_dropdown = page.locator(".ant-select").nth(2)
        skp_dropdown.click(force=True)
        time.sleep(1)
        target = page.locator(f".ant-select-dropdown li:has-text('{periode_keyword}')").first
        if target.is_visible():
            target.click(force=True)
            time.sleep(2)
        else:
            print(f"[WARNING] Periode '{periode_keyword}' tidak ditemukan di dropdown.")
            
        # Buka modal Add
        add_btn = page.locator("button:has-text('+ Add'), button:has-text('Add')").first
        add_btn.click()
        time.sleep(1.5)
        
        modal = page.locator(".ant-modal-content")
        modal.locator(".ant-select:has-text('Pilih rencana kinerja SKP')").first.click(force=True)
        time.sleep(1)
        
        raw_options = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden) li").all_text_contents()
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
                "masuk_capaian_skp": False
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
    parser.add_argument("--periode", "-p", default="Triwulan II", help="Periode SKP target (default: Triwulan II)")
    parser.add_argument("--rk", help="Daftar butir RK manual (pisahkan dengan titik koma ';')")
    parser.add_argument("--rk-file", help="Path ke file JSON/TXT daftar RK pengguna")
    parser.add_argument("--start-date", default="2026-04-01", help="Tanggal awal periode (YYYY-MM-DD)")
    parser.add_argument("--end-date", default="2026-06-30", help="Tanggal akhir periode (YYYY-MM-DD)")
    parser.add_argument("--drive-url", "-d", default="", help="Default URL Google Drive bukti dukung")
    parser.add_argument("--count", "-c", type=int, default=2, help="Jumlah kegiatan per butir RK (default: 2)")
    parser.add_argument("--templates", help="Path ke file JSON custom templates (opsional)")

    args = parser.parse_args()

    rk_list = []
    if args.fetch_rk:
        rk_list = fetch_user_rencana_kinerja(args.periode)
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
            rk_list = fetch_user_rencana_kinerja(args.periode)
        except Exception as e:
            print(f"[ERROR] Gagal mengambil RK dari browser: {e}")
            print("Gunakan opsi --rk \"Rencana 1; Rencana 2\" atau --rk-file <path_file.json>")
            return

    if rk_list:
        generate_activities_for_rk_list(
            rk_list=rk_list,
            start_date=args.start_date,
            end_date=args.end_date,
            drive_url=args.drive_url,
            activities_per_rk=args.count,
            custom_templates_file=args.templates or ""
        )

if __name__ == "__main__":
    main()
