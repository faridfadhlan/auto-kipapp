# Otomasi Input Kegiatan KIPApp BPS

Aplikasi otomasi berbasis Playwright untuk mempermudah dan mempercepat pengisian catatan kegiatan pekerjaan harian di **KIPApp BPS** (`https://kipapp.bps.go.id`).

---

## 📌 Fitur Utama

1. **Arsitektur Hybrid (REST API Internal + Playwright Browser)**:
   - **Super Cepat (Milidetik)**: Berkomunikasi langsung dengan REST API internal KIPApp (`https://kipapp.bps.go.id/api/v1/`). Fetch SKP selesai dalam ~0.2 detik, input 10 kegiatan selesai dalam ~1–2 detik (vs 2–3 menit browser).
   - **Deterministik & Ringan**: Tidak membebani CPU dengan rendering DOM browser yang berat.
   - **Sesi Otomatis & Caching**: Token JWT Bearer otomatis disinkronkan dari sesi SSO browser dan dicache di `~/.kipapp/session_token.json`.
   - **Graceful Fallback & Visual Mode**: Otomatis membuka Playwright browser jika sesi habis atau jika pengguna menambahkan flag `--browser` untuk preview visual.
2. **Rencana Kinerja (SKP) Dinamis**: Menyesuaikan butir SKP masing-masing pegawai tanpa batasan fix/kaku (baik bidang Sosial, Distribusi, Produksi, Nerwilis, IPDS, Umum/TU, Fungsional Statistisi/Pranata Komputer, dsb.).
3. **Auto-Fetch Butir SKP**: Mampu membaca langsung seluruh butir Rencana Kinerja aktif dari akun KIPApp pengguna (`--fetch-rk`).
4. **Penyusunan Kegiatan Cerdas (AI / Generator)**: Otomatis menyusun tahapan kegiatan realistis (Persiapan, Pelaksanaan, Verifikasi, Pelaporan) ke hari kerja efektif (Senin–Jumat).
5. **Centang Capaian SKP Otomatis**: Opsi *"Masukan ke capaian SKP"* selalu dicentang secara default pada setiap kegiatan yang disimpan atau diperbarui.
6. **Sesi Login Persisten**: Login SSO BPS hanya perlu dilakukan sekali. Sesi tersimpan aman di direktori lokal `./browser_data` atau direktori pengguna `~/.kipapp/browser_data` dan otomatis dapat digunakan di folder project mana pun tanpa perlu login berulang kali.
7. **Mendukung Tanggal Tunggal & Rentang Tanggal**: Mendukung format `"YYYY-MM-DD"` maupun periode rentang `"YYYY-MM-DD - YYYY-MM-DD"`.
8. **Mendukung Berbagai Format File**:
   - File Excel (`.xlsx`, `.xls`)
   - File CSV (`.csv`)
   - File JSON (`.json`)
   - Teks langsung di pesan chat
9. **Integrasi Google Drive**: Otomatis mengisi link bukti dukung (folder utama atau per kegiatan) dan auto-upload file fisik lokal.
10. **Mode Dry-Run (Preview)**: Memungkinkan Anda melihat simulasi pengisian form atau preview tangkapan layar form (`--dry-run` atau `--dry-run --browser`).
11. **Edit / Pembaruan Isian Realisasi SKP**: Mampu memperbarui data kegiatan yang telah tersimpan di KIPApp secara massal dalam hitungan detik via REST API (`edit_kegiatan.py` atau `kipapp_api.py`).

---

## 📂 Struktur File

| File | Deskripsi |
| :--- | :--- |
| `kipapp_api.py` | Modul client REST API internal KIPApp BPS untuk operasi milidetik (fetch SKP, query RK, input kegiatan, bulk update, checklist). |
| `auto_input_kegiatan.py` | Skrip utama input kegiatan (otomatis menggunakan REST API super cepat, fallback ke Playwright browser atau flag `--browser`). |
| `edit_kegiatan.py` | Skrip otomasi untuk mengedit/memperbarui butir kegiatan (update tautan bukti dukung, progres, capaian, dan checklist SKP secara massal). |
| `generate_kegiatan_from_rk.py` | Generator kegiatan otomatis dari butir SKP pengguna (bisa fetch otomatis via API/browser atau input manual). |
| `gdrive_uploader.py` | Modul pengunggah otomatis file bukti dukung lokal ke Google Drive. |
| `daftar_kegiatan_template.json` | Template data kegiatan berformat JSON. |
| `launch_login.py` | Skrip untuk membuka browser dan login manual pertama kali jika sesi kedaluwarsa. |
| `browser_data/` | Direktori penyimpanan profil browser & cookies (aman dan diabaikan oleh git). |
| `AGENTS.md` | Panduan standar instruksi universal untuk semua agent AI. |
| `CLAUDE.md` | Konfigurasi bawaan untuk Claude Code CLI. |
| `.cursorrules` & `.cursor/` | Aturan bawaan untuk Cursor IDE (format MDC & legacy). |
| `.github/copilot-instructions.md`| Instruksi workspace untuk GitHub Copilot. |
| `.windsurfrules` | Aturan bawaan untuk Windsurf IDE (Cascade). |
| `.clinerules` | Aturan bawaan untuk Cline dan Roo Code. |
| `.agents/skills/kipapp/SKILL.md` | Definisi skill Antigravity untuk agen. |

