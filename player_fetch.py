import requests
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
import os

PLAYER_NAME = "Virat Kohli"

search_url = (
    "https://en.wikipedia.org/w/api.php"
    "?action=query"
    "&format=json"
    "&prop=pageimages"
    "&piprop=original"
    f"&titles={PLAYER_NAME.replace(' ', '%20')}"
)

headers = {
    "User-Agent": "IPLTrackXBot/1.0"
}

try:
    r = requests.get(search_url, headers=headers, timeout=10)
    data = r.json()

    pages = data.get("query", {}).get("pages", {})
    page = list(pages.values())[0] if pages else {}

    if "original" in page:
        img_url = page["original"]["source"]

        img_data = requests.get(img_url, headers=headers, timeout=10).content
        img = Image.open(BytesIO(img_data)).convert("RGBA")

        # -------- UPSCALE + ENHANCE --------
        w, h = img.size
        img = img.resize((w * 2, h * 2), Image.LANCZOS)

        sharp = ImageEnhance.Sharpness(img)
        img = sharp.enhance(1.6)

        contrast = ImageEnhance.Contrast(img)
        img = contrast.enhance(1.15)

        img = img.filter(ImageFilter.DETAIL)

        os.makedirs("assets", exist_ok=True)
        img.save("assets/player_auto.png")

        print("Player image downloaded + enhanced → assets/player_auto.png")

    else:
        print("No image found for player")

except Exception as e:
    print("Player fetch failed:", e)

