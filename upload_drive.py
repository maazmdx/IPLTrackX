from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload

# Path to service account JSON
SERVICE_ACCOUNT_FILE = "data/service_account.json"

# Your Google Drive Folder ID (Posts folder)
FOLDER_ID = "130zHH0Khnlbz6ki3F3b_NQTjMy64s8cF"

# File to upload
FILE_PATH = "output/test_post.png"
FILE_NAME = "test_post.png"

# Authenticate
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/drive"]
)

drive_service = build("drive", "v3", credentials=credentials)

# Upload file
file_metadata = {
    "name": FILE_NAME,
    "parents": [FOLDER_ID]
}

media = MediaFileUpload(FILE_PATH, mimetype="image/png")

file = drive_service.files().create(
    body=file_metadata,
    media_body=media,
    fields="id",
    supportsAllDrives=True
).execute()


print("SUCCESS: File uploaded to Google Drive. File ID:", file.get("id"))
