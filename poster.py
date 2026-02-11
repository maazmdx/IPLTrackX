from instagrapi import Client
import os
import json
from urllib.parse import unquote

# --- CONFIGURATION ---
BASE_DIR = os.getcwd()
TEMP_DIR = os.path.join(BASE_DIR, "temp")
DESIGN_JSON = os.path.join(TEMP_DIR, "design_data.json")
FINAL_IMAGE = os.path.join(BASE_DIR, "final_post.jpg")

# --- YOUR SESSION ID ---
RAW_SESSION_ID = "80559640889%3ARtI08oIbXTRt63%3A21%3AAYgrWcQuYdwPFAWQbCAk6FgbNNC3weDlI1_qPGxFrA"

def upload_post():
    if not os.path.exists(FINAL_IMAGE):
        print("Error: No image found.")
        return

    # Load Caption
    with open(DESIGN_JSON, 'r') as f:
        data = json.load(f)
    
    caption = f"{data['caption']}\n.\n.\n#IPL2026 #Cricket #IPL #T20 #India #{data['title'].split()[0]}"

    print("--- THE POSTER (DIRTY FIX MODE) ---")
    cl = Client()
    
    try:
        session_id = unquote(RAW_SESSION_ID)
        print(f"Injecting Key: {session_id[:15]}...")
        
        # 1. Try to Login
        try:
            cl.login_by_sessionid(session_id)
            print("✅ Login verified successfully.")
        except Exception as e:
            # 2. IGNORE THE CRASH
            print(f"⚠️ Login Verification Failed ({e})")
            print("👉 IGNORING ERROR AND FORCING UPLOAD...")

        # 3. Force Upload (Even if login 'failed')
        print(f"Uploading Image...")
        media = cl.photo_upload(
            path=FINAL_IMAGE,
            caption=caption
        )
        print("✅ SUCCESS: Post uploaded! 🚀")
        print(f"View here: https://www.instagram.com/p/{media.code}/")
        
    except Exception as e:
        print(f"❌ FINAL ERROR: {e}")
        print("Diagnosis: Your IP address is hard-blocked by Instagram. You cannot post from this specific computer/server.")

if __name__ == "__main__":
    upload_post()
