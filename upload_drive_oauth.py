from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# OAuth credentials file
CLIENT_SECRET_FILE = 'data/oauth.json'

# Folder ID (Posts folder)
FOLDER_ID = '130zHH0Khnlbz6ki3F3b_NQTjMy64s8cF'

# File to upload
FILE_PATH = 'output/test_post.png'
FILE_NAME = 'test_post.png'

# Authenticate via browser (first time only)
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
creds = flow.run_local_server(port=0)

drive_service = build('drive', 'v3', credentials=creds)

file_metadata = {
    'name': FILE_NAME,
    'parents': [FOLDER_ID]
}

media = MediaFileUpload(FILE_PATH, mimetype='image/png')

file = drive_service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

print("SUCCESS: Uploaded with OAuth. File ID:", file.get('id'))
