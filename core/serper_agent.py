import os
import sys
import json
import requests
import io
from PIL import Image

# --- CONFIGURATION ---
# 🔴 PASTE YOUR SERPER KEY HERE 🔴
SERPER_API_KEY = "49a2a86b4c1d082a0beb0d17ab10fc8dd6997cfa"

# FIXED: Removed the typo 'l__file__' -> '__file__'
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")
NEWS_IMAGE = os.path.join(TEMP_DIR, "news_image.jpg")

BAD_DOMAINS = ["instagram", "facebook", "twitter", "youtube", "tiktok", "vector", "freepik", "dreamstime", "alamy"]

def download_image(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and len(resp.content) > 30000: # Min 30KB
            try:
                img_test = Image.open(io.BytesIO(resp.content))
                img_test.verify()
            except: return False

            with open(NEWS_IMAGE, 'wb') as f:
                f.write(resp.content)
            return True
    except:
        return False
    return False

def execute_search(query):
    print(f"🔎 SERPER: Searching for -> '{query}'")
    url = "https://google.serper.dev/images"
    payload = json.dumps({"q": query, "gl": "in", "num": 10})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=payload)
        results = response.json()
        
        if 'images' not in results: return False

        for item in results['images']:
            img_url = item.get('imageUrl')
            if any(x in img_url.lower() for x in BAD_DOMAINS): continue
            
            print(f"   ⬇️ Downloading from {item.get('source')}...")
            if download_image(img_url):
                print(f"✅ SERPER SUCCESS: Secured valid image.")
                return True
        return False
    except Exception as e:
        print(f"⚠️ Search Error: {e}")
        return False

def search_visuals():
    print("🔎 SERPER: Initializing High-Res Search...")
    
    if os.path.exists(NEWS_IMAGE): os.remove(NEWS_IMAGE)
    if not os.path.exists(NEWS_DATA): return False
    
    with open(NEWS_DATA, 'r') as f: data = json.load(f)
    
    base_query = data.get('visual_prompt', data['title'])
    
    # STRATEGY 1: ACTION SHOT
    query_1 = f"{base_query} match action real photo high res -logo -vector"
    if execute_search(query_1): return True
    
    print("⚠️ Action shot not found. Switching to Backup Strategy...")

    # STRATEGY 2: TEAM LOGO
    team_name = " ".join(base_query.split()[:3]) 
    query_2 = f"{team_name} cricket team official logo high res wallpaper"
    if execute_search(query_2): return True

    # STRATEGY 3: FLAG / GENERIC
    query_3 = f"{team_name} cricket flag wallpaper"
    if execute_search(query_3): return True

    print("❌ All visual strategies failed.")
    return False

if __name__ == "__main__":
    if search_visuals(): sys.exit(0)
    else: sys.exit(1)
