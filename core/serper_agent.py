import os
import sys
import json
import requests
import io
from PIL import Image

# --- CONFIGURATION ---
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "PASTE_YOUR_KEY_HERE_IF_LOCAL")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")

# We now support 2 images
IMG_1 = os.path.join(TEMP_DIR, "news_image_1.jpg")
IMG_2 = os.path.join(TEMP_DIR, "news_image_2.jpg")

BAD_DOMAINS = ["vector", "freepik", "dreamstime", "alamy", "stock", "getty", "icon"]

def download_image(url, save_path):
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200 and len(resp.content) > 30000:
            try:
                img = Image.open(io.BytesIO(resp.content))
                img.verify()
                with open(save_path, 'wb') as f: f.write(resp.content)
                return True
            except: return False
    except: return False
    return False

def execute_search(query, num_results=5):
    print(f"🔎 SERPER: Searching -> '{query}'")
    url = "https://google.serper.dev/images"
    payload = json.dumps({"q": query, "gl": "in", "num": num_results})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}

    try:
        resp = requests.post(url, headers=headers, data=payload).json()
        return [item['imageUrl'] for item in resp.get('images', []) 
                if not any(x in item['imageUrl'].lower() for x in BAD_DOMAINS)]
    except: return []

def search_visuals():
    if os.path.exists(IMG_1): os.remove(IMG_1)
    if os.path.exists(IMG_2): os.remove(IMG_2)
    
    with open(NEWS_DATA, 'r') as f: data = json.load(f)
    title = data.get('title', '').lower()
    
    # STRATEGY: DUAL IMAGE DETECTION
    # If "vs" or "beat" or "won" is in title, try to get 2 images
    teams = []
    
    # Simple extraction logic (You can expand this list)
    known_teams = ["india", "pakistan", "australia", "england", "rcb", "csk", "mi", "kkr", "srh", "gt", "lsg", "rr", "pbks", "dc"]
    for t in known_teams:
        if t in title: teams.append(t)
    
    # SCENARIO A: Two Teams Found (Split Screen)
    if len(teams) >= 2:
        print(f"⚔️ Dual-Mode Triggered: {teams[0]} vs {teams[1]}")
        
        # Image 1 (Team A)
        urls_1 = execute_search(f"{teams[0]} cricket captain match action real photo")
        for url in urls_1:
            if download_image(url, IMG_1): break
            
        # Image 2 (Team B)
        urls_2 = execute_search(f"{teams[1]} cricket captain match action real photo")
        for url in urls_2:
            if download_image(url, IMG_2): break
            
    # SCENARIO B: Single Topic (Hero Image)
    else:
        print("👤 Single-Mode Triggered")
        query = data.get('visual_prompt', title) + " real photo high res"
        urls = execute_search(query, 10)
        
        # Try to download at least one good one
        for url in urls:
            if download_image(url, IMG_1): 
                print("✅ Image 1 Secured.")
                break
        
        # Optional: Try to get a second contextual image (Stadium/Crowd) just in case
        if os.path.exists(IMG_1):
            urls_bg = execute_search(query + " stadium atmosphere wide shot")
            for url in urls_bg:
                # Ensure we don't download the exact same image
                if url != urls[0]: 
                    if download_image(url, IMG_2): break

if __name__ == "__main__":
    search_visuals()
    sys.exit(0)
