# Auto-KIPApp

Otomasi pencatatan kegiatan harian pegawai ke portal KIPApp BPS (https://kipapp.bps.go.id).

Mendukung eksekusi langsung melalui REST API KIPApp atau otomasi browser (Playwright). Dapat dioperasikan melalui AI Coding Agent (Antigravity, Cursor, Claude Code, GitHub Copilot, dsb.) maupun CLI terminal.

## Fitur

- Input kegiatan langsung via REST API internal KIPApp (eksekusi instan tanpa beban rendering browser).
- Login SSO BPS persisten: sesi tersimpan di lokal, tidak perlu login berulang kali.
- Format input: teks chat langsung, file JSON, Excel (.xlsx), atau CSV.
- Pemetaan otomatis deskripsi kerja ke butir Rencana Kinerja (SKP) pengguna.
- Opsi "Masukan ke capaian SKP" aktif secara default pada setiap input.
- Auto-upload file bukti fisik (PDF/gambar) dari lokal ke Google Drive.
- Pembaruan massal link bukti dukung dan checklist capaian SKP.

## Persiapan

### 1. Instalasi Dependensi

Gunakan `uv` (direkomendasikan) atau `pip`:

```bash
# Menggunakan uv
uv run playwright install chromium

# Atau menggunakan pip
pip install -r requirements.txt
playwright install chromium
```

### 2. Login Awal SSO BPS

Jalankan skrip login satu kali untuk menyimpan sesi SSO ke profil browser:

```bash
uv run python launch_login.py
```

Browser akan terbuka. Lakukan login SSO BPS. Begitu berhasil masuk ke KIPApp, sistem akan mendeteksi login, menyimpan token sesi, dan menutup browser secara otomatis.

## Penggunaan

### A. Lewat Chat AI (Antigravity, Cursor, Claude Code, Copilot)

Buka chat AI di editor dan berikan instruksi langsung:

- **Catat kegiatan harian**:
  > "Catat kegiatan hari ini: Membuat lembar kerja konfirmasi cleaning data SE2026, bukti dukung https://cloud.bpskalbar.id/s/xxxx"

- **Input dari file Excel atau CSV**:
  > "Baca file rekap.xlsx dan inputkan semua kegiatan ke KIPApp Triwulan IV."

- **Input dengan file bukti fisik lokal**:
  > "Catat kegiatan tanggal 4 November 2026: Tabulasi data SE2026. File bukti dukung di bukti_dukung/laporan.pdf."  
  *(File lokal akan diunggah ke Google Drive dan link publiknya dimasukkan ke form KIPApp).*

- **Auto-generate dari butir SKP**:
  > "Buatkan kegiatan untuk Triwulan IV 2026 dari butir SKP saya dan sebarkan ke hari kerja efektif."

- **Update bukti dukung massal**:
  > "Update bukti dukung semua kegiatan di Triwulan IV yang masih kosong ke link https://drive.google.com/drive/folders/xxxx"

- **Cek status kegiatan**:
  > "Tampilkan daftar kegiatan yang sudah tersimpan di Triwulan IV."

### B. Lewat CLI (Terminal)

```bash
# Cek daftar SKP tahun aktif
uv run python kipapp_api.py --list-skp

# Cek daftar kegiatan tersimpan pada periode tertentu
uv run python kipapp_api.py --list-kegiatan --periode "Triwulan IV"

# Input kegiatan dari file (JSON/Excel/CSV)
uv run python auto_input_kegiatan.py --file kegiatan/2026-TW-04/kegiatan.json --periode "Triwulan IV"

# Generate draf kegiatan dari SKP akun
uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "Triwulan IV"

# Update massal tautan bukti dukung
uv run python edit_kegiatan.py --periode "Triwulan IV" --drive-url "<URL_DRIVE>" --all

# Update checklist capaian SKP secara massal
uv run python kipapp_api.py --update-checklists --periode "Triwulan IV"
```

## Konfigurasi Google Drive (Opsional)

Diperlukan hanya jika ingin file lokal otomatis diunggah ke Google Drive sebagai bukti dukung:

1. Buat **OAuth 2.0 Client ID** bertipe **Desktop App** di Google Cloud Console (pastikan Google Drive API aktif).
2. Simpan file kredensial di root proyek dengan nama `credentials.json`.
3. (Opsional) Tentukan ID folder tujuan di `.env`:
   ```ini
   GDRIVE_FOLDER_ID=1jFthCV2kv3_p75wLrjmsMBFVZMH7lor2
   ```
4. Pada proses upload pertama, browser akan meminta konfirmasi izin akses Google akun Anda. Token autentikasi disimpan di `token.json`.

## Struktur Direktori

```text
├── auto_input_kegiatan.py       # Skrip utama input kegiatan (REST API / Browser fallback)
├── kipapp_api.py                # Klien REST API KIPApp
├── edit_kegiatan.py             # Pembaruan massal bukti dukung dan capaian
├── generate_kegiatan_from_rk.py # Generator kegiatan otomatis dari butir SKP
├── launch_login.py              # Inisialisasi login SSO BPS
├── gdrive_uploader.py           # Modul auto-upload bukti dukung ke Google Drive
├── kegiatan/                    # Arsip file JSON kegiatan per periode (YYYY-TW-0X)
├── browser_data/                # Profil browser Chromium & sesi lokal (diabaikan git)
└── AGENTS.md                    # Panduan standar instruksi universal AI agent
```

## Keamanan

File kredensial (`.env`, `credentials.json`, `token.json`, `service_account.json`), folder sesi browser (`browser_data/`), serta file media bukti dukung sudah terdaftar pada `.gitignore` dan tidak akan ter-commit ke repositori.
