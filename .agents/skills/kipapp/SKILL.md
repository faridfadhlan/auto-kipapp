---
name: kipapp
description: Mengotomasi input catatan kegiatan harian di KIPApp BPS (https://kipapp.bps.go.id). Gunakan skill ini setiap kali pengguna meminta untuk menginput, mengecek, auto-generate dari rencana SKP pengguna, melengkapi bukti dukung Google Drive, atau submit kegiatan pekerjaan ke KIPApp BPS dari file (Excel/CSV/JSON) maupun teks langsung.
---

# KIPApp BPS Automation Skill

Skill ini memandu agen untuk mengotomasi seluruh siklus pengisian, pelengkapan bukti dukung, penyusunan kegiatan dinamis sesuai Rencana Kinerja (SKP) pengguna, dan pengiriman catatan kegiatan di **KIPApp BPS** (`https://kipapp.bps.go.id`).

---

## 📍 Lingkungan & Lokasi Proyek

- **Direktori Proyek**: **Dinamis menyesuaikan folder project aktif pengguna** (`current working directory` / root workspace pengguna saat ini).
  - Agen TIDAK BOLEH mengasumsikan folder bernama tertentu (seperti `auto-kipapp`).
  - Semua file input pengguna (Excel, CSV, JSON) dibaca langsung dari folder project aktif tempat pengguna berada.
  - Semua file output yang dihasilkan (seperti `kegiatan_auto_generated.json`, screenshot review) disimpan langsung di folder project aktif tempat pengguna berada.
- **Eksekusi Skrip Otomasi**:
  - Jika skrip otomasi tersedia di folder project pengguna:
    ```bash
    uv run python auto_input_kegiatan.py ...
    ```
  - Jika pengguna berada di folder project lain, agen dapat menjalankan skrip dari repositori skill global:
    ```bash
    uv run python ~/.gemini/config/skills/kipapp/scripts/auto_input_kegiatan.py ...
    ```
- **Sesi Login Browser**:
  - Terpusat dan otomatis dideteksi di `./browser_data` (jika ada di project) atau `~/.kipapp/browser_data` (direktori global pengguna). Login SSO BPS hanya perlu dilakukan sekali dan langsung berlaku untuk project pengguna mana pun.

---

## 🎯 Fleksibilitas Rencana Kinerja (SKP Dinamis Per Pegawai)

> [!IMPORTANT]
> **Rencana Kinerja (SKP) bersifat unik dan dinamis untuk masing-masing pegawai.**
> Butir SKP bervariasi sesuai unit kerja atau tim fungsi (Statistik Sosial, Statistik Distribusi, Statistik Produksi, Nerwilis, IPDS, Bagian Umum/Tata Usaha, Fungsional Statistisi, Pranata Komputer, dll.).
> Jangan mengasumsikan butir SKP statis atau tetap.
>
> **Aturan Khusus Pemetaan Butir SKP BPS:**
> - Kegiatan terkait **entri dokumen**, **tabulasi**, **ekspor data**, maupun **backup data** **HARUS** dipetakan ke butir Rencana Kinerja **pengolahan** (keyword: `pengolahan`).
> - Kegiatan pemeriksaan draf/naskah publikasi dipetakan ke butir **publikasi** (keyword: `publikasi`).
> - Opsi checkbox *"Masukan ke capaian SKP"* pada formulir KIPApp **HARUS SELALU DICENTANG (CHECKED)** secara default untuk semua kegiatan yang disimpan.

---

## 📅 Penyesuaian Triwulan & Tahun Otomatis dari Prompt

Agen dan skrip **secara otomatis mengenali dan menyesuaikan triwulan serta tahun** dari permintaan pengguna:

| Input Prompt Pengguna | Periode KIPApp | Rentang Tanggal Otomatis (Hari Kerja) |
| :--- | :--- | :--- |
| *"Triwulan 1"*, *"TW I"*, *"Januari - Maret"* | `Triwulan I` | `01 Januari` s.d `31 Maret` |
| *"Triwulan 2"*, *"TW II"*, *"April - Juni"* | `Triwulan II` | `01 April` s.d `30 Juni` |
| *"Triwulan 3"*, *"TW III"*, *"Juli - September"* | `Triwulan III` | `01 Juli` s.d `30 September` |
| *"Triwulan 4"*, *"TW IV"*, *"Oktober - Desember"* | `Triwulan IV` | `01 Oktober` s.d `31 Desember` |
| *"Tahunan"* | `Tahunan` | `01 Januari` s.d `31 Desember` |

- **Deteksi Tahun**: Jika pengguna menyebutkan tahun (misal: *"Triwulan 3 tahun 2026"*), gunakan `--tahun 2026` dan tahun pada tanggal akan otomatis diset ke `2026`. Jika tidak disebutkan, default ke tahun berjalan.
- **Normalisasi Otomatis**: Skrip menerima format angka Arab (`1`, `2`, `3`, `4`) maupun Romawi (`I`, `II`, `III`, `IV`) dan otomatis mencocokkannya ke opsi dropdown KIPApp.

### Cara Mengetahui & Menangani Rencana Kinerja Pengguna:

1. **Auto-Fetch Otomatis dari Akun KIPApp Pengguna:**
   Jalankan skrip generator dengan flag `--fetch-rk`:
   ```bash
   uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "<PERIODE>"
   ```
   Skrip akan membuka KIPApp, membaca dropdown pilihan SKP yang sedang aktif di akun pengguna tersebut, dan menampilkan seluruh butir Rencana Kinerjanya secara presisi.

2. **Diberikan Manual oleh Pengguna (Teks Chat / File):**
   Pengguna dapat memberikan butir SKP di pesan chat atau lewat file:
   ```bash
   uv run python generate_kegiatan_from_rk.py --rk "Nama Butir SKP 1; Nama Butir SKP 2" --periode "<PERIODE>"
   ```
   Atau menggunakan file JSON daftar butir SKP:
   ```bash
   uv run python generate_kegiatan_from_rk.py --rk-file daftar_rk.json --periode "<PERIODE>"
   ```

3. **Penyusunan Berbasis Kemampuan LLM / AI Agen (Paling Direkomendasikan):**
   Agen dapat langsung memanfaatkan pemahaman bahasa alami untuk merancang rincian kegiatan kerja harian ASN yang spesifik, realistis, dan berbobot sesuai dengan tupoksi butir SKP pengguna. Kegiatan disebar ke hari kerja efektif (Senin – Jumat), lalu disimpan ke format JSON sebelum diinput.

---

## 🚀 Kemampuan & Alur Penggunaan

### 1. Auto-Generate Kegiatan Dinamis
Jika pengguna meminta *"buatkan kegiatan dari SKP saya"*:
- Tarik butir SKP via `--fetch-rk` atau gunakan butir SKP yang disediakan pengguna.
- Generate kegiatan dengan tahapan realistis (Persiapan & Koordinasi, Pelaksanaan Teknis, Verifikasi & Validasi, Pelaporan/Evaluasi).
- Simpan ke file JSON (contoh `kegiatan_auto_generated.json`).

### 2. Input Kegiatan dari File (Excel, CSV, JSON, TXT/Catatan Bebas) atau Teks Chat
- **File Teks & Catatan Harian (`.txt`, `.tsv`, `.log`, `.md`)**:
  - Didukung langsung: format pipe (`Tanggal | SKP | Kegiatan | Progres | Link`), tab, format bullet (`- 5 Juni 2026: Kegiatan...`), atau baris tanggal ISO (`2026-06-05: Kegiatan...`).
  - Untuk file catatan bebas atau notulen: Agen membaca file pengguna, mengekstrak kegiatan, mencocokkannya ke SKP KIPApp via kemampuan bahasa alami/LLM, lalu menyusun file JSON input untuk dieksekusi.
- **Excel (`.xlsx` / `.xls`) & CSV**: Kolom otomatis dideteksi (`Tanggal`, `Tanggal Selesai`, `Kegiatan`, `Rencana Kinerja`, `Capaian`, `Progres`, `Bukti Dukung`).
- **Mendukung Rentang Tanggal**:
  - Format string: `"2026-06-15 - 2026-06-19"` atau `"2026-06-15 s.d 2026-06-19"`.
  - Format 2 kolom terpisah: `Tanggal` dan `Tanggal Selesai`.
  - Skrip otomatis mencentang opsi *"Gunakan periode tanggal"* di formulir KIPApp dan mengisi rentang kalender.
- **JSON**: Mengikuti struktur `daftar_kegiatan_template.json`.

### 3. Pengisian Fleksibel Bukti Dukung (Link Web / Drive / Upload File Otomatis)
- **Link Bebas**: Kolom bukti dukung dapat berupa URL apa pun (link folder Google Drive, link file, atau tautan web internal).
- **Upload File Lokal Otomatis ke Google Drive**:
  - Jika bukti dukung berupa path file lokal (misal: `laporan.pdf`, `foto_kegiatan.jpg`, `notulen.docx`), skrip otomatis mengupload file tersebut ke Google Drive via Google Drive API.
  - Akses file otomatis disetel ke publik (`anyone with link can view`), lalu tautan Google Drive (`webViewLink`) disisipkan ke form KIPApp.
  - Parameter opsional: `--gdrive-folder-id "<ID_FOLDER>"` untuk mengarahkan upload ke folder Drive tertentu.
- **Konfigurasi Kredensial Google Drive**:
  - Letakkan `service_account.json` (Google Cloud Service Account, direkomendasikan) atau `credentials.json` (OAuth Desktop App) di folder proyek atau di `~/.kipapp/`.
  - Atau konfigurasikan path-nya di file `.env` (contoh tersedia di `.env.example`).
- **Default Link Drive Global**: Mendukung flag `--drive-url "<URL_FOLDER_DRIVE>"` sebagai fallback jika kolom bukti dukung kosong.

### 4. Mode Eksekusi
- **Dry-Run (Preview Tanpa Save)**:
  ```bash
  uv run python auto_input_kegiatan.py --file <PATH_FILE> --periode "<PERIODE>" --drive-url "<URL_DRIVE>" --dry-run
  ```
- **Live Save (Simpan ke KIPApp)**:
  ```bash
  uv run python auto_input_kegiatan.py --file <PATH_FILE> --periode "<PERIODE>" --drive-url "<URL_DRIVE>"
  ```

### 5. Edit / Pembaruan Massal Realisasi Kegiatan (`edit_kegiatan.py`)
Mendukung pembaruan tautan bukti dukung, progres, capaian, dan centang SKP untuk kegiatan yang sudah ada di KIPApp:
- **Update Semua Bukti Dukung di Triwulan Tertentu**:
  ```bash
  uv run python edit_kegiatan.py --periode "<PERIODE>" --drive-url "<URL_GOOGLE_DRIVE>" --all
  ```
- **Update HANYA yang Belum Punya Bukti**:
  ```bash
  uv run python edit_kegiatan.py --periode "<PERIODE>" --drive-url "<URL_GOOGLE_DRIVE>" --only-empty-bukti
  ```
- **Filter Berdasarkan Kata Kunci Kegiatan atau Tanggal**:
  ```bash
  uv run python edit_kegiatan.py --periode "<PERIODE>" --drive-url "<URL_GOOGLE_DRIVE>" -k "publikasi"
  ```

---

## 🔍 Mekanisme Pencocokan Dropdown Rencana Kinerja
Di form input KIPApp, skrip mencocokkan kata kunci (`rencana_kinerja_keyword`) dengan opsi pada dropdown:
- Cukup berikan kata pembeda yang unik (2–4 kata dari kalimat SKP pengguna, misalnya `"pengolahan"`, `"pengelolaan perangkat"`, `"pembinaan statistik"`, `"administrasi keuangan"`, dsb.).
- Skrip akan mencari elemen dropdown yang memuat teks tersebut secara otomatis.
