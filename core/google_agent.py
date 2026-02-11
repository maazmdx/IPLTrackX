import os
import requests
from googleapiclient.discovery import build
from PIL import Image
import io
import sys

# --- CONFIGURATION ---
GOOGLE_API_KEY = "AIzaSyBMsDM7M8BxmrS216fcMIYz68iwS74ZFws"  # <--- MAKE SURE THIS IS FILLED
SEARCH_CX = "35360f9b6cce948c8"

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
NEWS_IMAGE_FILE = os.path.join(TEMP_DIR, "news_image.jpg")
CUTOUT_FILE = os.path.join(TEMP_DIR, "player_cutout.png")

# --- 1. GOOGLE SEARCH (STRICT MODE) ---
def google_search_image(query):
    print(f"☁️ GOOGLE: Searching for '{query}'...")
    
    if "PASTE_YOUR" in GOOGLE_API_KEY:
        print("\n🛑 CRITICAL ERROR: API Key Missing in core/google_agent.py")
        return False

    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        
        # 2. The Search Request
        res = service.cse().list(
            q=query,
            cx=SEARCH_CX,
            searchType="image",
            imgSize="XXLARGE",  # <--- FIXED: UPDATED TO 'XXLARGE' (High Res)
            fileType="jpg",
            num=5,
            safe="off"
        ).execute()

        if 'items' not in res:
            print("❌ Google Search returned 0 results.")
            return False

        for item in res['items']:
            img_url = item['link']
            print(f"   🔍 Analyzing: {img_url[:50]}...")
            
            # 3. Anti-Stock Filter
            if any(x in img_url.lower() for x in ["freepik", "shutterstock", "istock", "vector", "clipart"]):
                print("      🚫 Stock Photo Detected. Skipping.")
                continue

            # 4. Download & Verify
            try:
                resp = requests.get(img_url, timeout=10)
                if resp.status_code == 200:
                    image_data = resp.content
                    
                    # 5. Resolution Check
                    img = Image.open(io.BytesIO(image_data))
                    w, h = img.size
                    if w < 1200: 
                        print(f"      ⚠️ Too small ({w}x{h}). Needs 1200+. Skipping.")
                        continue
                    
                    # Save
                    with open(NEWS_IMAGE_FILE, 'wb') as f:
                        f.write(image_data)
                    print(f"✅ SECURED HIGH-RES IMAGE: {w}x{h}")
                    return True
            except Exception as e:
                print(f"      ⚠️ Download failed: {e}")
                continue
        
        print("❌ No suitable images found after filtering.")
        return False

    except Exception as e:
        print(f"❌ GOOGLE API ERROR: {e}")
        return False

# --- 2. BACKGROUND REMOVAL ---
def google_remove_background():
    print("☁️ PROCESSING: Context Awareness (Background Removal)...")
    from rembg import remove
    try:
        if not os.path.exists(NEWS_IMAGE_FILE): return False
        inp = Image.open(NEWS_IMAGE_FILE)
        out = remove(inp)
        out.save(CUTOUT_FILE)
        print("✅ Background Removed.")
        return True
    except Exception as e:
        print(f"⚠️ BG Removal Error: {e}")
        return False

# --- 3. UPSCALER ---
def google_upscale_image():
    print("☁️ PROCESSING: High-Fidelity Upscaling...")
    try:
        if not os.path.exists(NEWS_IMAGE_FILE): return False
        img = Image.open(NEWS_IMAGE_FILE)
        w, h = img.size
        
        if w < 3000:
            target_w = 3000
            ratio = target_w / w
            target_h = int(h * ratio)
            new_img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            new_img.save(NEWS_IMAGE_FILE)
            print(f"✅ Enhanced to 4K Standards: {target_w}x{target_h}")
        else:
            print("✅ Image is already Ultra-HD.")
        return True
    except Exception as e:
        print(f"⚠️ Upscale Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "search"
    success = False

    if cmd == "search": success = google_search_image("India vs Pakistan cricket match real photo")
    elif cmd == "bg_remove": success = google_remove_background()
    elif cmd == "upscale": success = google_upscale_image()
    
    # CRITICAL: Exit with error code if failed. This stops main.py from proceeding.
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
