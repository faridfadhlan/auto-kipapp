# AGENTS.md — Panduan Instruksi untuk Semua Agent AI Coding

Dokumen ini merupakan panduan standar untuk setiap Agent AI Coding (**Google Antigravity, Claude Code, Cursor, GitHub Copilot, Windsurf, Cline, Roo Code, Kilo Code, OpenCode, OpenHands, Zed / Z-Code, Devin**, dll.) dalam mengoperasikan otomasi pengisian kegiatan harian di **KIPApp BPS** (`https://kipapp.bps.go.id`).

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

### ⚠️ Aturan Penting Pemetaan Semantik Butir SKP:
- **Entri Dokumen, Tabulasi, Export, Backup Data**:
  Semua kegiatan yang berkaitan dengan **entri data/dokumen**, **tabulasi**, **ekspor/impor data**, atau **backup data**, **HARUS** dipetakan ke butir Rencana Kinerja (SKP) yang berkaitan dengan **pengolahan** (misal: *"Terlaksanakannya kegiatan pengolahan yang berkualitas dan tepat waktu"*, keyword: `pengolahan`), **BUKAN** ke butir survei lapangan, distribusi, atau tim lainnya.
- **Publikasi**:
  Kegiatan pemeriksaan tabel, naskah rilis, atau penyusunan buku publikasi dipetakan ke butir yang memuat kata kunci **publikasi**.
- **Centang Capaian SKP (Wajib Selalu Checked)**:
  Formulir input kegiatan di portal KIPApp memuat opsi checkbox *"Masukan ke capaian SKP"*. Opsi ini **HARUS SELALU DICENTANG (CHECKED)** secara default pada setiap kegiatan yang disimpan atau digenerate, kecuali jika pengguna secara spesifik meminta sebaliknya.

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
- `masuk_capaian_skp`: Boolean (`true`/`false`, **default: `true`**). Harus selalu bernilai `true` agar kegiatan otomatis terhitung ke dalam capaian realisasi SKP.

---

## ☁️ Integrasi Google Drive (Upload File Bukti Dukung)

- **Upload Otomatis**: Jika pengguna memberikan file fisik lokal sebagai bukti dukung, `gdrive_uploader.py` otomatis menguploadnya ke Google Drive via Google Drive API dan mengembalikan link publik (`webViewLink`).
- **Kredensial Google API**:
  - Letakkan `service_account.json` (Google Cloud Service Account) atau `credentials.json` (OAuth Client ID) di folder proyek atau di `~/.kipapp/`.
  - Dapat juga diset via `.env` (lihat `.env.example`).
  - Target folder ID dapat diset via `--gdrive-folder-id "<ID_FOLDER>"` atau `GDRIVE_FOLDER_ID` di `.env`.

---

## 💬 Pola Permintaan Pengguna & Respon Agent (Semua Agent Coding)

Setiap agent coding (Claude, Cursor, Copilot, Windsurf, Cline, Roo Code, Kilo Code, OpenCode, OpenHands, Zed, Antigravity, dll.) harus merespon prompt pengguna dengan alur kerja berikut:

### Skenario 1: Permintaan Auto-Generate dari SKP
- **Prompt Contoh**: *"Buatkan kegiatan SKP Triwulan II 2026 dari akun KIPApp saya"*
- **Tindakan Agent**:
  1. Jalankan `uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "Triwulan II" --tahun 2026`.
  2. Laporkan daftar kegiatan yang berhasil digenerate kepada pengguna.
  3. Tanyakan atau tawarkan apakah ingin langsung diinputkan ke KIPApp.

### Skenario 2: Permintaan Input dari File (Excel/CSV/JSON)
- **Prompt Contoh**: *"Inputkan file kegiatan_juni.xlsx ke KIPApp Triwulan II, link bukti dukung https://drive.google.com/..."*
- **Tindakan Agent**:
  1. Jalankan `uv run python auto_input_kegiatan.py --file kegiatan_juni.xlsx --periode "Triwulan II" --drive-url "<URL>"`.
  2. Laporkan status jumlah kegiatan yang berhasil disimpan.

