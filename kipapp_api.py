#!/usr/bin/env python3
"""
KIPApp BPS REST API Client Module
Menyediakan akses langsung ke REST API internal KIPApp BPS (https://kipapp.bps.go.id/api/v1/)
untuk eksekusi yang super-cepat (dalam hitungan milidetik), deterministik, dan stabil tanpa beban DOM browser.
"""

import os
import sys
import json
import time
import re
import base64
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_URL = "https://kipapp.bps.go.id/api/v1"
CACHE_TOKEN_FILE = Path.home() / ".kipapp" / "session_token.json"


def get_browser_data_dir(custom_path: str = "") -> Path:
    """Menemukan direktori browser_data secara dinamis."""
    if custom_path:
        p = Path(custom_path).expanduser().resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p
    cwd_dir = Path.cwd() / "browser_data"
    if cwd_dir.exists():
        return cwd_dir
    script_dir = Path(__file__).parent / "browser_data"
    if script_dir.exists():
        return script_dir
    home_dir = Path.home() / ".kipapp" / "browser_data"
    home_dir.mkdir(parents=True, exist_ok=True)
    return home_dir


def normalize_periode(periode_str: str) -> str:
    """Menormalkan format triwulan input menjadi nama standar."""
    p = str(periode_str).strip().lower()
    if re.search(r'\b(tw|triwulan)?\s*(iv|4)\b', p):
        return "Triwulan IV"
    elif re.search(r'\b(tw|triwulan)?\s*(iii|3)\b', p):
        return "Triwulan III"
    elif re.search(r'\b(tw|triwulan)?\s*(ii|2)\b', p):
        return "Triwulan II"
    elif re.search(r'\b(tw|triwulan)?\s*(i|1)\b', p):
        return "Triwulan I"
    elif "tahunan" in p:
        return "Tahunan"
    return periode_str


