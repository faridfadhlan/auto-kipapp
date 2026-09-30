import json
import random
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

USER_DATA_DIR = Path(__file__).parent / "browser_data"

TEMPLATES_PER_RK = {
    "pengolahan": [
        ("Pemeriksaan konsistensi tabulasi hasil pendataan", "Terselesaikannya pemeriksaan konsistensi data pendataan dengan akurat"),
        ("Validasi anomali data survei sektoral", "Teridentifikasi dan terselesaikannya validasi anomali data survei"),
        ("Monitoring progres kelengkapan dokumen pengolahan", "Terlaksananya monitoring kelengkapan dokumen pengolahan per kabupaten/kota"),
        ("Pembersihan dan rekonsiliasi data mentah survei", "Tersusunnya data bersih hasil rekonsiliasi survei"),
    ],
    "perangkat dan jaringan": [
        ("Pemeliharaan berkala server dan jaringan intranet kantor", "Terlaksananya pemeliharaan server dan stabilitas jaringan intranet"),
        ("Pemeriksaan keamanan firewall dan koneksi internet BPS", "Terverifikasinya konfigurasi keamanan firewall dan kelancaran akses internet"),
        ("Penanganan kendala teknis perangkat PC dan printer pegawai", "Terselesaikannya perbaikan kendala teknis perangkat kerja pegawai"),
        ("Backup berkala konfigurasi switch dan router jaringan", "Tersimpannya cadangan konfigurasi perangkat jaringan dengan aman"),
    ],
    "pembinaan": [
        ("Koordinasi teknis pembinaan statistik sektoral bersama OPD Pemda", "Terlaksananya koordinasi teknis penyelenggaraan statistik sektoral dengan OPD"),
        ("Evaluasi kepatuhan prinsip Satu Data Indonesia (SDI) pada produsen data", "Tersusunnya catatan evaluasi kepatuhan prinsip Satu Data Indonesia"),
        ("Pemberian asistensi metadata statistik sektoral untuk dinas terkait", "Terlaksananya pendampingan penyusunan metadata statistik sektoral"),
        ("Penelaahan standar data dan rekomendasi statistik kegiatan OPD", "Terselesaikannya telaah standar data dan rekomendasi statistik kegiatan"),
    ],
    "sbr": [
        ("Pembaruan direktori usaha Statistical Business Register (SBR)", "Terlaksananya verifikasi dan pembaruan data direktori usaha SBR"),
        ("Validasi keaktifan unit usaha hasil survei ke dalam basis data SBR", "Terverifikasinya status keaktifan unit usaha pada basis data SBR"),
        ("Pencocokan data izin usaha oss dengan profil direktori SBR", "Tersinkronisasinya data perizinan usaha ke dalam profil SBR"),
        ("Penyusunan laporan rekonsiliasi anomali data unit statistik usaha", "Tersusunnya laporan hasil rekonsiliasi anomali unit usaha"),
    ],
    "kompetensi": [
        ("Mengikuti webinar / sosialisasi peningkatan kompetensi ASN BPS", "Telah mengikuti kegiatan sosialisasi peningkatan kompetensi teknis ASN"),
        ("Penyusunan rencana kebutuhan pembelajaran mandiri pegawai", "Tersusunnya usulan kebutuhan pengembangan kompetensi pegawai"),
        ("Pemberian sharing knowledge terkait tata kelola data statistik kepada rekan tim", "Terlaksananya sesi berbagi pengetahuan teknis kepada anggota tim"),
    ],
    "monitoring": [
        ("Penyusunan dashboard monitoring pencapaian target survei kependudukan", "Tersedianya visualisasi progres pengumpulan data survei kependudukan"),
        ("Analisis kelengkapan sampel survei angkatan kerja (Sakernas)", "Tersusunnya laporan evaluasi pemenuhan sampel Sakernas"),
        ("Evaluasi non-response rate survei sosial ekonomi kependudukan", "Tercatatnya tingkat respon dan mitigasi sampel non-response"),
    ],
    "sistem informasi": [
        ("Pengembangan fitur baru modul pelaporan aplikasi internal BPS", "Terselesaikannya implementasi fitur baru modul pelaporan aplikasi"),
        ("Pengujian fungsi (black-box testing) modul entri sistem informasi", "Terdokumentasikannya hasil pengujian fungsionalitas modul sistem"),
        ("Optimalisasi query basis data dan performa aplikasi web", "Meningkatnya kecepatan pemrosesan query basis data aplikasi"),
        ("Dokumentasi teknis dan perbaikan bug pada API integrasi data", "Tersusunnya dokumentasi teknis dan terselesaikannya patch bug API"),
    ],
    "publikasi": [
        ("Penelaahan tabel angka dan infografis draf publikasi statistik", "Terverifikasinya akurasi tabel angka dan visualisasi draf publikasi"),
        ("Penyusunan ulasan deskriptif indikator strategis daerah", "Tersusunnya narasi deskriptif draf rilis indikator strategis"),
        ("Layouting dan finalisasi naskah publikasi statistik tahunan", "Terselesaikannya tata letak dan tata bahasa naskah publikasi"),
    ]
}

def generate_activities_for_empty_rk(start_date="2026-04-01", end_date="2026-06-30", drive_url="", rk_keywords=None):
    if rk_keywords is None:
        rk_keywords = list(TEMPLATES_PER_RK.keys())
    
    # Kumpulkan hari kerja (Senin - Jumat) di rentang tanggal
    cur = datetime.date.fromisoformat(start_date)
    end = datetime.date.fromisoformat(end_date)
    workdays = []
    while cur <= end:
        if cur.weekday() < 5: # 0-4 = Senin-Jumat
            workdays.append(cur.strftime("%Y-%m-%d"))
        cur += datetime.timedelta(days=1)

    generated = []
    used_dates = set()

    for key in rk_keywords:
        matched_key = key.lower()
        if matched_key not in TEMPLATES_PER_RK:
            # Cari substring match
            for k in TEMPLATES_PER_RK:
                if k in matched_key:
                    matched_key = k
                    break
        
        if matched_key not in TEMPLATES_PER_RK:
            continue

        templates = TEMPLATES_PER_RK[matched_key]
        for keg, cap in templates[:2]: # Ambil 2 kegiatan per RK
            avail_dates = [d for d in workdays if d not in used_dates]
            if not avail_dates:
                avail_dates = workdays
            chosen_date = random.choice(avail_dates)
            used_dates.add(chosen_date)

            generated.append({
                "tanggal": chosen_date,
                "rencana_kinerja_keyword": matched_key,
                "kegiatan": keg,
                "progres": 100,
                "capaian": cap,
                "link_dukung": drive_url,
                "masuk_capaian_skp": False
            })

    # Sort berdasarkan tanggal
    generated.sort(key=lambda x: x["tanggal"])

    out_file = Path("kegiatan_auto_generated.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(generated, f, indent=2, ensure_ascii=False)

    print(f"Berhasil membuat {len(generated)} kegiatan baru untuk butir-butir RK yang masih kosong!")
    print(f"File disimpan di: {out_file.resolve()}")
    return out_file

if __name__ == "__main__":
    generate_activities_for_empty_rk()
