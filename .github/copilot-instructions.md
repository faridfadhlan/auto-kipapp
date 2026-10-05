# GitHub Copilot Instructions — KIPApp BPS Automation

Panduan instruksi ruang kerja untuk GitHub Copilot dalam menangani proyek otomasi KIPApp BPS.

## Peran & Tanggung Jawab
Membantu pengguna menyusun dan mengotomasi pengisian formulir catatan kegiatan pekerjaan harian di **KIPApp BPS** (`https://kipapp.bps.go.id`).

## Mode Operasional
- **Mode Penggunaan (Default)**:
  - Operasional harian: input kegiatan, generate SKP, cek data.
  - 🚫 **DILARANG MENGUBAH SOURCE CODE APAPUN** (`*.py`, file proyek).
  - 📁 **Simpan File JSON di Folder Periode**: Simpan semua hasil file kegiatan JSON di `kegiatan/<Periode>/` (contoh: `kegiatan/Triwulan III/kegiatan_auto_generated.json`), BUKAN di root workspace.
  - ⚡ **Live Save Default**: Langsung eksekusi penyimpanan nyata ke KIPApp tanpa konfirmasi dry-run.
- **Mode Development**:
  - HANYA aktif jika diminta eksplisit pengembangan/perbaikan kode ("mode dev", "tambah fitur", "fix bug"). Diperbolehkan mengubah source code.

## Pedoman Penting
1. **Keamanan & Kredensial**:
   - Jangan pernah menyarankan menyimpan atau melakukan commit terhadap kredensial, token JWT Bearer, SSO cookies, NIP pegawai, atau folder `browser_data/`.
2. **Kesesuaian Ruang Kerja**:
   - Selalu gunakan lokasi direktori proyek saat ini (`cwd`).
   - Baca file data kegiatan (`.xlsx`, `.csv`, `.json`, `.txt`, catatan harian) dan simpan file hasil JSON di folder periode `kegiatan/<Periode>/`.
3. **Rencana Kinerja Dinamis & Aturan Pemetaan**:
   - Setiap pegawai BPS memiliki butir Rencana Kinerja (SKP) yang unik sesuai fungsi tugas.
   - Jangan menggunakan daftar SKP statis. Gunakan opsi `--fetch-rk` untuk membaca langsung dari akun KIPApp atau sesuaikan dengan butir SKP yang disediakan pengguna. Khusus entri dokumen/data, tabulasi, export, dan backup wajib dipetakan ke butir **pengolahan**.
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

# Auto-generate kegiatan dari SKP pengguna (otomatis disimpan di kegiatan/<Periode>/)
uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "<PERIODE>"

# Input kegiatan ke KIPApp via REST API (otomatis membaca dari kegiatan/<Periode>/)
uv run python auto_input_kegiatan.py --periode "<PERIODE>" --drive-url "<URL_DRIVE>"

# Input dengan file spesifik
uv run python auto_input_kegiatan.py --file "kegiatan/<PERIODE>/kegiatan_auto_generated.json" --periode "<PERIODE>"
```
