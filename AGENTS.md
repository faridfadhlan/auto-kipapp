# AGENTS.md — Panduan Instruksi untuk Semua Agent AI Coding

Dokumen ini merupakan panduan standar untuk setiap Agent AI Coding (**Google Antigravity, Claude Code, Cursor, GitHub Copilot, Windsurf, Cline/Roo Code, OpenHands/Devin**, dll.) dalam mengoperasikan otomasi pengisian kegiatan harian di **KIPApp BPS** (`https://kipapp.bps.go.id`).

---

## 📌 Deskripsi & Tujuan Proyek

Aplikasi otomasi berbasis Playwright untuk mencatat, menyusun, dan menginput capaian kegiatan harian pegawai ke dalam portal KIPApp BPS secara cepat, akurat, dan tanpa biaya API LLM tambahan.

---

## 📍 Prinsip Ruang Kerja (Workspace Agnostic)

- **Direktori Proyek Dinamis**: Agent **HARUS** bekerja di dalam direktori kerja aktif pengguna saat ini (`current working directory` / workspace root).
- **Jangan Mengasumsikan Nama Folder Tertentu**: Pengguna dapat menjalankan otomasi ini di dalam folder proyek mana pun.
- **File Input & Output**:
  - File data kegiatan (`.xlsx`, `.csv`, `.json`) dibaca langsung dari folder proyek pengguna.
  - File hasil generasi (`kegiatan_auto_generated.json`, preview screenshot) disimpan langsung di folder proyek pengguna.

---

## 🛡️ Kebijakan Privasi & Keamanan (Kredensial)

> [!CAUTION]
> **DILARANG KERAS** melakukan commit, log publik, atau mengekspos:
> 1. Folder `browser_data/` (berisi token JWT Bearer, SSO cookies, profil Chromium).
> 2. File kredensial (`.env`, token, password).
> 3. Tangkapan layar (`*.png`) atau file dump (`*.json`) yang memuat NIP, nama lengkap, atau foto profil pegawai.
> Pastikan file-file ini selalu masuk dalam `.gitignore`.

---

## 🎯 Rencana Kinerja (SKP) Bersifat Dinamis

- **Setiap pegawai BPS memiliki Rencana Kinerja (SKP) yang berbeda** sesuai fungsi/tim (Statistik Sosial, Distribusi, Produksi, Neraca Wilayah, IPDS, Bagian Umum/TU, Fungsional Statistisi/Pranata Komputer, dll.).
- **JANGAN PERNAH** mengasumsikan butir SKP bersifat tetap/statis.
- **Cara Menangani SKP Pengguna**:
  1. **Otomatis (`--fetch-rk`)**: Jalankan skrip untuk menarik seluruh butir SKP aktif langsung dari akun KIPApp pengguna:
     ```bash
     uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "<PERIODE>"
     ```
  2. **Manual/File**: Terima butir SKP dari chat atau file pengguna via `--rk "Butir 1; Butir 2"` atau `--rk-file <FILE.json>`.
  3. **Penyusunan Berbasis AI**: Agent dapat merancang tahapan kegiatan kerja harian ASN (Persiapan, Pelaksanaan, Verifikasi, Pelaporan) yang kontekstual dan realistis berdasarkan kalimat SKP pengguna.

---

## 📅 Fleksibilitas Triwulan & Tahun

Agent otomatis mendeteksi periode triwulan dan tahun dari permintaan pengguna:
- **Triwulan I**: 1 Januari s.d 31 Maret (`--periode "Triwulan I"`)
- **Triwulan II**: 1 April s.d 30 Juni (`--periode "Triwulan II"`)
- **Triwulan III**: 1 Juli s.d 30 September (`--periode "Triwulan III"`)
- **Triwulan IV**: 1 Oktober s.d 31 Desember (`--periode "Triwulan IV"`)
- **Tahunan**: 1 Januari s.d 31 Desember (`--periode "Tahunan"`)
- Parameter `--tahun` (misal `--tahun 2026`) untuk menyesuaikan tahun anggaran.
- Tanggal kegiatan disebarkan hanya pada **hari kerja efektif (Senin – Jumat)**.

---

## 🛠️ Perintah Eksekusi Utama

Agent dapat menggunakan runner `uv run python` atau `python3`:

### 1. Inisialisasi Sesi Login (Jika Belum Login / Sesi Habis)
```bash
uv run python launch_login.py
```
*(Profil tersimpan di `browser_data/` atau terpusat di `~/.kipapp/browser_data/`).*

### 2. Auto-Generate Kegiatan Dinamis dari SKP
```bash
# Otomatis fetch dari KIPApp sesuai periode triwulan
uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "Triwulan II" --tahun 2026

# Atau dengan butir SKP spesifik dari pengguna
uv run python generate_kegiatan_from_rk.py --rk "Nama Butir SKP 1; Nama Butir SKP 2" --periode "Triwulan II"
```

### 3. Input Kegiatan ke Form KIPApp (Excel / CSV / JSON)
```bash
# Mode Preview / Dry-Run (Tanpa Klik Save)
uv run python auto_input_kegiatan.py --file daftar_kegiatan.xlsx --periode "Triwulan II" --dry-run

# Mode Eksekusi Nyata (Live Save)
uv run python auto_input_kegiatan.py --file daftar_kegiatan.xlsx --periode "Triwulan II" --drive-url "https://drive.google.com/..."
```

---

## 📋 Format Kolom Data Kegiatan (Excel/CSV/JSON)

- `tanggal`: Tanggal kegiatan tunggal (`YYYY-MM-DD`) atau rentang (`YYYY-MM-DD - YYYY-MM-DD`).
- `rencana_kinerja_keyword`: Kata kunci pembeda butir SKP pengguna (dicocokkan pada dropdown form KIPApp).
- `kegiatan`: Deskripsi aktivitas kerja yang dilaksanakan.
- `progres`: Angka persentase (default: 100).
- `capaian`: Output hasil kegiatan (opsional, disamakan dengan kegiatan jika kosong).
- `link_dukung`: Tautan bukti dukung bebas (URL web/drive) ATAU path file lokal (misal: `laporan.pdf`, `foto.jpg`). Jika berupa file lokal, sistem otomatis menguploadnya ke Google Drive dan menyisipkan link publiknya.
- `masuk_capaian_skp`: Boolean (`true`/`false`).

---

## ☁️ Integrasi Google Drive (Upload File Bukti Dukung)

- **Upload Otomatis**: Jika pengguna memberikan file fisik lokal sebagai bukti dukung, `gdrive_uploader.py` otomatis menguploadnya ke Google Drive via Google Drive API dan mengembalikan link publik (`webViewLink`).
- **Kredensial Google API**:
  - Letakkan `service_account.json` (Google Cloud Service Account) atau `credentials.json` (OAuth Client ID) di folder proyek atau di `~/.kipapp/`.
  - Dapat juga diset via `.env` (lihat `.env.example`).
  - Target folder ID dapat diset via `--gdrive-folder-id "<ID_FOLDER>"` atau `GDRIVE_FOLDER_ID` di `.env`.

