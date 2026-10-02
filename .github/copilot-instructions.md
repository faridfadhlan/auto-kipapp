# GitHub Copilot Instructions — KIPApp BPS Automation

Panduan instruksi ruang kerja untuk GitHub Copilot dalam menangani proyek otomasi KIPApp BPS.

## Peran & Tanggung Jawab
Membantu pengguna menyusun dan mengotomasi pengisian formulir catatan kegiatan pekerjaan harian di **KIPApp BPS** (`https://kipapp.bps.go.id`).

## Pedoman Penting
1. **Keamanan & Kredensial**:
   - Jangan pernah menyarankan menyimpan atau melakukan commit terhadap kredensial, token JWT Bearer, SSO cookies, NIP pegawai, atau folder `browser_data/`.
2. **Kesesuaian Ruang Kerja**:
   - Selalu gunakan lokasi direktori proyek saat ini (`cwd`).
   - Baca file data kegiatan (`.xlsx`, `.csv`, `.json`, `.txt`, catatan harian) dan simpan file hasil langsung di direktori aktif proyek.
3. **Rencana Kinerja Dinamis & Aturan Pemetaan**:
   - Setiap pegawai BPS memiliki butir Rencana Kinerja (SKP) yang unik sesuai fungsi tugas.
   - Jangan menggunakan daftar SKP statis. Gunakan opsi `--fetch-rk` untuk membaca langsung dari akun KIPApp atau sesuaikan dengan butir SKP yang disediakan pengguna.
4. **Centang Capaian SKP**:
   - Selalu centang opsi *"Masukan ke capaian SKP"* secara default.
5. **Eksekusi Otomatis Langsung**:
   - Jika ada perintah memasukkan / membuatkan / mencatat kegiatan atau sejenisnya, LANGSUNG eksekusi input nyata (live save) ke KIPApp secara default tanpa meminta konfirmasi dry-run lagi.
6. **Fleksibilitas Triwulan**:
   - Kenali otomatis Triwulan I, II, III, IV, Tahunan, serta tahun anggaran dari prompt pengguna.
   - Sebarkan kegiatan ke hari kerja efektif (Senin–Jumat).

## Perintah Kerja
```bash
# Buka login SSO manual jika sesi kedaluwarsa
uv run python launch_login.py

# Auto-generate kegiatan dari SKP pengguna
uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "<PERIODE>"

# Input kegiatan ke KIPApp
uv run python auto_input_kegiatan.py --file <NAMA_FILE> --periode "<PERIODE>" --drive-url "<URL_DRIVE>"
```
