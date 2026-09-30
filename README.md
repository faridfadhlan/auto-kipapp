# Otomasi Input Kegiatan KIPApp BPS

Aplikasi otomasi berbasis Playwright untuk mempermudah dan mempercepat pengisian catatan kegiatan pekerjaan harian di **KIPApp BPS** (`https://kipapp.bps.go.id`).

---

## 📌 Fitur Utama
1. **Sesi Login Persisten (`browser_data`)**: Login SSO BPS hanya perlu dilakukan sekali. Sesi tersimpan aman di direktori lokal tanpa perlu login berulang kali.
2. **Skill Antigravity (`kipapp`)**: Terpasang secara global (`~/.gemini/config/skills/kipapp/SKILL.md`) sehingga Anda bisa langsung meminta agen mengisikan kegiatan di sesi obrolan mana pun.
3. **Mendukung Berbagai Format File**:
   - File Excel (`.xlsx`, `.xls`)
   - File CSV (`.csv`)
   - File JSON (`.json`)
   - Teks langsung di pesan chat
4. **Integrasi Google Drive**: Otomatis mengisi link bukti dukung (bisa satu link folder utama atau link spesifik per kegiatan).
5. **Mode Dry-Run (Preview)**: Memungkinkan Anda melihat tampilan pengisian form sebelum disimpan ke server KIPApp (dilengkapi screenshot review).

---

## 📂 Struktur File

| File | Deskripsi |
| :--- | :--- |
| `auto_input_kegiatan.py` | Skrip utama untuk menjalankan otomasi input form kegiatan. |
| `generate_kegiatan_from_rk.py` | Skrip generator kegiatan otomatis dari daftar Rencana Kinerja (SKP). |
| `daftar_kegiatan_template.json` | Template data kegiatan berformat JSON. |
| `launch_login.py` | Skrip untuk membuka browser dan login manual pertama kali jika sesi kedaluwarsa. |
| `browser_data/` | Direktori penyimpanan profil browser & cookies (jangan dihapus/commit). |
| `.agents/skills/kipapp/SKILL.md` | Definisi skill Antigravity untuk agen. |

---

## 🚀 Cara Penggunaan

### 1. Menyiapkan Data Kegiatan
Anda bisa menyediakan file Excel (`.xlsx`), CSV (`.csv`), atau JSON (`.json`).

**Format Kolom Excel / CSV:**
- `Tanggal` (contoh: `2026-06-02`)
- `Kegiatan` (contoh: `Melakukan evaluasi hasil validasi data SE2026`)
- `Rencana Kinerja` (kata kunci butir SKP, misal: `pengolahan`, `sistem informasi`, `pembinaan`, `SBR`)
- `Capaian` (opsional, jika kosong disamakan dengan kegiatan)
- `Progres` (angka persentase, default: 100)
- `Bukti Dukung` (opsional, link Google Drive)

### 2. Melalui Obrolan Antigravity (Paling Mudah)
Cukup ketik perintah seperti:
> *"Tolong inputkan kegiatan Triwulan II dari file kegiatan_juni.xlsx, dengan folder bukti dukung https://drive.google.com/..."*

Agen akan otomatis mengaktifkan skill **`kipapp`** dan memprosesnya untuk Anda!

### 2. Uji Coba Pengisian (Dry-Run Preview)
Jalankan perintah ini untuk melihat form diisi secara visual tanpa benar-benar menyimpan ke server:
```bash
uv run python auto_input_kegiatan.py --dry-run
```
*(Screenshot hasil pengisian tiap baris akan tersimpan sebagai `preview_kegiatan_1.png`, `preview_kegiatan_2.png`, dst.)*

### 3. Eksekusi Pengisian Nyata (Live Save)
Setelah data kegiatan dipastikan benar, jalankan tanpa flag `--dry-run`:
```bash
uv run python auto_input_kegiatan.py --file daftar_kegiatan_template.json --periode "Triwulan II"
```
Skrip akan otomatis membuka form, mengisi seluruh data, dan mengklik tombol **Save** untuk tiap kegiatan.
