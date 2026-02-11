import os
import json
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from rembg import remove
from duckduckgo_search import DDGS
import requests

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")
NEWS_IMAGE_FILE = os.path.join(TEMP_DIR, "news_image.jpg")
CUTOUT_IMAGE_FILE = os.path.join(TEMP_DIR, "player_cutout.png")

# Context Keywords
CONTEXT_RULES = {
    "IPL": ["IPL", "CSK", "RCB", "MI", "KKR", "Auction", "Franchise"],
    "TEST": ["Test Match", "Red Ball", "WTC", "Border Gavaskar"],
    "ODI": ["ODI", "World Cup", "50 over", "Champions Trophy"],
    "T20": ["T20", "T20I", "Suryakumar", "Hardik", "Rinku"]
}

def detect_context(title):
    title = title.upper()
    for ctx, keywords in CONTEXT_RULES.items():
        if any(k.upper() in title for k in keywords):
            return ctx
    return "GENERIC"

def verify_and_correct_image(current_image_path, context, player_name):
    """
    Checks if we need to re-download a better jersey match.
    (Simple logic: If context is specific, force a specific search)
    """
    if context == "GENERIC" or not player_name:
        return True
        
    print(f"🧩 CONTEXT PROCESSOR: Verifying {player_name} in {context} kit...")
    
    # Construct strict search query
    if context == "IPL":
        query = f"{player_name} IPL jersey match photo hd"
    elif context == "TEST":
        query = f"{player_name} test match white jersey photo hd"
    elif context == "ODI":
        query = f"{player_name} india blue odi jersey photo hd"
    else:
        query = f"{player_name} cricket jersey photo hd"

    # We perform a "Force Search" to overwrite the generic Hunter image
    # This ensures we get the right kit even if Hunter got a generic one
    try:
        print(f"🔄 RE-FETCHING: {query}")
        with DDGS() as ddgs:
            results = ddgs.images(query, max_results=5, safesearch="off")
            for res in results:
                img_url = res.get('image')
                if not img_url: continue
                try:
                    response = requests.get(img_url, timeout=10)
                    if response.status_code == 200:
                        with open(NEWS_IMAGE_FILE, 'wb') as f:
                            f.write(response.content)
                        print("✅ Context-Correct Image Secured.")
                        return True
                except: continue
    except Exception as e:
        print(f"⚠️ Re-fetch failed: {e}. Keeping original.")
    
    return True

def process_image():
    if not os.path.exists(NEWS_DATA_FILE): return
    if not os.path.exists(NEWS_IMAGE_FILE): return

    with open(NEWS_DATA_FILE, 'r') as f: data = json.load(f)
    
    title = data.get('title', '')
    player = data.get('player', '')
    
    # 1. Detect Context
    context = detect_context(title)
    data['context'] = context
    
    # 2. Verify Jersey (Re-download if needed)
    verify_and_correct_image(NEWS_IMAGE_FILE, context, player)
    
    # 3. Background Removal (Subject Isolation)
    print("✂️  Removing Background (rembg)...")
    try:
        input_image = Image.open(NEWS_IMAGE_FILE).convert("RGB")
        
        # Pre-enhance before removal for better edge detection
        enhancer = ImageEnhance.Contrast(input_image)
        input_image = enhancer.enhance(1.2)
        
        output_image = remove(input_image)
        output_image.save(CUTOUT_IMAGE_FILE)
        print("✅ Cutout Saved: temp/player_cutout.png")
        data['has_cutout'] = True
    except Exception as e:
        print(f"⚠️ Background Removal Failed: {e}")
        data['has_cutout'] = False

    # Save updated context data
    with open(NEWS_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    process_image()
