import os
import json
import requests
import io
from PIL import Image

SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")

IMG_1 = os.path.join(TEMP_DIR, "news_image_1.jpg")

BAD_DOMAINS = ["vector", "freepik", "dreamstime", "alamy", "stock", "getty", "icon"]


def download_image(url, save_path):
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200 and len(r.content) > 25000:
            img = Image.open(io.BytesIO(r.content))
            img.verify()
            with open(save_path, "wb") as f:
                f.write(r.content)
            return True
    except:
        return False
    return False


def search_images(query):
    url = "https://google.serper.dev/images"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = json.dumps({"q": query, "num": 8})

    try:
        res = requests.post(url, headers=headers, data=payload, timeout=10).json()
        urls = []
        for img in res.get("images", []):
            link = img.get("imageUrl", "")
            if not any(b in link.lower() for b in BAD_DOMAINS):
                urls.append(link)
        return urls
    except:
        return []


def search_visuals():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    if os.path.exists(IMG_1):
        os.remove(IMG_1)

    if not os.path.exists(NEWS_DATA):
        print("No design data.")
        return

    with open(NEWS_DATA, "r") as f:
        data = json.load(f)

    query = data.get("visual_prompt", data.get("title", "")) + " cricket match action"

    print("🔎 Searching image:", query)

    # -------- TRY 3 TIMES --------
    for attempt in range(3):
        urls = search_images(query)
        for url in urls:
            if download_image(url, IMG_1):
                print("✅ Image secured")
                return

        print(f"Retry {attempt+1}/3 failed")

    # -------- FALLBACK IMAGE --------
    print("⚠️ Using fallback image")

    fallback = Image.new("RGB", (1080, 1350), "#0b1220")
    fallback.save(IMG_1)


if __name__ == "__main__":
    search_visuals()
