# Otomasi Input Kegiatan KIPApp BPS

Aplikasi otomasi berbasis Playwright untuk mempermudah dan mempercepat pengisian catatan kegiatan pekerjaan harian di **KIPApp BPS** (`https://kipapp.bps.go.id`).

---

## 📌 Fitur Utama

1. **Rencana Kinerja (SKP) Dinamis**: Menyesuaikan butir SKP masing-masing pegawai tanpa batasan fix/kaku (baik bidang Sosial, Distribusi, Produksi, Nerwilis, IPDS, Umum/TU, Fungsional Statistisi/Pranata Komputer, dsb.).
2. **Auto-Fetch Butir SKP**: Mampu membaca langsung seluruh butir Rencana Kinerja aktif dari akun KIPApp pengguna (`--fetch-rk`).
3. **Penyusunan Kegiatan Cerdas (AI / Generator)**: Otomatis menyusun tahapan kegiatan realistis (Persiapan, Pelaksanaan, Verifikasi, Pelaporan) ke hari kerja efektif (Senin–Jumat).
4. **Sesi Login Persisten**: Login SSO BPS hanya perlu dilakukan sekali. Sesi tersimpan aman di direktori lokal `./browser_data` atau direktori pengguna `~/.kipapp/browser_data` dan otomatis dapat digunakan di folder project mana pun tanpa perlu login berulang kali.
5. **Mendukung Tanggal Tunggal & Rentang Tanggal**: Mendukung format `"YYYY-MM-DD"` maupun periode rentang `"YYYY-MM-DD - YYYY-MM-DD"`.
6. **Mendukung Berbagai Format File**:
   - File Excel (`.xlsx`, `.xls`)
   - File CSV (`.csv`)
   - File JSON (`.json`)
   - Teks langsung di pesan chat
7. **Integrasi Google Drive**: Otomatis mengisi link bukti dukung (folder utama atau per kegiatan).
8. **Mode Dry-Run (Preview)**: Memungkinkan Anda melihat tampilan pengisian form sebelum disimpan ke server KIPApp (dilengkapi screenshot review).
9. **Edit / Pembaruan Isian Realisasi SKP**: Mampu memperbarui data kegiatan yang telah tersimpan di KIPApp secara massal maupun terfilter (mengisi/mengganti tautan bukti dukung Google Drive, mengubah persentase progres, deskripsi capaian, dan centang capaian SKP).

---

## 📂 Struktur File

| File | Deskripsi |
| :--- | :--- |
| `auto_input_kegiatan.py` | Skrip utama untuk menjalankan otomasi input form kegiatan. |
| `edit_kegiatan.py` | Skrip otomasi untuk mengedit/memperbarui butir kegiatan (misal update tautan bukti dukung, progres, capaian). |
| `generate_kegiatan_from_rk.py` | Generator kegiatan otomatis dari butir SKP pengguna (bisa fetch otomatis atau manual). |
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
- **Windsurf IDE**: Membaca `.windsurfrules`.
- **Cline & Roo Code**: Membaca `.clinerules`.
- **OpenHands / Devin / Standard LLM**: Membaca `AGENTS.md`.

---

## 🚀 Cara Penggunaan

Anda tidak perlu menghafal atau mengetik perintah terminal secara manual. Cukup berikan instruksi menggunakan bahasa sehari-hari langsung di jendela obrolan agent AI coding Anda (**Google Antigravity, Claude Code, Cursor, GitHub Copilot, Windsurf, Cline / Roo Code, OpenHands/Devin**, dll.). Agent akan secara mandiri mengenali konteks, menyusun data kegiatan, dan mengeksekusi otomasi KIPApp.

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

---

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
