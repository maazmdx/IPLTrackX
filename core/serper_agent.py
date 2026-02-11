import os
import sys
import json
import requests
import io
import re
from PIL import Image, ImageStat

# ================= CONFIG =================
SERPER_API_KEY = os.environ.get("SERPER_API_KEY", "PASTE_YOUR_KEY_HERE_IF_LOCAL")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")

IMG_1 = os.path.join(TEMP_DIR, "news_image_1.jpg")
IMG_2 = os.path.join(TEMP_DIR, "news_image_2.jpg")

BAD_DOMAINS = ["vector", "freepik", "dreamstime", "alamy", "stock", "getty", "icon"]

KNOWN_TEAMS = [
    "india", "pakistan", "australia", "england", "new zealand", "south africa",
    "bangladesh", "sri lanka", "afghanistan",
    "mumbai indians", "mi", "chennai super kings", "csk",
    "royal challengers", "rcb", "kolkata knight riders", "kkr",
    "sunrisers hyderabad", "srh", "delhi capitals", "dc",
    "rajasthan royals", "rr", "lucknow super giants", "lsg",
    "gujarat titans", "gt", "punjab kings", "pbks"
]


# ================= IMAGE QUALITY =================

def image_is_valid(img):
    """Reject tiny, stretched, or blank images."""
    w, h = img.size
    if w < 500 or h < 500:
        return False

    # Reject extreme aspect ratios (banner / logo / collage)
    ratio = w / h
    if ratio < 0.5 or ratio > 2.0:
        return False

    # Reject blank / flat images
    stat = ImageStat.Stat(img.convert("L"))
    if stat.stddev[0] < 10:
        return False

    return True


# ================= DOWNLOAD =================

def download_image(url, save_path):
    try:
        resp = requests.get(url, timeout=6)
        if resp.status_code != 200 or len(resp.content) < 40000:
            return False

        img = Image.open(io.BytesIO(resp.content)).convert("RGB")

        if not image_is_valid(img):
            return False

        img.save(save_path, quality=95)
        return True

    except:
        return False


# ================= SERPER SEARCH =================

def execute_search(query, num_results=6):
    print(f"🔎 SERPER: {query}")

    url = "https://google.serper.dev/images"
    payload = json.dumps({"q": query, "gl": "in", "num": num_results})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}

    try:
        resp = requests.post(url, headers=headers, data=payload).json()

        results = []
        for item in resp.get('images', []):
            img_url = item.get("imageUrl", "").lower()
            if not img_url:
                continue
            if any(b in img_url for b in BAD_DOMAINS):
                continue
            results.append(img_url)

        return results

    except:
        return []


# ================= TEAM DETECTION =================

def extract_teams(title):
    t = title.lower()
    found = []

    for team in KNOWN_TEAMS:
        if team in t and team not in found:
            found.append(team)

    return found[:2]


# ================= MAIN SEARCH =================

def search_visuals():

    os.makedirs(TEMP_DIR, exist_ok=True)

    if os.path.exists(IMG_1): os.remove(IMG_1)
    if os.path.exists(IMG_2): os.remove(IMG_2)

    with open(NEWS_DATA, 'r') as f:
        data = json.load(f)

    title = data.get('title', '').lower()
    visual_prompt = data.get('visual_prompt', title)

    teams = extract_teams(title)

    # ========= DUAL MODE =========
    if len(teams) == 2:
        print(f"⚔️ Dual Mode: {teams[0]} vs {teams[1]}")

        # Team A
        urls = execute_search(f"{teams[0]} cricket player match action real photo")
        for url in urls:
            if download_image(url, IMG_1):
                print("   ✔ Team A image secured")
                break

        # Team B
        urls = execute_search(f"{teams[1]} cricket player match action real photo")
        for url in urls:
            if download_image(url, IMG_2):
                print("   ✔ Team B image secured")
                break

    # ========= SINGLE MODE =========
    else:
        print("👤 Single Mode")

        urls = execute_search(f"{visual_prompt} cricket match action real photo high resolution")

        for url in urls:
            if download_image(url, IMG_1):
                print("   ✔ Main image secured")
                break

        # Optional secondary (stadium / crowd)
        if os.path.exists(IMG_1):
            urls_bg = execute_search(f"{visual_prompt} cricket stadium crowd wide shot")
            for url in urls_bg:
                if download_image(url, IMG_2):
                    print("   ✔ Secondary image secured")
                    break


# ================= ENTRY =================

if __name__ == "__main__":
    search_visuals()
    sys.exit(0)