### Skenario 3: Input dengan File Bukti Dukung Lokal
- **Prompt Contoh**: *"Inputkan data dari capaian.csv. File bukti dukung ada di folder dokumen/ (upload ke Google Drive saya)"*
- **Tindakan Agent**:
  1. Jalankan `auto_input_kegiatan.py` dengan file tersebut.
  2. Sistem otomatis mengupload file fisik lokal ke Google Drive dan menyisipkan tautan publiknya ke formulir.

### Skenario 4: Simulasi / Preview (Dry Run)
- **Prompt Contoh**: *"Coba test input dulu tanpa simpan (preview)"*
- **Tindakan Agent**:
  1. Tambahkan flag `--dry-run` pada perintah eksekusi.
  2. Beritahukan kepada pengguna lokasi file screenshot preview (`preview_kegiatan_*.png`).

### Skenario 5: Permintaan Pencatatan Kegiatan Langsung dari Chat
- **Prompt Contoh**: *"Catat kegiatan tanggal 29 Juni 2026: Evaluasi pendataan SE2026 untuk SKP pengolahan"*
- **Tindakan Agent**:
  1. Buat file JSON sementara berisi kegiatan tersebut.
  2. Jalankan `auto_input_kegiatan.py` dengan file JSON tersebut.

### Skenario 6: Mengambil Referensi dari File Bebas (.txt, .md, Log Kerja, Catatan Harian)
- **Prompt Contoh**: *"Saya punya catatan tugas di file catatan_mingguan.txt. Tolong baca dan cocokkan dengan butir SKP akun KIPApp saya untuk Triwulan II, lalu inputkan ke KIPApp."*
- **Tindakan Agent**:
  1. Baca file referensi pengguna (`.txt`, `.csv`, `.xlsx`, `.md`, dll.) menggunakan tool pembaca file.
  2. Ambil butir SKP aktif pengguna di KIPApp via `uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "<PERIODE>"`.
  3. Lakukan pencocokan semantik (semantic matching) antara deskripsi kegiatan pengguna di file dengan butir SKP yang paling sesuai.
  4. Susun daftar kegiatan lengkap (tanggal, keyword SKP, kegiatan, capaian, progres) ke file JSON.
  5. Eksekusi `uv run python auto_input_kegiatan.py --file <file_json> --periode "<PERIODE>"`.
  6. Laporkan kegiatan yang berhasil diinput kepada pengguna dan bersihkan file JSON sementara jika diperlukan.

### Skenario 7: Mengambil File Referensi dengan Filter / Kriteria Spesifik
- **Prompt Contoh**: *"Dari file rekap.xlsx atau log.txt, ambil hanya kegiatan minggu kedua bulan Juni dan inputkan ke KIPApp."*
- **Tindakan Agent**:
  1. Baca file yang dimaksud dan filter baris kegiatan sesuai rentang tanggal atau kriteria yang diminta pengguna.
  2. Petakan ke butir SKP KIPApp.
  3. Inputkan ke KIPApp menggunakan `auto_input_kegiatan.py`.

### Skenario 8: Edit / Pembaruan Massal Butir Realisasi (Update Bukti Dukung ke Google Drive)
- **Prompt Contoh**: *"Tolong tambahkan semua bukti dukung di Triwulan II ke URL folder Google Drive: https://drive.google.com/..."*
- **Tindakan Agent**:
  1. Jalankan `edit_kegiatan.py` dengan parameter periode dan URL Google Drive yang diminta:
     ```bash
     uv run python edit_kegiatan.py --periode "<PERIODE>" --drive-url "<URL_DRIVE>" --all
     ```
  2. Jika pengguna meminta hanya kegiatan yang belum punya bukti: tambahkan flag `--only-empty-bukti`.
  3. Laporkan jumlah kegiatan yang berhasil diperbarui kepada pengguna.