---

## 🤖 Kompatibilitas Multi-Agent AI Coding

Skill dan otomasi ini langsung dikenali secara otomatis tanpa konfigurasi manual tambahan di berbagai platform AI coding agent:

- **Google Antigravity**: Membaca `.agents/skills/kipapp/SKILL.md` atau `~/.gemini/config/skills/kipapp/`.
- **Claude Code**: Membaca `CLAUDE.md`.
- **Cursor IDE**: Membaca `.cursorrules` dan `.cursor/rules/kipapp.mdc`.
- **GitHub Copilot**: Membaca `.github/copilot-instructions.md`.
- **Windsurf IDE (Cascade)**: Membaca `.windsurfrules`.
- **Cline & Roo Code**: Membaca `.clinerules`.
- **Kilo Code**: Membaca `.kilorules` dan `.clinerules`.
- **OpenCode & OpenHands**: Membaca `AGENTS.md`.
- **Zed (Z-Code / Zed AI)**: Membaca `AGENTS.md`.
- **Devin, Aider, Goose, & Open LLM Agents**: Membaca `AGENTS.md`.

## 🚀 Cara Penggunaan

Panduan langkah demi langkah dari awal (cloning repositori) hingga berinteraksi dengan AI Coding Agent:

---

### 📥 Langkah 1: Clone Repositori & Buka Proyek

Buka aplikasi terminal Anda dan jalankan perintah:

```bash
# 1. Clone repositori ini ke komputer Anda
git clone https://github.com/faridfadhlan/auto-kipapp.git

# 2. Masuk ke direktori proyek
cd auto-kipapp
```

Buka folder proyek `auto-kipapp` di IDE / Code Editor pilihan Anda:
- **Google Antigravity**: Buka folder `auto-kipapp` sebagai workspace aktif.
- **Cursor IDE**: Ketik `cursor .` di terminal atau pilih menu *File > Open Folder...* lalu pilih folder `auto-kipapp`.
- **VS Code** *(dengan GitHub Copilot / Cline / Roo Code)*: Ketik `code .` di terminal.
- **Windsurf IDE**: Ketik `windsurf .` atau buka folder `auto-kipapp`.
- **Claude Code**: Masuk ke terminal di folder `auto-kipapp`, lalu jalankan perintah `claude`.
- **Zed / Z-Code**: Ketik `zed .` atau buka folder `auto-kipapp`.

---

### 📦 Langkah 2: Persiapan Environment & Dependensi

