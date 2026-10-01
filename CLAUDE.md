# CLAUDE.md — Panduan untuk Claude Code

Panduan untuk Claude Code saat bekerja pada proyek otomasi pengisian kegiatan harian **KIPApp BPS** (`https://kipapp.bps.go.id`).

## Ringkasan Proyek
Otomasi pengisian catatan kegiatan harian pegawai BPS ke sistem KIPApp menggunakan Playwright persistent browser session tanpa biaya token LLM browser external.

## Aturan Keamanan & Kredensial (Kritis)
- **JANGAN PERNAH** membaca, membuat commit, atau menampilkan konten dari `browser_data/`. Folder ini menyimpan session cookies SSO BPS dan token autentikasi.
- **JANGAN PERNAH** menyertakan NIP pegawai, token Bearer, atau URL folder pribadi ke dalam commit git atau file publik.
- Pastikan semua dump dan file temporary tetap ter-ignore di `.gitignore`.

## Fleksibilitas Proyek
- **Direktori Proyek**: Bekerja selalu di direktori kerja aktif pengguna saat ini (`cwd`). Jangan asumsikan folder harus bernama tertentu.
- **Rencana Kinerja (SKP)**: Bersifat dinamis per pegawai (Sosial, Distribusi, Produksi, Nerwilis, IPDS, Umum/TU, Fungsional, dll.). Jangan gunakan daftar statis. Khusus kegiatan terkait entri dokumen, tabulasi, export, atau backup data, WAJIB dipetakan ke butir Rencana Kinerja terkait **pengolahan**.
- **Triwulan & Tahun**: Tangani triwulan (`Triwulan I`, `Triwulan II`, `Triwulan III`, `Triwulan IV`, `Tahunan`) dan tahun anggaran secara otomatis sesuai prompt pengguna. Tanggal kerja disebarkan ke hari kerja Senin–Jumat.

## Perintah Utama
Jalankan perintah menggunakan `uv run python <script>` atau `python3 <script>` (otomatis berjalan via REST API super cepat):

```bash
# 1. Login pertama kali / perpanjang sesi
uv run python launch_login.py

# 2. Auto-fetch SKP dan buat kegiatan dinamis via REST API (~0.2 detik)
uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "Triwulan II" --tahun 2026

# 3. Buat kegiatan dari SKP manual pengguna
uv run python generate_kegiatan_from_rk.py --rk "Butir SKP 1; Butir SKP 2" --periode "Triwulan II"

# 4. Input kegiatan via REST API super cepat (Default)
uv run python auto_input_kegiatan.py --file kegiatan_auto_generated.json --periode "Triwulan II" --drive-url "<URL_DRIVE>"

# 5. Input kegiatan mode Playwright Browser visual
uv run python auto_input_kegiatan.py --file kegiatan_auto_generated.json --periode "Triwulan II" --browser

# 6. Preview input kegiatan (Dry Run tanpa klik Save)
uv run python auto_input_kegiatan.py --file kegiatan_auto_generated.json --periode "Triwulan II" --dry-run

# 7. Edit / pembaruan massal bukti dukung & capaian
uv run python edit_kegiatan.py --periode "Triwulan II" --drive-url "<URL_DRIVE>" --all

# 8. Utilitas REST API langsung (inspeksi & checklist)
uv run python kipapp_api.py --list-skp
uv run python kipapp_api.py --list-rk --periode "Triwulan II"
uv run python kipapp_api.py --list-kegiatan --periode "Triwulan II"
uv run python kipapp_api.py --update-checklists --periode "Triwulan II"
```

## Format Data Kegiatan
Mendukung file Excel (`.xlsx`, `.xls`), CSV (`.csv`), JSON (`.json`), serta teks/catatan bebas (`.txt`, `.tsv`, `.log`, `.md`) dengan kolom:
- `tanggal` (bisa tanggal tunggal `YYYY-MM-DD` atau rentang `YYYY-MM-DD - YYYY-MM-DD`)
- `rencana_kinerja_keyword` (kata kunci pembeda butir SKP pengguna)
- `kegiatan` (deskripsi pekerjaan)
- `progres` (default 100)
- `capaian` (opsional, disamakan dengan kegiatan jika kosong)
- `link_dukung` (opsional: URL bebas atau path file lokal yang otomatis diupload ke Google Drive)
- `masuk_capaian_skp` (boolean, **default true**)

## Integrasi Google Drive
- Jika bukti dukung berupa file lokal, sistem otomatis menguploadnya ke Google Drive dan menyisipkan link publiknya.
- Kredensial Google: Simpan `service_account.json` (Service Account) atau `credentials.json` (OAuth) di folder proyek atau `~/.kipapp/`, atau konfigurasikan file `.env`.
