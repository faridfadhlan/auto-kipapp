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
| `daftar_kegiatan_template.json` | Template data kegiatan berformat JSON. |
| `launch_login.py` | Skrip untuk membuka browser dan login manual pertama kali jika sesi kedaluwarsa. |
| `browser_data/` | Direktori penyimpanan profil browser & cookies (aman dan diabaikan oleh git). |
| `.agents/skills/kipapp/SKILL.md` | Definisi skill Antigravity untuk agen. |

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
- `Bukti Dukung` (opsional, link Google Drive)

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

---

### 4. Melalui Obrolan Antigravity (Paling Praktis)
Jika Anda menggunakan asisten AI Antigravity, cukup katakan:
> *"Tolong buatkan kegiatan untuk Triwulan II dari butir SKP saya dan langsung inputkan ke KIPApp dengan link bukti dukung https://drive.google.com/..."*

Agen akan secara otomatis mengaktifkan skill **`kipapp`**, mengambil butir SKP Anda, merancang kegiatan harian yang sesuai, dan memprosesnya.
