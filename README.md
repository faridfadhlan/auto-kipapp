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

---

## 📂 Struktur File

| File | Deskripsi |
| :--- | :--- |
| `auto_input_kegiatan.py` | Skrip utama untuk menjalankan otomasi input form kegiatan. |
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

### 1. Auto-Generate Kegiatan dari Butir SKP Anda

Skrip dan skill mendukung penyesuaian triwulan (`Triwulan I`, `Triwulan II`, `Triwulan III`, `Triwulan IV`, maupun `Tahunan`) serta tahun anggaran secara otomatis.

**Opsi A — Tarik butir SKP otomatis dari akun KIPApp Anda:**
```bash
# Contoh untuk Triwulan I
uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "Triwulan I" --tahun 2026

# Contoh untuk Triwulan III
uv run python generate_kegiatan_from_rk.py --fetch-rk --periode "Triwulan III"
```

**Opsi B — Masukkan butir SKP kustom Anda sendiri:**
```bash
uv run python generate_kegiatan_from_rk.py --rk "Nama Butir SKP 1; Nama Butir SKP 2" --periode "Triwulan III"
```
*(Hasilnya akan disimpan di `kegiatan_auto_generated.json` dengan rentang tanggal kerja efektif yang otomatis disesuaikan).*

---

### 2. Input Kegiatan dari File (Excel / CSV / JSON)

**Format Kolom Excel / CSV:**
- `Tanggal` (contoh: `2026-06-02` atau rentang `2026-06-02 - 2026-06-05`)
- `Tanggal Selesai` (opsional jika tanggal akhir di kolom terpisah)
- `Kegiatan` (contoh: `Melakukan evaluasi hasil validasi data SE2026`)
- `Rencana Kinerja` (kata kunci pembeda butir SKP Anda, misal: `pengolahan`, `keuangan`, `publikasi`)
- `Capaian` (opsional, jika kosong disamakan dengan kegiatan)
- `Progres` (angka persentase, default: 100)
- `Bukti Dukung` (opsional: link bebas web/Drive atau path file fisik lokal seperti `laporan.pdf`, `foto.jpg`)

> [!TIP]
> **Upload Otomatis File Lokal ke Google Drive**: Jika kolom `Bukti Dukung` diisi path file lokal, skrip akan otomatis mengupload file tersebut ke Google Drive melalui Google Drive API, membuat hak aksesnya dapat dilihat publik, dan menyisipkan link `webViewLink` ke KIPApp.
>
> **Konfigurasi Kredensial Google API:**
> 1. Salin `.env.example` menjadi `.env`.
> 2. Letakkan file kunci Google Cloud: `service_account.json` (Service Account) atau `credentials.json` (OAuth Client) di direktori proyek Anda atau di `~/.kipapp/`.
> 3. (Opsional) Masukkan ID Folder Drive tujuan pada `GDRIVE_FOLDER_ID`.

---

### 3. Eksekusi Pengisian Form KIPApp

**Mode Dry-Run (Preview Tanpa Menyimpan):**
```bash
uv run python auto_input_kegiatan.py --file kegiatan_auto_generated.json --periode "Triwulan II" --dry-run
```
*(Screenshot review form akan tersimpan sebagai `preview_kegiatan_1.png`, dst.)*

**Mode Live (Simpan Langsung ke KIPApp):**
```bash
uv run python auto_input_kegiatan.py --file kegiatan_auto_generated.json --periode "Triwulan II" --drive-url "https://drive.google.com/..."
```

### 4. Melalui Chat Agent AI Coding (Universal untuk Semua Agent)

Anda dapat langsung memberikan perintah menggunakan bahasa sehari-hari di jendela obrolan agent AI coding pilihan Anda (**Claude Code, Cursor, GitHub Copilot, Windsurf, Cline / Roo Code, Google Antigravity, OpenHands/Devin**, dll.). Agent akan otomatis membaca panduan proyek dan mengeksekusi perintah yang sesuai:

#### 🔹 Skenario A: Auto-Generate Kegiatan dari SKP
> *"Tolong buatkan kegiatan SKP untuk Triwulan II tahun 2026 dari akun KIPApp saya dan sebarkan ke hari kerja efektif."*

#### 🔹 Skenario B: Input dari File (Excel / CSV / JSON)
> *"Inputkan file kegiatan_juni.xlsx ke KIPApp periode Triwulan II dengan link folder bukti dukung https://drive.google.com/..."*

#### 🔹 Skenario C: Upload File Fisik Lokal Otomatis ke Google Drive
> *"Tolong inputkan kegiatan dari file capaian.xlsx ke KIPApp. Jika kolom bukti dukung memuat file PDF/foto lokal, upload otomatis ke Google Drive saya."*

#### 🔹 Skenario D: Uji Coba Pengisian (Dry-Run Preview)
> *"Coba simulasikan pengisian KIPApp untuk file kegiatan.json dengan mode dry-run, jangan klik simpan dulu."*

#### 🔹 Skenario E: Input Kegiatan Langsung Lewat Chat (Tanpa File)
> *"Tolong catat kegiatan ke KIPApp tanggal 15–19 Juni 2026: 'Pelaksanaan pengawasan survei ekonomi di lapangan' untuk butir SKP pengolahan dengan progres 100%."*
