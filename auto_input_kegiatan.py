import json
import time
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

def load_activities(file_path: Path):
    ext = file_path.suffix.lower()
    if ext == ".json":
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif ext in [".xlsx", ".xls", ".csv"]:
        import pandas as pd
        if ext == ".csv":
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Standardize column names
        col_map = {}
        for col in df.columns:
            c_clean = str(col).strip().lower()
            if any(k in c_clean for k in ["tanggal", "tgl", "date"]):
                col_map[col] = "tanggal"
            elif any(k in c_clean for k in ["rencana", "skp", "rk"]):
                col_map[col] = "rencana_kinerja_keyword"
            elif any(k in c_clean for k in ["kegiatan", "aktivitas", "deskripsi"]):
                col_map[col] = "kegiatan"
            elif any(k in c_clean for k in ["progres", "progress"]):
                col_map[col] = "progres"
            elif any(k in c_clean for k in ["capaian", "output", "hasil"]):
                col_map[col] = "capaian"
            elif any(k in c_clean for k in ["dukung", "drive", "link", "bukti"]):
                col_map[col] = "link_dukung"
            elif any(k in c_clean for k in ["masuk", "skp"]):
                col_map[col] = "masuk_capaian_skp"

        df = df.rename(columns=col_map)
        
        # Format dates
        if "tanggal" in df.columns:
            df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.strftime("%Y-%m-%d")

        records = df.to_dict(orient="records")
        # Fill missing values
        clean_records = []
        for r in records:
            clean_records.append({
                "tanggal": str(r.get("tanggal", "")).strip(),
                "rencana_kinerja_keyword": str(r.get("rencana_kinerja_keyword", "")).strip() if pd.notna(r.get("rencana_kinerja_keyword")) else "",
                "kegiatan": str(r.get("kegiatan", "")).strip() if pd.notna(r.get("kegiatan")) else "",
                "progres": int(r.get("progres", 100)) if pd.notna(r.get("progres")) else 100,
                "capaian": str(r.get("capaian", "")).strip() if pd.notna(r.get("capaian")) else str(r.get("kegiatan", "")).strip(),
                "link_dukung": str(r.get("link_dukung", "")).strip() if pd.notna(r.get("link_dukung")) else "",
                "masuk_capaian_skp": bool(r.get("masuk_capaian_skp", False)) if pd.notna(r.get("masuk_capaian_skp")) else False,
            })
        return clean_records
    else:
        raise ValueError(f"Format file '{ext}' tidak didukung. Gunakan .json, .csv, atau .xlsx")

import re

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

