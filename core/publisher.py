import os
import sys
import time
import socket
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# --- CONFIGURATION ---
socket.setdefaulttimeout(600)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
FINAL_IMAGE = os.path.join(BASE_DIR, "final_post.jpg")
FINAL_CAPTION = os.path.join(BASE_DIR, "final_caption.txt")

# AUTH FILES
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")

# 🔴 YOUR MAIN FOLDER ID (Do not change this) 🔴
MAIN_FOLDER_ID = "1R-wX0mAaYbZHoygVmnX97ttPiZwt156Z"

def authenticate_drive():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, ['https://www.googleapis.com/auth/drive.file'])
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('drive', 'v3', credentials=creds)

def upload_to_drive():
    print(f"🔍 PUBLISHER: Preparing Upload to Main Folder...")
    
    if not os.path.exists(FINAL_IMAGE):
        print("❌ Publisher Error: Final image not found.")
        return True 

    for attempt in range(1, 4):
        try:
            print(f"--- ☁️ CLOUD UPLOADER (Attempt {attempt}/3) ---")
            service = authenticate_drive()
            if not service: return False

            # Generate Timestamp
            date_str = datetime.now().strftime("%d-%b")
            time_str = datetime.now().strftime("%H-%M")
            
            # 1. Upload IMAGE
            img_name = f"{date_str}_Post-{time_str}.jpg"
            media_img = MediaFileUpload(FINAL_IMAGE, mimetype='image/jpeg', resumable=True)
            service.files().create(
                body={'name': img_name, 'parents': [MAIN_FOLDER_ID]}, 
                media_body=media_img
            ).execute()
            print(f"✅ Image Uploaded: {img_name}")

            # 2. Upload CAPTION
            if os.path.exists(FINAL_CAPTION):
                txt_name = f"{date_str}_Caption-{time_str}.txt"
                media_txt = MediaFileUpload(FINAL_CAPTION, mimetype='text/plain', resumable=True)
                service.files().create(
                    body={'name': txt_name, 'parents': [MAIN_FOLDER_ID]}, 
                    media_body=media_txt
                ).execute()
                print(f"✅ Caption Uploaded: {txt_name}")
            
            return True

        except Exception as e:
            if "storageQuotaExceeded" in str(e): return True 
            print(f"⚠️ Upload Failed: {e}")
            time.sleep(10)

    return False

if __name__ == "__main__":
    if upload_to_drive(): sys.exit(0)
    else: sys.exit(1)
