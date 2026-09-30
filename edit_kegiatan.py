import time
import argparse
import re
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

def normalize_periode(periode_str: str) -> str:
    """
    Menormalkan format triwulan input (misal: 'TW 1', 'triwulan 3')
    menjadi format standar KIPApp ('Triwulan I', 'Triwulan III', dst.)
    """
    p = str(periode_str).strip().lower()
    if re.search(r'\b(tw|triwulan)?\s*(iv|4)\b', p):
        return "Triwulan IV"
    elif re.search(r'\b(tw|triwulan)?\s*(iii|3)\b', p):
        return "Triwulan III"
    elif re.search(r'\b(tw|triwulan)?\s*(ii|2)\b', p):
        return "Triwulan II"
    elif re.search(r'\b(tw|triwulan)?\s*(i|1)\b', p):
        return "Triwulan I"
    elif "tahunan" in p:
        return "Tahunan"
    return periode_str

def edit_kegiatan(
    periode_keyword: str = "Triwulan II",
    tahun: str = "",
    drive_url: str = "",
    update_all: bool = False,
    only_empty_bukti: bool = False,
    keyword_filter: str = "",
    date_filter: str = "",
    new_progres: str = "",
    new_capaian: str = "",
    new_masuk_skp: str = "",
    browser_data: str = "",
    dry_run: bool = False
):
    norm_periode = normalize_periode(periode_keyword)
    user_data_dir = get_browser_data_dir(browser_data)

    print("=" * 65)
    print("Memulai Otomasi Edit / Pembaruan Realisasi Kegiatan KIPApp BPS")
    print(f"Periode SKP Target: {norm_periode} (Input: {periode_keyword})")
    if tahun:
        print(f"Tahun: {tahun}")
    if drive_url:
        print(f"Target URL Bukti Dukung: {drive_url}")
    if only_empty_bukti:
        print("Filter: HANYA kegiatan yang belum memiliki bukti dukung")
    elif update_all:
        print("Filter: SEMUA kegiatan pada periode ini")
    if keyword_filter:
        print(f"Filter Kata Kunci: '{keyword_filter}'")
    if date_filter:
        print(f"Filter Tanggal: '{date_filter}'")
    print(f"Mode: {'DRY RUN (Preview Tanpa Save)' if dry_run else 'LIVE (Simpan ke KIPApp)'}")
    print("=" * 65)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            viewport={"width": 1400, "height": 900},
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else context.new_page()

        print("\n[1/3] Navigasi ke Pelaksanaan Kinerja...")
        page.goto("https://kipapp.bps.go.id/#/pelaksanaan-aksi", wait_until="networkidle")
        time.sleep(2)

        # Cek apakah butuh login
        is_logged_in = False
        for _ in range(4):
            if page.locator(".ant-menu, a[href*='pelaksanaan-aksi'], button:has-text('Tambah')").count() > 0 and "login" not in page.url.lower():
                is_logged_in = True
                break
            time.sleep(1)

        if not is_logged_in or "login" in page.url.lower() or "sso" in page.url.lower() or page.locator("button:has-text('Login'), input[type='password']").count() > 0:
            print("\n" + "=" * 65)
            print(">>> ANDA BELUM LOGIN ATAU SESI KIPAPP TELAH BERAKHIR <<<")
            print("Silakan lakukan login SSO BPS pada jendela browser yang terbuka.")
            print("Sistem akan otomatis melanjutkan pengisian setelah Anda berhasil masuk...")
            print("=" * 65 + "\n")
            try:
                page.wait_for_selector(".ant-menu, a[href*='pelaksanaan-aksi'], button:has-text('Tambah Kegiatan')", timeout=300000)
                time.sleep(3)
                if "#/pelaksanaan-aksi" not in page.url:
                    page.goto("https://kipapp.bps.go.id/#/pelaksanaan-aksi", wait_until="networkidle")
                    time.sleep(2)
                print("Login berhasil terdeteksi! Melanjutkan proses otomasi...")
            except Exception as login_err:
                print(f"[ERROR] Batas waktu login (5 menit) terlampaui: {login_err}")
                context.close()
                return

        # Tutup modal notifikasi / tour
        page.evaluate("() => document.querySelectorAll('.ant-modal-wrap, .ant-modal-mask').forEach(e => e.remove())")
        time.sleep(1)

        # Pilih Tahun jika ditentukan
        if tahun:
            print(f"Memilih Tahun: {tahun}...")
            tahun_dropdown = page.locator(".ant-select").nth(1)
            tahun_dropdown.click(force=True)
            time.sleep(0.8)
            opt_tahun = page.locator(f".ant-select-dropdown li:has-text('{tahun}')").first
            if opt_tahun.is_visible():
                opt_tahun.click(force=True)
                time.sleep(1.5)

        # [2/3] Pilih Periode SKP
        print(f"[2/3] Memilih Periode SKP ({norm_periode})...")
        skp_dropdown = page.locator(".ant-select").nth(2)
        skp_dropdown.click(force=True)
        time.sleep(1.2)

        target_opt = page.locator(f".ant-select-dropdown:not(.ant-select-dropdown-hidden) li:has-text('{norm_periode}')").first
        if not target_opt.is_visible():
            target_opt = page.locator(f".ant-select-dropdown:not(.ant-select-dropdown-hidden) li:has-text('{periode_keyword}')").first

        if not target_opt.is_visible():
            print(f"[ERROR] Periode SKP '{norm_periode}' (atau '{periode_keyword}') tidak ditemukan di dropdown!")
            context.close()
            return

        target_opt.click(force=True)
        time.sleep(3)
        print("Periode SKP berhasil dipilih.")

        # Set page size ke 40 agar menampilkan sebanyak mungkin kegiatan dalam 1 halaman
        try:
            size_changer = page.locator(".ant-pagination .ant-select").first
            if size_changer.is_visible():
                size_changer.click(force=True)
                time.sleep(0.8)
                opt40 = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden) li:has-text('40 / page')").first
                if opt40.is_visible():
                    opt40.click(force=True)
                    time.sleep(2)
                    print("Ukuran halaman berhasil diset ke 40 data per halaman.")
        except Exception as e:
            print(f"[NOTE] Menggunakan ukuran halaman standar: {e}")

        # [3/3] Iterasi baris tabel kegiatan
        print("\n[3/3] Membaca dan memperbarui butir kegiatan...")
        total_edited = 0
        total_skipped = 0

        current_page = 1
        while True:
            # Ambil seluruh baris data di tabel saat ini
            rows = page.locator(".ant-table-scroll tbody tr, .ant-table-body tbody tr")
            row_count = rows.count()
            print(f"\nHalaman {current_page}: Ditemukan {row_count} kegiatan di tabel.")

            if row_count == 0:
                print("Tidak ada kegiatan yang ditemukan pada halaman ini.")
                break

            for idx in range(row_count):
                # Query ulang row agar referensi DOM selalu segar
                row = page.locator(".ant-table-scroll tbody tr, .ant-table-body tbody tr").nth(idx)
                row.scroll_into_view_if_needed()
                time.sleep(0.3)

                tds = row.locator("td")
                if tds.count() < 10:
                    continue

                no_str = tds.nth(1).inner_text().strip()
                tgl_str = tds.nth(2).inner_text().strip().replace("\n", " ")
                rk_str = tds.nth(3).inner_text().strip()
                keg_str = tds.nth(4).inner_text().strip()
                bukti_str = tds.nth(7).inner_text().strip()

                has_bukti = ("lihat" in bukti_str.lower()) or (tds.nth(7).locator("button, a").count() > 0)

                # Filter: Only empty bukti
                if only_empty_bukti and has_bukti:
                    total_skipped += 1
                    continue

                # Filter: Keyword
                if keyword_filter:
                    kw = keyword_filter.lower()
                    if kw not in keg_str.lower() and kw not in rk_str.lower():
                        total_skipped += 1
                        continue

                # Filter: Date
                if date_filter:
                    if date_filter not in tgl_str:
                        total_skipped += 1
                        continue

                print(f"\n-> Memproses Kegiatan #{no_str} [{tgl_str}]:")
                print(f"   Kegiatan: {keg_str[:65]}...")
                print(f"   Status Bukti Saat Ini: {'Sudah ada' if has_bukti else 'Belum ada bukti dukung'}")

                # Buka dropdown Aksi
                aksi_btn = row.locator("button:has-text('Aksi')").first
                aksi_btn.scroll_into_view_if_needed()
                aksi_btn.click(force=True)
                time.sleep(0.8)

                # Klik Edit
                edit_item = page.locator(".ant-dropdown:not(.ant-dropdown-hidden) li:has-text('Edit')").first
                if not edit_item.is_visible():
                    print("   [WARNING] Menu Edit tidak muncul, mencoba klik ulang tombol Aksi...")
                    aksi_btn.click(force=True)
                    time.sleep(0.8)
                    edit_item = page.locator(".ant-dropdown:not(.ant-dropdown-hidden) li:has-text('Edit')").first

                if not edit_item.is_visible():
                    print("   [ERROR] Tidak dapat membuka menu Edit. Melanjutkan ke baris berikutnya.")
                    continue

                edit_item.click(force=True)
                time.sleep(1.5)

                modal = page.locator(".ant-modal-content")
                if not modal.is_visible():
                    print("   [ERROR] Modal edit tidak terbuka.")
                    continue

                # Lakukan perubahan nilai
                # 1. Update Link Data Dukung
                if drive_url:
                    dukung_inp = modal.locator("input[placeholder*='Data Dukung']").first
                    dukung_inp.fill(drive_url)
                    print(f"   Set Bukti Dukung -> {drive_url}")

                # 2. Update Progres jika ditentukan
                if new_progres:
                    prog_inp = modal.locator("input[placeholder*='Progres']").first
                    prog_inp.fill(str(new_progres))
                    print(f"   Set Progres -> {new_progres}%")

                # 3. Update Capaian jika ditentukan
                if new_capaian:
                    cap_inp = modal.locator("textarea[placeholder*='Capaian']").first
                    cap_inp.fill(new_capaian)
                    print(f"   Set Capaian -> {new_capaian[:50]}...")

                # 4. Update Masuk Capaian SKP jika ditentukan
                if new_masuk_skp:
                    chk = modal.locator("label:has-text('Masukan ke capaian SKP') input[type='checkbox']")
                    if new_masuk_skp.lower() in ["true", "1", "ya"]:
                        if not chk.is_checked():
                            chk.check()
                    elif new_masuk_skp.lower() in ["false", "0", "tidak"]:
                        if chk.is_checked():
                            chk.uncheck()

                time.sleep(0.5)

                # Simpan atau Cancel
                if dry_run:
                    print(f"   [DRY RUN] Preview perubahan kegiatan #{no_str}. Membatalkan (Cancel)...")
                    modal.locator("button:has-text('Cancel')").first.click()
                    time.sleep(1)
                else:
                    save_btn = modal.locator("button:has-text('Save')").first
                    save_btn.click()
                    time.sleep(2)
                    # Pastikan modal telah tertutup
                    try:
                        modal.wait_for(state="hidden", timeout=10000)
                    except Exception:
                        pass
                    print(f"   ✅ Berhasil memperbarui kegiatan #{no_str}!")
                    total_edited += 1

                time.sleep(1)

            # Cek halaman berikutnya di pagination
            next_btn = page.locator(".ant-pagination-next:not(.ant-pagination-disabled)").first
            if next_btn.is_visible():
                print(f"\nBeralih ke halaman {current_page + 1}...")
                next_btn.click(force=True)
                time.sleep(2.5)
                current_page += 1
            else:
                break

        print("\n" + "=" * 65)
        if dry_run:
            print(f"Dry run selesai. Simulasi memeriksa seluruh kegiatan pada {norm_periode}.")
        else:
            print(f"Selesai! Berhasil memperbarui {total_edited} kegiatan di {norm_periode}.")
            if total_skipped > 0:
                print(f"Dilewati (tidak memenuhi kriteria filter): {total_skipped} kegiatan.")
        print("=" * 65)

        time.sleep(2)
        context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Otomasi Edit / Update Realisasi Kegiatan KIPApp BPS")
    parser.add_argument("--periode", "-p", default="Triwulan II", help="Periode SKP target (default: Triwulan II)")
    parser.add_argument("--tahun", "-t", default="", help="Tahun anggaran/SKP (contoh: 2026)")
    parser.add_argument("--drive-url", "-d", default="", help="URL link bukti dukung Google Drive baru")
    parser.add_argument("--all", action="store_true", help="Update semua kegiatan pada periode ini")
    parser.add_argument("--only-empty-bukti", action="store_true", help="Hanya update kegiatan yang belum memiliki bukti dukung")
    parser.add_argument("--keyword", "-k", default="", help="Filter kegiatan berdasarkan kata kunci kegiatan atau rencana kinerja")
    parser.add_argument("--date", default="", help="Filter tanggal spesifik (contoh: 2026-06-05)")
    parser.add_argument("--progres", default="", help="Nilai persentase progres baru (contoh: 100)")
    parser.add_argument("--capaian", default="", help="Deskripsi capaian baru")
    parser.add_argument("--masuk-skp", default="", help="Set centang Masukan ke Capaian SKP (true/false)")
    parser.add_argument("--browser-data", default="", help="Direktori profil browser kustom")
    parser.add_argument("--dry-run", action="store_true", help="Simulasi tanpa menyimpan perubahan")

    args = parser.parse_args()

    edit_kegiatan(
        periode_keyword=args.periode,
        tahun=args.tahun,
        drive_url=args.drive_url,
        update_all=args.all or (not args.only_empty_bukti and not args.keyword and not args.date),
        only_empty_bukti=args.only_empty_bukti,
        keyword_filter=args.keyword,
        date_filter=args.date,
        new_progres=args.progres,
        new_capaian=args.capaian,
        new_masuk_skp=args.masuk_skp,
        browser_data=args.browser_data,
        dry_run=args.dry_run
    )