def input_kegiatan(file_path: str, periode_keyword: str = "Triwulan II", tahun: str = "", default_drive_url: str = "", gdrive_folder_id: str = "", browser_data: str = "", dry_run: bool = False):
    activities_file = Path(file_path)
    if not activities_file.exists():
        print(f"[ERROR] File kegiatan {file_path} tidak ditemukan!")
        return

    try:
        activities = load_activities(activities_file)
    except Exception as e:
        print(f"[ERROR] Gagal membaca file kegiatan: {e}")
        return

    if not activities:
        print("[WARNING] Tidak ada data kegiatan untuk diinput.")
        return

    norm_periode = normalize_periode(periode_keyword)
    user_data_dir = get_browser_data_dir(browser_data)

    print("=" * 65)
    print(f"Memulai Otomasi Input Kegiatan KIPApp BPS ({len(activities)} kegiatan)")
    print(f"Periode SKP Target: {norm_periode} (Input: {periode_keyword})")
    if tahun:
        print(f"Tahun Anggaran/SKP: {tahun}")
    print(f"Profil Browser: {user_data_dir}")
    if default_drive_url:
        print(f"Default Google Drive Link: {default_drive_url}")
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

        print("\n[1/4] Navigasi ke Pelaksanaan Kinerja...")
        page.goto("https://kipapp.bps.go.id/#/pelaksanaan-aksi", wait_until="networkidle")
        time.sleep(2)

        # Tutup modal notifikasi / tour jika ada
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

        # [2/4] Pilih Periode SKP
        print(f"[2/4] Memilih Periode SKP ({norm_periode})...")
        skp_dropdown = page.locator(".ant-select:has-text('Pilih SKP')").first
        if not skp_dropdown.is_visible():
            skp_dropdown = page.locator(".ant-select").nth(2) # Dropdown ke-3 (Pegawai, Tahun, SKP)
        skp_dropdown.click(force=True)
        time.sleep(1)

        target_opt = page.locator(f".ant-select-dropdown li:has-text('{norm_periode}')").first
        if not target_opt.is_visible():
            # Fallback coba teks aslinya
            target_opt = page.locator(f".ant-select-dropdown li:has-text('{periode_keyword}')").first
            
        if not target_opt.is_visible():
            print(f"[ERROR] Periode SKP '{norm_periode}' (atau '{periode_keyword}') tidak ditemukan di dropdown!")
            context.close()
            return

        target_opt.click(force=True)
        time.sleep(3)
        print("Periode SKP berhasil dipilih.")

        # [3/4] Loop input tiap kegiatan
        success_count = 0
        for i, item in enumerate(activities, 1):
            print(f"\n--- Menginput Kegiatan #{i} [{item.get('tanggal', '-')}] ---")
            print(f"  Kegiatan: {item.get('kegiatan')[:60]}...")
            print(f"  RK Match: {item.get('rencana_kinerja_keyword')}")

            # Klik tombol + Add
            add_btn = page.locator("button:has-text('+ Add'), button:has-text('Add')").first
            add_btn.click()
            time.sleep(2)

            modal = page.locator(".ant-modal-content")

            # 1. Pilih Rencana Kinerja
            rk_keyword = item.get("rencana_kinerja_keyword", "")
            if rk_keyword:
                modal.locator(".ant-select:has-text('Pilih rencana kinerja SKP')").first.click()
                time.sleep(1.2)
                rk_opt = page.locator(f".ant-select-dropdown:not(.ant-select-dropdown-hidden) li:has-text('{rk_keyword}')").first
                if rk_opt.is_visible():
                    rk_opt.click(force=True)
                else:
                    page.locator(f".ant-select-dropdown li:has-text('{rk_keyword}')").last.click(force=True)
                time.sleep(1)

            # 2. Input Tanggal (Single atau Range)
            tanggal_str = str(item.get("tanggal", "")).strip()
            tanggal_selesai = str(item.get("tanggal_selesai", "")).strip()

            # Deteksi otomatis rentang tanggal jika ada pemisah ' - ' atau ' s.d '
            if not tanggal_selesai:
                if " - " in tanggal_str:
                    parts = tanggal_str.split(" - ")
                    tanggal_str = parts[0].strip()
                    tanggal_selesai = parts[1].strip()
                elif " s.d " in tanggal_str:
                    parts = tanggal_str.split(" s.d ")
                    tanggal_str = parts[0].strip()
                    tanggal_selesai = parts[1].strip()

            chk_periode = modal.locator("label:has-text('Gunakan periode tanggal') input[type='checkbox']")

            if tanggal_selesai:
                print(f"  Mode Rentang Tanggal: {tanggal_str} s.d {tanggal_selesai}")
                if not chk_periode.is_checked():
                    chk_periode.check()
                    time.sleep(0.8)

                modal.locator(".ant-calendar-picker").first.click()
                time.sleep(1)
                cal_inputs = page.locator(".ant-calendar-range input.ant-calendar-input, .ant-calendar-input")
                if cal_inputs.count() >= 2:
                    cal_inputs.nth(0).fill(tanggal_str)
                    cal_inputs.nth(0).press("Enter")
                    time.sleep(0.4)
                    cal_inputs.nth(1).fill(tanggal_selesai)
                    cal_inputs.nth(1).press("Enter")
                    time.sleep(0.6)
                # Tutup popup kalender jika masih terbuka
                modal.locator(".ant-modal-title").click(force=True)
                time.sleep(0.5)
            else:
                if chk_periode.is_checked():
                    chk_periode.uncheck()
                    time.sleep(0.5)

                if tanggal_str:
                    modal.locator(".ant-calendar-picker").first.click()
                    time.sleep(0.8)
                    cal_input = page.locator(".ant-calendar-input").first
                    if cal_input.is_visible():
                        cal_input.fill(tanggal_str)
                        cal_input.press("Enter")
                        time.sleep(0.8)

            # 3. Input Kegiatan
            kegiatan_text = item.get("kegiatan", "")
            modal.locator("textarea[placeholder*='Kegiatan']").first.fill(kegiatan_text)
            time.sleep(0.3)

            # 4. Input Progres
            progres_val = str(item.get("progres", 100))
            progres_inp = modal.locator("input[placeholder*='Progres']").first
            progres_inp.fill(progres_val)
            time.sleep(0.3)

            # 5. Input Capaian
            capaian_text = item.get("capaian", kegiatan_text)
            modal.locator("textarea[placeholder*='Capaian']").first.fill(capaian_text)
            time.sleep(0.3)

            # 6. Input Data Dukung (bebas: link drive/web atau file lokal yang otomatis diupload)
            raw_dukung = item.get("link_dukung", "").strip() or default_drive_url.strip()
            link_dukung = ""
            if raw_dukung:
                if raw_dukung.startswith("http://") or raw_dukung.startswith("https://"):
                    link_dukung = raw_dukung
                else:
                    # Input berupa file lokal -> upload ke Google Drive
                    try:
                        from gdrive_uploader import upload_file_to_drive
                        link_dukung = upload_file_to_drive(raw_dukung, folder_id=gdrive_folder_id)
                    except Exception as upload_err:
                        print(f"  [WARNING] Gagal mengupload file bukti dukung ke Google Drive: {upload_err}")
                        link_dukung = raw_dukung

            if link_dukung:
                print(f"  Bukti Dukung: {link_dukung}")
                modal.locator("input[placeholder*='Data Dukung']").first.fill(link_dukung)
                time.sleep(0.3)

            # 7. Checkbox Masukan ke Capaian SKP
            if item.get("masuk_capaian_skp", False):
                chk = modal.locator("label:has-text('Masukan ke capaian SKP') input[type='checkbox']")
                if not chk.is_checked():
                    chk.check()
                    time.sleep(0.3)

            # Preview Screenshot
            page.screenshot(path=f"preview_kegiatan_{i}.png")

            # 8. Simpan atau Cancel (jika Dry Run)
            if dry_run:
                print(f"  [DRY-RUN] Preview tersimpan di preview_kegiatan_{i}.png. Membatalkan (Cancel)...")
                modal.locator("button:has-text('Cancel')").first.click()
                time.sleep(1.5)
            else:
                print("  Menyimpan kegiatan (Klik Save)...")
                modal.locator("button:has-text('Save')").first.click()
                time.sleep(3)
                page.screenshot(path="kegiatan_saved.png")
                print(f"  Kegiatan #{i} berhasil disimpan! Bukti simpan: kegiatan_saved.png")
                success_count += 1

        print("\n" + "=" * 65)
        if dry_run:
            print(f"Dry run selesai. Semua {len(activities)} form berhasil diuji tanpa perubahan data.")
        else:
            print(f"Selesai! {success_count} dari {len(activities)} kegiatan berhasil diinput ke KIPApp.")
        print("=" * 65)

        time.sleep(3)
        context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Otomasi Input Kegiatan KIPApp BPS")
    parser.add_argument("--file", "-f", default="daftar_kegiatan_template.json", help="Path ke file JSON kegiatan")
    parser.add_argument("--periode", "-p", default="Triwulan II", help="Kata kunci periode SKP (default: Triwulan II, contoh: 'Triwulan I', 'Triwulan 3', 'TW IV')")
    parser.add_argument("--tahun", "-t", default="", help="Tahun anggaran/SKP (contoh: 2026)")
    parser.add_argument("--drive-url", "-d", default="", help="Default link Google Drive jika per-kegiatan tidak diisi")
    parser.add_argument("--gdrive-folder-id", default="", help="ID Folder Google Drive tujuan jika bukti dukung berupa file lokal")
    parser.add_argument("--browser-data", default="", help="Lokasi kustom direktori browser_data (opsional)")
    parser.add_argument("--dry-run", action="store_true", help="Uji coba pengisian form tanpa mengklik Save")
    args = parser.parse_args()

    input_kegiatan(args.file, args.periode, tahun=args.tahun, default_drive_url=args.drive_url, gdrive_folder_id=args.gdrive_folder_id, browser_data=args.browser_data, dry_run=args.dry_run)