class KipappAPI:
    """Client REST API KIPApp BPS menggunakan token x-auth."""

    def __init__(self, browser_data: str = ""):
        self.browser_data = str(get_browser_data_dir(browser_data))
        self.auth_token: Optional[str] = None
        self.pegawai_id: Optional[str] = None
        self.nip_lama: Optional[str] = None
        self.nama: Optional[str] = None
        self.tahun_map: Dict[int, int] = {}  # {2026: 8, 2025: 7, ...}
        self._load_cached_token()

    def _load_cached_token(self):
        """Membaca token dan identitas akun dari cache."""
        if CACHE_TOKEN_FILE.exists():
            try:
                with open(CACHE_TOKEN_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Data identitas pegawai bersifat permanen per akun
                    self.pegawai_id = data.get("pegawai_id")
                    self.nip_lama = data.get("nip_lama")
                    self.nama = data.get("nama")
                    self.tahun_map = {int(k): v for k, v in data.get("tahun_map", {}).items()}
                    
                    cached_time = data.get("timestamp", 0)
                    if time.time() - cached_time < 8 * 3600:
                        self.auth_token = data.get("token")
            except Exception:
                pass

    def _save_cached_token(self):
        """Menyimpan token dan info sesi ke cache."""
        try:
            CACHE_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_TOKEN_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "token": self.auth_token,
                    "pegawai_id": self.pegawai_id,
                    "nip_lama": self.nip_lama,
                    "nama": self.nama,
                    "tahun_map": self.tahun_map,
                    "timestamp": time.time()
                }, f, indent=2)
        except Exception:
            pass

    def get_token(self, force_refresh: bool = False) -> str:
        """
        Mendapatkan token x-auth. Jika belum ada atau force_refresh=True,
        buka browser headless sebentar untuk menangkap token sesi SSO aktif.
        """
        if self.auth_token and not force_refresh:
            return self.auth_token

        print("[API] Mengekstrak token sesi KIPApp dari profil browser...")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                ctx = p.chromium.launch_persistent_context(
                    user_data_dir=self.browser_data,
                    headless=True
                )
                page = ctx.new_page()

                captured_token = None
                def on_req(r):
                    nonlocal captured_token
                    if "x-auth" in r.headers:
                        captured_token = r.headers["x-auth"]

                page.on("request", on_req)
                page.goto("https://kipapp.bps.go.id/#/pelaksanaan-aksi", wait_until="commit")
                time.sleep(3)

                ctx.close()

                if captured_token:
                    self.auth_token = captured_token
                    self._extract_nip_from_jwt()
                    self._save_cached_token()
                    print("[API] Token sesi berhasil diperbarui.")
                    return self.auth_token
                else:
                    raise ValueError("Gagal menangkap header x-auth. Pastikan profil browser telah login SSO BPS.")
        except Exception as e:
            raise RuntimeError(f"Gagal mengambil token sesi KIPApp: {e}")

    def _extract_nip_from_jwt(self):
        """Mengekstrak NIP lama dari payload token JWT."""
        if not self.auth_token:
            return
        try:
            raw_jwt = self.auth_token.replace("Bearer ", "").strip()
            parts = raw_jwt.split(".")
            if len(parts) >= 2:
                payload_b64 = parts[1]
                payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
                payload = json.loads(base64.urlsafe_b64decode(payload_b64))
                self.nip_lama = payload.get("nip") or payload.get("nip-lama")
        except Exception:
            pass

    def request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, retry: bool = True) -> Any:
        """Mengirim HTTP request langsung ke KIPApp REST API."""
        token = self.get_token()
        url = f"{BASE_URL}/{endpoint.lstrip('/')}"
        headers = {
            "x-auth": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        body_bytes = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method.upper())

        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                resp_text = res.read().decode("utf-8")
                try:
                    return json.loads(resp_text)
                except Exception:
                    return resp_text
        except urllib.error.HTTPError as e:
            resp_body = e.read().decode("utf-8", errors="ignore")
            # Jika 401 atau token kedaluwarsa, coba refresh token sekali
            if e.code in [401, 403] and retry:
                print("[API] Token kedaluwarsa, melakukan refresh sesi otomatis...")
                self.get_token(force_refresh=True)
                return self.request(method, endpoint, data=data, retry=False)
            raise RuntimeError(f"HTTP Error {e.code} pada {url}: {resp_body}")
        except Exception as e:
            raise RuntimeError(f"Koneksi gagal ke {url}: {e}")

    def get_pegawai_id(self) -> str:
        """Mendapatkan pegawaiid aktif pengguna."""
        if self.pegawai_id:
            return self.pegawai_id

        # Pastikan token telah tersedia
        self.get_token()

        if not self.nip_lama:
            self._extract_nip_from_jwt()

        if self.nip_lama:
            pegawai_list = self.request("GET", f"pegawai?niplama={self.nip_lama}")
            if isinstance(pegawai_list, list) and pegawai_list:
                # Ambil penempatan aktif paling mutakhir (item terakhir)
                active = pegawai_list[-1]
                self.pegawai_id = str(active.get("id"))
                self.nama = active.get("nama")
                self._save_cached_token()
                return self.pegawai_id

        raise RuntimeError("Gagal menentukan pegawai_id dari sesi akun.")

    def get_tahun_id(self, tahun: int = 2026) -> int:
        """Mengonversi angka tahun anggaran menjadi tahun ID KIPApp (misal 2026 -> 8)."""
        if tahun in self.tahun_map:
            return self.tahun_map[tahun]

        tahun_list = self.request("GET", "tahun?jenis=2")
        if isinstance(tahun_list, list):
            for t in tahun_list:
                th_val = t.get("tahunawal")
                th_id = t.get("id")
                if th_val and th_id:
                    self.tahun_map[int(th_val)] = int(th_id)
            self._save_cached_token()

        return self.tahun_map.get(tahun, 8)

    # ==========================================
    # RESOURCE METHODS (SKP, RK, IKI, KEGIATAN)
    # ==========================================

    def get_skp_list(self, tahun: int = 2026) -> List[Dict[str, Any]]:
        """Mengambil seluruh daftar SKP pengguna pada tahun anggaran target."""
        pegawai_id = self.get_pegawai_id()
        tahun_id = self.get_tahun_id(tahun)
        res = self.request("GET", f"skp?periodeid={tahun_id}&pegawaiid={pegawai_id}&jenis=2")
        return res if isinstance(res, list) else []

    def get_skp_by_periode(self, periode_keyword: str, tahun: int = 2026) -> Optional[Dict[str, Any]]:
        """Mencari objek SKP berdasarkan kata kunci periode (misal: 'Triwulan III', 'TW 2', 'Tahunan')."""
        norm = normalize_periode(periode_keyword).lower()
        skps = self.get_skp_list(tahun=tahun)

        target_period_id = None
        if re.search(r'\b(tw|triwulan)?\s*(iv|4)\b', norm):
            target_period_id = 4
        elif re.search(r'\b(tw|triwulan)?\s*(iii|3)\b', norm):
            target_period_id = 3
        elif re.search(r'\b(tw|triwulan)?\s*(ii|2)\b', norm):
            target_period_id = 2
        elif re.search(r'\b(tw|triwulan)?\s*(i|1)\b', norm):
            target_period_id = 1

        for s in skps:
            pid = s.get("periodepenilaianid")
            ket = str(s.get("keteranganperiodepenilaian", "")).lower()
            if target_period_id is not None and pid == target_period_id:
                return s
            if norm in ket or norm in str(s.get("deskperiodeawal", "")).lower():
                return s

        return None

    def get_rencana_kinerja(self, skpid: str) -> List[Dict[str, Any]]:
        """Mengambil daftar Rencana Kinerja (RK) aktif pada suatu SKP."""
        res = self.request("GET", f"skp/rk?skpid={skpid}&direct=1")
        return res if isinstance(res, list) else []

    def match_rk(self, skpid: str, keyword: str) -> Optional[Dict[str, Any]]:
        """Mencocokkan keyword dengan butir Rencana Kinerja terbaik."""
        rks = self.get_rencana_kinerja(skpid)
        if not rks:
            return None
        kw = keyword.lower().strip()
        for item in rks:
            text = (item.get("rencanakinerja") or item.get("rk") or "").lower()
            if kw in text:
                return item
        words = kw.split()
        for item in rks:
            text = (item.get("rencanakinerja") or item.get("rk") or "").lower()
            if any(w in text for w in words if len(w) > 3):
                return item
        return rks[0]

    def get_kegiatan_list(self, skpid: str) -> List[Dict[str, Any]]:
        """Mengambil seluruh catatan kegiatan pada suatu SKP secara instan."""
        res = self.request("GET", f"kegiatan?skpid={skpid}")
        return res if isinstance(res, list) else []

    def create_kegiatan(
        self,
        skpid: str,
        rkid: str,
        kegiatan: str,
        tanggal: str,
        capaian: Optional[str] = None,
        progres: int = 100,
        datadukung: str = "",
        iscapaianskp: int = 1,
        tanggalselesai: Optional[str] = None,
        jammulai: Optional[str] = None,
        jamselesai: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Membuat kegiatan baru secara instan via REST API (POST /api/v1/kegiatan).
        Opsi iscapaianskp selalu bernilai 1 (checked) secara default.
        """
        payload = {
            "skpid": str(skpid),
            "rkid": str(rkid),
            "kegiatan": kegiatan,
            "tanggal": tanggal,
            "tanggalselesai": tanggalselesai,
            "progres": int(progres),
            "jammulai": jammulai,
            "jamselesai": jamselesai,
            "capaian": capaian if capaian else kegiatan,
            "datadukung": datadukung if datadukung else "",
            "iscapaianskp": int(iscapaianskp)
        }
        res = self.request("POST", "kegiatan", data=payload)
        return res if isinstance(res, dict) else {"status": True, "raw": res}

    def update_kegiatan(
        self,
        kegiatan_id: str,
        skpid: str,
        rkid: str,
        kegiatan: str,
        tanggal: str,
        capaian: Optional[str] = None,
        progres: int = 100,
        datadukung: str = "",
        iscapaianskp: int = 1,
        tanggalselesai: Optional[str] = None,
        jammulai: Optional[str] = None,
        jamselesai: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Memperbarui data kegiatan yang ada via REST API (PUT /api/v1/kegiatan).
        """
        payload = {
            "id": str(kegiatan_id),
            "skpid": str(skpid),
            "rkid": str(rkid),
            "kegiatan": kegiatan,
            "tanggal": tanggal,
            "tanggalselesai": tanggalselesai,
            "progres": int(progres),
            "jammulai": jammulai,
            "jamselesai": jamselesai,
            "capaian": capaian if capaian else kegiatan,
            "datadukung": datadukung if datadukung else "",
            "iscapaianskp": int(iscapaianskp)
        }
        res = self.request("PUT", "kegiatan", data=payload)
        return res if isinstance(res, dict) else {"status": True, "raw": res}

    def delete_kegiatan(self, kegiatan_id: str) -> Dict[str, Any]:
        """Menghapus kegiatan via REST API (DELETE /api/v1/kegiatan)."""
        res = self.request("DELETE", "kegiatan", data={"id": str(kegiatan_id)})
        return res if isinstance(res, dict) else {"status": True, "raw": res}

    def update_all_checklists(self, skpid: str) -> Tuple[int, int]:
        """
        Mencentang capaian SKP (iscapaianskp = 1) pada seluruh kegiatan
        dalam satu SKP secara massal.
        """
        kegs = self.get_kegiatan_list(skpid)
        updated = 0
        already = 0
        for k in kegs:
            if k.get("iscapaianskp") == 1:
                already += 1
                continue

            kid = k.get("kegiatanperhariid") or k.get("id")
            res = self.update_kegiatan(
                kegiatan_id=str(kid),
                skpid=str(skpid),
                rkid=str(k.get("rkid")),
                kegiatan=k.get("kegiatan"),
                tanggal=k.get("tanggal"),
                capaian=k.get("capaian"),
                progres=k.get("progres", 100),
                datadukung=k.get("datadukung") or "",
                iscapaianskp=1,
                tanggalselesai=k.get("tanggalselesai")
            )
            if res.get("status"):
                updated += 1
            time.sleep(0.05)
        return updated, already


# ==========================================
# CLI ENTRY POINT
# ==========================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="KIPApp BPS REST API CLI Client")
    parser.add_argument("--list-skp", action="store_true", help="Tampilkan daftar seluruh SKP aktif dan statusnya")
    parser.add_argument("--list-rk", action="store_true", help="Tampilkan butir Rencana Kinerja (SKP)")
    parser.add_argument("--list-kegiatan", action="store_true", help="Tampilkan seluruh kegiatan pada periode target")
    parser.add_argument("--periode", "-p", default="Triwulan III", help="Periode SKP target (default: Triwulan III)")
    parser.add_argument("--tahun", "-t", type=int, default=2026, help="Tahun anggaran/SKP (default: 2026)")
    parser.add_argument("--update-checklists", action="store_true", help="Centang capaian SKP pada seluruh kegiatan")
    parser.add_argument("--browser-data", default="", help="Path folder browser_data kustom")

    args = parser.parse_args()
    api = KipappAPI(browser_data=args.browser_data)

    if args.list_skp:
        print("\n" + "=" * 65)
        print(f"DAFTAR SKP PEGAWAI DI KIPAPP BPS (Tahun {args.tahun})")
        print("=" * 65)
        skps = api.get_skp_list(tahun=args.tahun)
        for s in skps:
            periode_label = f"Triwulan {s.get('keteranganperiodepenilaian')} ({s.get('deskperiodeawal')} - {s.get('deskperiodeakhir')})"
            print(f"ID: {s.get('id')} | Periode: {periode_label:<32} | Status: {s.get('statusskp')}")
        return

    skp = api.get_skp_by_periode(args.periode, tahun=args.tahun)
    if not skp:
        print(f"[ERROR] SKP periode '{args.periode}' tahun {args.tahun} tidak ditemukan.")
        return

    skpid = str(skp.get("id"))
    periode_label = f"Triwulan {skp.get('keteranganperiodepenilaian')} ({skp.get('deskperiodeawal')} - {skp.get('deskperiodeakhir')})"
    print(f"\nSKP Terpilih: {periode_label} (ID: {skpid}, Status: {skp.get('statusskp')})")

    if args.list_rk:
        print("\n" + "=" * 65)
        print(f"DAFTAR RENCANA KINERJA (SKP ID: {skpid})")
        print("=" * 65)
        rks = api.get_rencana_kinerja(skpid)
        for i, r in enumerate(rks, 1):
            print(f"{i}. [ID: {r.get('rkid') or r.get('id')}] {r.get('rencanakinerja')}")
        return

    if args.list_kegiatan:
        print("\n" + "=" * 65)
        print(f"DAFTAR KEGIATAN (SKP ID: {skpid})")
        print("=" * 65)
        kegs = api.get_kegiatan_list(skpid)
        print(f"Total kegiatan: {len(kegs)}")
        for i, k in enumerate(kegs, 1):
            status_skp = "✅ Centang" if k.get("iscapaianskp") == 1 else "❌ Belum Centang"
            bukti = "Ada Bukti" if k.get("datadukung") else "Tanpa Bukti"
            print(f"{i}. [{k.get('tanggal')}] ({status_skp}, {bukti}) {k.get('kegiatan')[:60]}...")
        return

    if args.update_checklists:
        print(f"\nMemperbarui seluruh checklist capaian SKP pada {periode_label}...")
        updated, already = api.update_all_checklists(skpid)
        print(f"Selesai! {updated} baru dicentang, {already} sudah tercentang sebelumnya.")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