Proyek ini membutuhkan Python (>= 3.10) dan mendukung pengelola paket modern [`uv`](https://github.com/astral-sh/uv) (sangat direkomendasikan karena cepat & tanpa perlu konfigurasi virtualenv manual) maupun `pip` standar.

#### Opsi A: Menggunakan `uv` (Direkomendasikan)
Jika Anda belum menginstal `uv`, pasang dengan satu perintah:
- **macOS / Linux**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows (PowerShell)**:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

Kemudian instal browser Chromium untuk Playwright:
```bash
uv run playwright install chromium
```
*(Dengan `uv`, seluruh pustaka Python otomatis diunduh dan dipasang secara terisolasi saat skrip pertama kali dijalankan).*

#### Opsi B: Menggunakan `pip` & Virtual Environment Standar
```bash
python3 -m venv .venv
source .venv/bin/activate       # macOS / Linux
# Di Windows: .venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium
```

---

### 🔑 Langkah 3: Inisialisasi Sesi Login SSO BPS (Hanya Dilakukan Sekali)

Sebelum meminta Agent AI menginputkan kegiatan, hubungkan akun KIPApp Anda sekali saja:

```bash
uv run python launch_login.py
# Atau jika menggunakan pip/venv: python launch_login.py
```

1. Jendela browser Chromium akan otomatis terbuka menampilkan portal login SSO BPS KIPApp (`https://kipapp.bps.go.id`).
2. Masukkan **Username (NIP / Akun SSO)** dan **Password SSO BPS** Anda.
3. Setelah berhasil masuk ke halaman dashboard KIPApp, tutup browser atau biarkan skrip menutupnya secara otomatis.
4. **Selesai!** Profil dan sesi login tersimpan aman di `browser_data/` (dan terpusat di `~/.kipapp/browser_data/`). Token JWT API internal otomatis diekstrak dan dicache. Anda **tidak perlu login lagi** untuk eksekusi-eksekusi berikutnya.

---

### ⚙️ Langkah 4 (Opsional): Konfigurasi Bukti Dukung Google Drive

Jika Anda ingin bukti dukung fisik lokal (misal file `laporan.pdf`, `foto.jpg`, `notulen.docx`) otomatis diunggah ke Google Drive dan dijadikan tautan publik:
1. Salin template `.env`:
   ```bash
   cp .env.example .env
   ```
2. Isi `GDRIVE_FOLDER_ID` di file `.env` dengan ID folder Google Drive tujuan Anda.
3. Letakkan file kredensial Google (`service_account.json` atau `credentials.json`) di folder proyek atau di `~/.kipapp/`.

> [!NOTE]
> Jika bukti dukung Anda sudah berupa tautan online/Google Drive yang sudah ada, langkah ini bisa dilewati.

---

### 💬 Langkah 5: Memulai Obrolan dengan AI Coding Agent

Sekarang proyek Anda telah siap sepenuhnya! Buka panel obrolan (chat) AI di editor Anda:
- **Google Antigravity**: Klik panel chat di samping atau tekan shortcut chat.
- **Cursor IDE**: Tekan `Cmd + L` (Mac) atau `Ctrl + L` (Windows/Linux) untuk membuka Cursor Composer / Chat.
- **Windsurf IDE**: Buka panel *Cascade*.
- **Claude Code**: Langsung ketik instruksi di sesi terminal `claude`.
- **GitHub Copilot / Cline / Roo Code**: Buka tab chat di sidebar VS Code.

Agent AI secara otomatis membaca seluruh pedoman dan modul otomasi (`AGENTS.md`, `SKILL.md`, `.cursorrules`, dll.). Cukup berikan instruksi dalam **bahasa Indonesia sehari-hari** tanpa perlu menghafal sintaks perintah terminal!

---

### 💬 Contoh Perintah Chat ke Agent AI:

#### 🔹 1. Mengambil Referensi dari File Catatan Bebas (`.txt`, `.md`, Log Kerja)
> *"Saya punya catatan kegiatan di file `catatan_harian.txt`. Tolong baca file tersebut, cocokkan setiap aktivitasnya dengan butir SKP di akun KIPApp saya untuk Triwulan II 2026, lalu inputkan ke KIPApp."*

#### 🔹 2. Mengambil Referensi dari Rekap Excel / CSV
> *"Tolong baca file `rekap_pekerjaan.xlsx` (atau `daftar_kegiatan.csv`). Sesuaikan tanggal dan kegiatannya dengan SKP saya di KIPApp Triwulan II, lalu simpan ke KIPApp dengan link bukti dukung https://drive.google.com/..."*

#### 🔹 3. Membaca File Referensi dengan Filter Tanggal Spesifik
> *"Dari file `log_tugas.txt`, ambil hanya kegiatan untuk minggu kedua Juni (tanggal 8 s.d 12 Juni 2026), lalu inputkan ke KIPApp Triwulan II."*

#### 🔹 4. Auto-Generate Kegiatan dari Butir SKP Akun Anda (Tanpa File)
> *"Tolong buatkan kegiatan SKP untuk Triwulan II tahun 2026 dari akun KIPApp saya dan sebarkan ke hari kerja efektif."*

#### 🔹 5. Input File dengan Bukti Dukung Lokal (Auto-Upload ke Google Drive)
> *"Tolong inputkan kegiatan dari file `capaian.xlsx` ke KIPApp. Jika kolom bukti dukung memuat file PDF/foto lokal, upload otomatis ke Google Drive saya."*

#### 🔹 6. Simulasi / Uji Coba Pengisian (Dry-Run Preview)
> *"Coba simulasikan pengisian KIPApp dari file `catatan.txt` dengan mode dry-run, tampilkan screenshot preview dan jangan klik simpan dulu."*

#### 🔹 7. Input Kegiatan Langsung Lewat Chat (Tanpa File)
> *"Tolong catat kegiatan ke KIPApp tanggal 15–19 Juni 2026: 'Pelaksanaan pengawasan survei ekonomi di lapangan' untuk butir SKP pengolahan dengan progres 100%."*

#### 🔹 8. Edit / Pembaruan Massal Butir Realisasi (Update Bukti Dukung ke Google Drive)
> *"Tolong tambahkan/update semua bukti dukung kegiatan di Triwulan II ke URL folder Google Drive: https://drive.google.com/drive/folders/<ID_FOLDER_GOOGLE_DRIVE>"*
> *(Atau: "Lengkapi bukti dukung yang masih kosong saja di Triwulan II dengan link Drive https://drive.google.com/drive/folders/...")*

#### 🔹 9. Centang Massal Capaian SKP
> *"Tolong cek dan centang semua kegiatan saya di Triwulan III agar masuk ke capaian SKP."*

---

## ⚡ Eksekusi CLI Cepat (REST API & Mode Visual)

Semua skrip otomatis berjalan dalam **mode REST API super cepat** secara default:

```bash
# 1. Fetch SKP & Auto-Generate Kegiatan (~0.2 detik)
uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "Triwulan III"

# 2. Input Kegiatan Cepat via REST API (~1 detik)
uv run python auto_input_kegiatan.py --file kegiatan_auto_generated.json --periode "Triwulan III"

# 3. Input Kegiatan Mode Browser Visual (Playwright)
uv run python auto_input_kegiatan.py --file kegiatan_auto_generated.json --periode "Triwulan III" --browser

# 4. Edit Bukti Dukung / Progres Massal via REST API
uv run python edit_kegiatan.py --periode "Triwulan III" --drive-url "https://drive.google.com/..." --all

# 5. Utilitas REST API Langsung (Inspeksi & Checklist)
uv run python kipapp_api.py --list-skp
uv run python kipapp_api.py --list-rk --periode "Triwulan III"
uv run python kipapp_api.py --list-kegiatan --periode "Triwulan III"
uv run python kipapp_api.py --update-checklists --periode "Triwulan III"
```

## ☁️ Integrasi Google Drive (Auto-Upload Bukti Dukung)

Aplikasi ini mendukung **pengunggahan otomatis file bukti fisik lokal** (seperti `laporan.pdf`, `foto_kegiatan.jpg`, `notulen.docx`, dll.) langsung ke Google Drive Anda melalui Google Drive API.

### 🔄 Cara Kerja:
1. Saat Anda mengisi kolom bukti dukung dengan path file lokal di komputer Anda, sistem otomatis mengunggah file tersebut ke Google Drive.
2. Hak akses file di Google Drive otomatis diatur ke publik (*Anyone with the link can view*).
3. Tautan publik (`webViewLink`) langsung disisipkan ke dalam isian formulir KIPApp BPS.

---

### ⚙️ Langkah Konfigurasi (Pilih Salah Satu):

#### Opsi 1: Google Service Account (Paling Praktis & Tanpa Pop-up Login)
1. Buka [Google Cloud Console](https://console.cloud.google.com/), buat project baru (atau gunakan yang sudah ada), lalu aktifkan **Google Drive API**.
2. Buat **Service Account** di menu *IAM & Admin* > *Service Accounts*.
3. Buat dan unduh kunci privat JSON (*Create key* > *JSON*).
4. Simpan file tersebut di folder proyek Anda dengan nama `service_account.json` (atau di direktori global `~/.kipapp/service_account.json`).
5. **Penting**: Buka folder Google Drive tempat Anda ingin menyimpan file bukti, klik **Bagikan (Share)**, lalu masukkan alamat email Service Account Anda sebagai **Editor**.

#### Opsi 2: Google OAuth 2.0 Client (Desktop App)
1. Di Google Cloud Console, buka menu *APIs & Services* > *Credentials*.
2. Buat kredensial bertipe **OAuth client ID** dengan jenis aplikasi **Desktop App**.
3. Unduh file kredensial JSON dan simpan di folder proyek dengan nama `credentials.json` (atau di `~/.kipapp/credentials.json`).
4. Pada proses upload pertama kali, browser akan membuka jendela persetujuan izin akses Google Drive sekali saja.

---

### 📁 Menentukan Folder Google Drive Tujuan (`.env`):
1. Salin template konfigurasi:
   ```bash
   cp .env.example .env
   ```
2. Salin ID folder dari tautan Google Drive Anda:
   - Contoh URL: `https://drive.google.com/drive/folders/1aBcDeFgHiJkLmNoPqRsTuVwXyZ`
   - Maka ID-nya adalah: `1aBcDeFgHiJkLmNoPqRsTuVwXyZ`
3. Masukkan ID tersebut ke dalam file `.env`:
   ```env
   GDRIVE_FOLDER_ID=1aBcDeFgHiJkLmNoPqRsTuVwXyZ
   ```
*(Jika dikosongkan, file akan otomatis diunggah ke root My Drive).*

> [!NOTE]
> File kredensial (`service_account*.json`, `credentials*.json`, token, dan `.env`) sudah otomatis terdaftar di `.gitignore` untuk mencegah kebocoran data sensitif ke publik.
