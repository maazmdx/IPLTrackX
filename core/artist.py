import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageStat

# =========================================================
# BASIC PATHS
# =========================================================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")
IMG_1 = os.path.join(TEMP_DIR, "news_image_1.jpg")
FINAL_IMAGE = os.path.join(BASE_DIR, "final_post.jpg")

FONT_BOLD = os.path.join(FONTS_DIR, "Anton-Regular.ttf")
FONT_REGULAR = os.path.join(FONTS_DIR, "Roboto-Regular.ttf")

# =========================================================
# FONT SAFETY (NO CRASH EVER)
# =========================================================
def ensure_fonts():
    os.makedirs(FONTS_DIR, exist_ok=True)
    fonts = {
        "Anton-Regular.ttf":
        "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",
        "Roboto-Regular.ttf":
        "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"
    }

    for name, url in fonts.items():
        path = os.path.join(FONTS_DIR, name)
        if os.path.exists(path) and os.path.getsize(path) > 20000:
            continue
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and len(r.content) > 20000:
                with open(path, "wb") as f:
                    f.write(r.content)
        except:
            pass

def safe_font(path, size):
    try:
        if not os.path.exists(path) or os.path.getsize(path) < 10000:
            raise Exception
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# =========================================================
# HELPERS
# =========================================================
def brightness(img):
    stat = ImageStat.Stat(img.convert("L"))
    return stat.mean[0]

def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = cur + (" " if cur else "") + w
        if draw.textbbox((0,0), test, font=font)[2] <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def shadow(draw, xy, text, font, fill, off=4):
    x,y = xy
    draw.text((x+off, y+off), text, font=font, fill=(0,0,0))
    draw.text((x, y), text, font=font, fill=fill)

# =========================================================
# MAIN RENDER
# =========================================================
def create_design():
    print("🎨 ARTIST: Rendering FINAL broadcast post")
    ensure_fonts()

    W, H = 1080, 1350
    canvas = Image.new("RGB", (W,H), "#000000")

    # ---------------- IMAGE (NO BLACK BARS EVER)
    if os.path.exists(IMG_1):_
