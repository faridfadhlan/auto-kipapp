import os
import mimetypes
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

def find_credentials_file() -> tuple[str, str]:
    """
    Mencari file kredensial Google Drive (Service Account atau OAuth Client)
    Mengembalikan tuple: (tipe, path_file)
    """
    # 1. Cek Service Account dari Environment Variable
    sa_env = os.getenv("GDRIVE_SERVICE_ACCOUNT_FILE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if sa_env and Path(sa_env).expanduser().exists():
        return "service_account", str(Path(sa_env).expanduser().resolve())

    # 2. Cek file service_account.json di folder project aktif atau ~/.kipapp/
    candidate_sa = [
        Path.cwd() / "service_account.json",
        Path.home() / ".kipapp" / "service_account.json",
        Path(__file__).parent / "service_account.json"
    ]
    for c in candidate_sa:
        if c.exists():
            return "service_account", str(c.resolve())

    # 3. Cek OAuth2 Client Credentials
    oauth_env = os.getenv("GDRIVE_OAUTH_CLIENT_FILE")
    if oauth_env and Path(oauth_env).expanduser().exists():
        return "oauth", str(Path(oauth_env).expanduser().resolve())

    candidate_oauth = [
        Path.cwd() / "credentials.json",
        Path.cwd() / "client_secrets.json",
        Path.home() / ".kipapp" / "credentials.json",
        Path(__file__).parent / "credentials.json"
    ]
    for c in candidate_oauth:
        if c.exists():
            return "oauth", str(c.resolve())

    return "", ""

def get_drive_service():
    """
    Inisialisasi dan mengembalikan Google Drive API service client
    """
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    cred_type, cred_path = find_credentials_file()

    # Opsi 1: Google Service Account (Rekomendasi Utama: tanpa popup browser)
    if cred_type == "service_account":
        creds = service_account.Credentials.from_service_account_file(
            cred_path, scopes=SCOPES
        )
        return build("drive", "v3", credentials=creds)

    # Opsi 2: Google OAuth 2.0 User Credentials
    elif cred_type == "oauth":
        token_path = Path.cwd() / "token.json"
        if not token_path.exists():
            token_path = Path.home() / ".kipapp" / "token.json"

        creds = None
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Simpan token
            save_dest = Path.cwd() / "token.json"
            with open(save_dest, "w") as token_file:
                token_file.write(creds.to_json())

        return build("drive", "v3", credentials=creds)

    else:
        raise FileNotFoundError(
            "Tidak ditemukan kredensial Google Drive!\n"
            "Silakan taruh file 'service_account.json' atau 'credentials.json' di direktori project,\n"
            "atau set environment variable GOOGLE_APPLICATION_CREDENTIALS / GDRIVE_SERVICE_ACCOUNT_FILE di .env."
        )

def upload_file_to_drive(file_path: str | Path, folder_id: str = "", make_public: bool = True) -> str:
    """
    Mengupload file ke Google Drive dan mengembalikan link publik (webViewLink).
    Jika input file_path sudah berupa URL (http/https), langsung dikembalikan apa adanya.
    """
    path_str = str(file_path).strip()
    if not path_str:
        return ""

    # Jika sudah berupa URL web / Google Drive, langsung return
    if path_str.startswith("http://") or path_str.startswith("https://"):
        return path_str

    target_file = Path(path_str).expanduser()
    if not target_file.exists():
        # Cek relatif terhadap direktori project
        target_file = Path.cwd() / path_str
        if not target_file.exists():
            print(f"[WARNING] File bukti dukung '{path_str}' tidak ditemukan di lokal. Menggunakan teks aslinya.")
            return path_str

    target_file = target_file.resolve()
    print(f"\n[GDrive] Mengupload bukti dukung: {target_file.name}...")

    # Folder ID dari parameter atau .env
    target_folder = folder_id or os.getenv("GDRIVE_FOLDER_ID", "").strip()

    from googleapiclient.http import MediaFileUpload
    service = get_drive_service()

    mime_type, _ = mimetypes.guess_type(str(target_file))
    if not mime_type:
        mime_type = "application/octet-stream"

    file_metadata = {"name": target_file.name}
    if target_folder:
        file_metadata["parents"] = [target_folder]

    media = MediaFileUpload(str(target_file), mimetype=mime_type, resumable=True)

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink, webContentLink"
    ).execute()

    file_id = uploaded.get("id")
    web_link = uploaded.get("webViewLink") or f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"

    # Set permission agar bisa dilihat siapa saja yang memiliki link (misal penilai SKP)
    if make_public and file_id:
        try:
            service.permissions().create(
                fileId=file_id,
                body={"type": "anyone", "role": "reader"}
            ).execute()
        except Exception as perm_err:
            print(f"[WARNING] Gagal mengubah permission file Drive menjadi publik: {perm_err}")

    print(f"[GDrive] Upload berhasil! Link: {web_link}")
    return web_link

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Penggunaan: python gdrive_uploader.py <path_file> [folder_id]")
        sys.exit(1)

    fpath = sys.argv[1]
    fid = sys.argv[2] if len(sys.argv) > 2 else ""
    try:
        url = upload_file_to_drive(fpath, folder_id=fid)
        print(f"\nLink Siap Pakai: {url}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
