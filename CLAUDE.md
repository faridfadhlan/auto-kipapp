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
- **Rencana Kinerja (SKP)**: Bersifat dinamis per pegawai (Sosial, Distribusi, Produksi, Nerwilis, IPDS, Umum/TU, Fungsional, dll.). Jangan gunakan daftar statis.
- **Triwulan & Tahun**: Tangani triwulan (`Triwulan I`, `Triwulan II`, `Triwulan III`, `Triwulan IV`, `Tahunan`) dan tahun anggaran secara otomatis sesuai prompt pengguna. Tanggal kerja disebarkan ke hari kerja Senin–Jumat.

## Perintah Utama
Jalankan perintah menggunakan `uv run python <script>` atau `python3 <script>`:

```bash
# 1. Login pertama kali / perpanjang sesi
uv run python launch_login.py

# 2. Auto-fetch SKP dan buat kegiatan dinamis
uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "Triwulan II" --tahun 2026

# 3. Buat kegiatan dari SKP manual pengguna
uv run python generate_kegiatan_from_rk.py --rk "Butir SKP 1; Butir SKP 2" --periode "Triwulan II"

# 4. Preview input kegiatan (Dry Run tanpa klik Save)
uv run python auto_input_kegiatan.py --file kegiatan_auto_generated.json --periode "Triwulan II" --dry-run

# 5. Live input kegiatan ke KIPApp
uv run python auto_input_kegiatan.py --file kegiatan_auto_generated.json --periode "Triwulan II" --drive-url "<URL_DRIVE>"
```

## Format Data Kegiatan
Mendukung file Excel (`.xlsx`, `.xls`), CSV (`.csv`), dan JSON (`.json`) dengan kolom:
- `tanggal` (bisa tanggal tunggal `YYYY-MM-DD` atau rentang `YYYY-MM-DD - YYYY-MM-DD`)
- `rencana_kinerja_keyword` (kata kunci pembeda butir SKP pengguna)
- `kegiatan` (deskripsi pekerjaan)
- `progres` (default 100)
- `capaian` (opsional, disamakan dengan kegiatan jika kosong)
- `link_dukung` (opsional: URL bebas atau path file lokal yang otomatis diupload ke Google Drive)
- `masuk_capaian_skp` (boolean, default false)

## Integrasi Google Drive
- Jika bukti dukung berupa file lokal, sistem otomatis menguploadnya ke Google Drive dan menyisipkan link publiknya.
- Kredensial Google: Simpan `service_account.json` (Service Account) atau `credentials.json` (OAuth) di folder proyek atau `~/.kipapp/`, atau konfigurasikan file `.env`.
