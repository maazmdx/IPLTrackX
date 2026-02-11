import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageStat

# ================= CONFIG =================
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


# ================= FONT SAFETY =================

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

        print(f"⬇️ Downloading font: {name}")
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and len(r.content) > 20000:
                with open(path, "wb") as f:
                    f.write(r.content)
        except:
            print(f"⚠️ Failed to download {name}")


def safe_font(path, size):
    try:
        if not os.path.exists(path) or os.path.getsize(path) < 10000:
            raise Exception("Font missing/corrupt")
        return ImageFont.truetype(path, size)
    except:
        print(f"⚠️ Using default font for {path}")
        return ImageFont.load_default()


# ================= HELPERS =================

def calculate_brightness(image):
    grey = image.convert("L")
    stat = ImageStat.Stat(grey)
    return stat.mean[0]


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""

    for word in words:
        test = current + (" " if current else "") + word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_shadow(draw, pos, text, font, fill, offset=3):
    x, y = pos
    draw.text((x + offset, y + offset), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=fill)


# ================= MAIN =================

def create_design():

    print("🎨 ARTIST: Rendering broadcast post...")
    ensure_fonts()

    W, H = 1080, 1350
    canvas = Image.new("RGB", (W, H), "#000000")

    # ---------- IMAGE FIT (NO BLACK BARS) ----------
    if os.path.exists(IMG_1):
        img = Image.open(IMG_1).convert("RGB")

        ratio = W / img.width
        new_h = int(img.height * ratio)
        img = img.resize((W, new_h), Image.Resampling.LANCZOS)

        if new_h > H:
            top = (new_h - H) // 2
            img = img.crop((0, top, W, top + H))

        canvas.paste(img, (0, 0))

    # ---------- SOFT GRADIENT ----------
    brightness = calculate_brightness(canvas)
    base_opacity = int(140 + (brightness / 255) * 40)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    for y in range(int(H * 0.45), H):
        factor = (y - H * 0.45) / (H * 0.55)
        alpha = int(base_opacity * factor)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    canvas.paste(overlay, (0, 0), overlay)

    # ---------- LOAD TEXT ----------
    draw = ImageDraw.Draw(canvas)

    with open(NEWS_DATA, 'r') as f:
        data = json.load(f)

    headline = data.get("title", "BREAKING NEWS").upper()
    summary = data.get("summary", "")

    SAFE_LEFT = 70
    SAFE_BOTTOM = H - 100
    TEXT_WIDTH = int(W * 0.46)

    # ---------- HEADLINE AUTO SIZE ----------
    HL_SIZE = 88
    while True:
        hl_font = safe_font(FONT_BOLD, HL_SIZE)
        lines = wrap_text(draw, headline, hl_font, TEXT_WIDTH)
        if len(lines) <= 4 or HL_SIZE <= 72:
            break
        HL_SIZE -= 2

    # ---------- SUMMARY SIZE (BIGGER) ----------
    SM_SIZE = int(HL_SIZE * 0.48)
    SM_SIZE = max(36, min(48, SM_SIZE))
    sm_font = safe_font(FONT_REGULAR, SM_SIZE)

    hl_lines = wrap_text(draw, headline, hl_font, TEXT_WIDTH)
    sm_lines = wrap_text(draw, summary, sm_font, TEXT_WIDTH)

    hl_h = int(HL_SIZE * 1.05)
    sm_h = int(SM_SIZE * 1.25)

    total_hl = len(hl_lines) * hl_h
    total_sm = len(sm_lines) * sm_h

    summary_y = SAFE_BOTTOM - total_sm
    headline_y = summary_y - 30 - total_hl
    badge_y = headline_y - 70

    # ---------- BADGE ----------
    draw.rounded_rectangle(
        [(SAFE_LEFT, badge_y), (SAFE_LEFT + 290, badge_y + 55)],
        radius=6, fill="#D10024"
    )

    badge_font = safe_font(FONT_BOLD, 32)
    draw_shadow(draw, (SAFE_LEFT + 18, badge_y + 8), "BREAKING NEWS", badge_font, "white", offset=1)

    # ---------- HEADLINE ----------
    y = headline_y
    for line in hl_lines:
        draw_shadow(draw, (SAFE_LEFT, y), line, hl_font, "white", offset=4)
        y += hl_h

    # ---------- SUMMARY ----------
    y = summary_y
    for line in sm_lines:
        draw_shadow(draw, (SAFE_LEFT, y), line, sm_font, "#F0F0F0", offset=2)
        y += sm_h

    # ---------- WATERMARK ----------
    wm_font = safe_font(FONT_BOLD, 30)
    draw.text((W - 260, 50), "@IPLTrackX", font=wm_font, fill=(255, 255, 255, 110))

    # ---------- INSTAGRAM SHARPEN ----------
    canvas = ImageEnhance.Contrast(canvas).enhance(1.05)
    canvas = canvas.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))

    canvas.save(FINAL_IMAGE, format="JPEG", quality=95, subsampling=0, optimize=True)
    print(f"✅ SAVED: {FINAL_IMAGE}")


if __name__ == "__main__":
    create_design()

