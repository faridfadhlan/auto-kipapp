---
name: kipapp
description: Mengotomasi input catatan kegiatan harian di KIPApp BPS (https://kipapp.bps.go.id). Gunakan skill ini setiap kali pengguna meminta untuk menginput, mengecek, auto-generate dari rencana SKP, melengkapi bukti dukung Google Drive, atau submit kegiatan pekerjaan ke KIPApp BPS dari file (Excel/CSV/JSON) maupun teks langsung.
---

# KIPApp BPS Automation Skill

Skill ini memandu agen untuk mengotomasi seluruh siklus pengisian, pelengkapan bukti dukung, pembuatan otomatis dari rencana kinerja, dan pengiriman catatan kegiatan di **KIPApp BPS** (`https://kipapp.bps.go.id`).

---

## 📍 Lingkungan & Lokasi Proyek

- Direktori Proyek: Root direktori `auto-kipapp`
- Interpreter & Tools: `uv` (jalankan perintah via `uv run python <script>`)
- Sesi Browser: Simpan otomatis di `browser_data/` setelah login SSO satu kali

---

## 🚀 Kemampuan & Fitur Utama

### 1. Auto-Generate Kegiatan dari Rencana Kinerja (SKP) yang Ada
Jika pengguna meminta untuk *"mengisi/mengotomatiskan kegiatan dari daftar rencana yang sudah ada"*:
- Agen dapat membaca butir SKP Utama yang terdaftar di KIPApp (misal 8 butir SKP Triwulan II: *Pengolahan*, *Perangkat & Jaringan*, *Pembinaan Statistik Sektoral*, *SBR*, *Kompetensi*, *Monitoring*, *Sistem Informasi*, *Publikasi*).
- Jalankan skrip generator:
  ```bash
  uv run python generate_kegiatan_from_rk.py
  ```
- Skrip akan mendeteksi butir SKP yang masih 0 kegiatan dan menyusunkan daftar kegiatan pekerjaan harian yang realistis, membaginya ke hari kerja (Senin - Jumat) di periode tersebut, dan menyimpannya ke `kegiatan_auto_generated.json`.
- Pengguna dapat me-review atau langsung diinput ke KIPApp.

### 2. Input Kegiatan dari File (Excel, CSV, JSON) atau Teks Chat
- **Excel (`.xlsx` / `.xls`) & CSV**: Kolom otomatis dideteksi (`Tanggal`, `Tanggal Selesai`, `Kegiatan`, `Rencana Kinerja`, `Capaian`, `Progres`, `Bukti Dukung`).
- **Mendukung Rentang Tanggal**:
  - Format string: `"2026-06-15 - 2026-06-19"` atau `"2026-06-15 s.d 2026-06-19"`.
  - Format 2 kolom terpisah: `Tanggal` dan `Tanggal Selesai`.
  - Skrip otomatis mencentang opsi *"Gunakan periode tanggal"* di formulir KIPApp dan mengisikan tanggal awal serta tanggal akhir.
- **JSON**: Mengikuti struktur `daftar_kegiatan_template.json`.
- **Teks Chat**: Jika pengguna menulis daftar kegiatan di pesan, agen menyimpan ke file JSON lalu menjalankan skrip.

### 3. Pengisian Otomatis Bukti Dukung Google Drive
- Mendukung flag `--drive-url "<URL_FOLDER_DRIVE>"` untuk mengisi link bukti dukung pada form secara serentak jika kolom bukti dukung kosong.

### 4. Mode Eksekusi
- **Dry-Run (Preview Tanpa Save)**:
  ```bash
  uv run python auto_input_kegiatan.py --file <PATH_FILE> --periode "<PERIODE>" --drive-url "<URL_DRIVE>" --dry-run
  ```
- **Live Save (Simpan ke KIPApp)**:
  ```bash
  uv run python auto_input_kegiatan.py --file <PATH_FILE> --periode "<PERIODE>" --drive-url "<URL_DRIVE>"
  ```

---

## 📋 Daftar Butir Rencana Kinerja (Referensi Mapping)
- `pengolahan` : Terlaksanakannya kegiatan pengolahan yang berkualitas dan tepat waktu
- `perangkat dan jaringan` : Terlaksanakannya kegiatan pengelolaan perangkat dan jaringan yang berkualitas dan tepat waktu
- `pembinaan` : Terlaksanakannya kegiatan Pembinaan Statistik Sektoral yang berkualitas dan tepat waktu
- `sbr` : Terlaksanakannya kegiatan pengelolaan Statistic Business Register (SBR) yang berkualitas dan tepat waktu
- `kompetensi` : Terlaksananya Tata Kelola Pengembangan Kompetensi yang Tertib
- `monitoring` : Tersedianya Laporan Monitoring Kegiatan Statistik Kependudukan dan Ketenagakerjaan
- `sistem informasi` : Terlaksanakannya kegiatan pengembangan sistem informasi yang berkualitas dan tepat waktu
- `publikasi` : Tersedianya publikasi yang berkualitas dan tepat waktu
