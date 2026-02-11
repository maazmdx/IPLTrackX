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
    if os.path.exists(IMG_1):
        img = Image.open(IMG_1).convert("RGB")
        ratio = W / img.width
        nh = int(img.height * ratio)
        img = img.resize((W, nh), Image.Resampling.LANCZOS)

        if nh > H:
            top = int((nh - H) * 0.35)
            img = img.crop((0, top, W, top + H))

        canvas.paste(img, (0,0))

    # ---------------- STRONG TEXT BACKGROUND
    b = brightness(canvas)
    overlay = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(overlay)

    base = int(200 + (b/255)*40)
    for y in range(int(H*0.40), H):
        a = int(base * ((y-H*0.40)/(H*0.60)))
        d.line([(0,y),(W,y)], fill=(0,0,0,a))

    canvas.paste(overlay, (0,0), overlay)

    draw = ImageDraw.Draw(canvas)

    # ---------------- LOAD DATA
    with open(NEWS_DATA) as f:
        data = json.load(f)

    headline = data.get("title","BREAKING NEWS").upper()
    summary  = data.get("summary","")

    if len(headline.split()) <= 2:
        headline += " MATCH WIN"

    SAFE_LEFT = 70
    SAFE_BOTTOM = H - 110
    TEXT_W = int(W*0.50)

    # ---------------- HEADLINE (BIG BUT CONTROLLED)
    HL = 96
    while HL >= 72:
        hfont = safe_font(FONT_BOLD, HL)
        hlines = wrap(draw, headline, hfont, TEXT_W)
        if len(hlines) <= 4:
            break
        HL -= 2

    # ---------------- SUMMARY (BIG & READABLE)
    SM = int(HL * 0.65)
    SM = max(44, min(56, SM))
    sfont = safe_font(FONT_REGULAR, SM)

    hlines = wrap(draw, headline, hfont, TEXT_W)
    slines = wrap(draw, summary, sfont, TEXT_W)

    hh = int(HL*1.05)
    sh = int(SM*1.30)

    total_h = len(hlines)*hh + len(slines)*sh + 90

    sy = SAFE_BOTTOM - len(slines)*sh
    hy = sy - 30 - len(hlines)*hh
    by = hy - 75

    # ---------------- BREAKING BADGE
    draw.rounded_rectangle(
        [(SAFE_LEFT, by),(SAFE_LEFT+300, by+58)],
        radius=8, fill="#D10024"
    )
    shadow(draw, (SAFE_LEFT+18, by+10), "BREAKING NEWS",
           safe_font(FONT_BOLD, 34), "white", off=2)

    # ---------------- HEADLINE DRAW
    y = hy
    for l in hlines:
        shadow(draw, (SAFE_LEFT, y), l, hfont, "white", off=5)
        y += hh

    # ---------------- SUMMARY DRAW (CLEAR!)
    y = sy
    for l in slines:
        shadow(draw, (SAFE_LEFT, y), l, sfont, "#FFFFFF", off=3)
        y += sh

    # ---------------- WATERMARK
    draw.text((W-260, 45), "@IPLTrackX",
              font=safe_font(FONT_BOLD, 32),
              fill=(255,255,255,140))

    # ---------------- INSTAGRAM FINISH
    canvas = ImageEnhance.Contrast(canvas).enhance(1.10)
    canvas = canvas.filter(ImageFilter.UnsharpMask(radius=1.4, percent=130, threshold=3))

    canvas.save(FINAL_IMAGE, "JPEG", quality=95, subsampling=0, optimize=True)
    print("✅ FINAL POST SAVED")

# =========================================================
if __name__ == "__main__":
    create_design()
