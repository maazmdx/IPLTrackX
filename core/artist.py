import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageStat

# ================= PATHS =================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")
IMG_1 = os.path.join(TEMP_DIR, "news_image_1.jpg")
FINAL_IMAGE = os.path.join(BASE_DIR, "final_post.jpg")

# ================= SYSTEM FONT =================
def sys_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

# ================= HELPERS =================
def brightness(img):
    return ImageStat.Stat(img.convert("L")).mean[0]

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

def glass_text(draw, xy, text, font):
    x, y = xy
    # shadow
    draw.text((x+4, y+4), text, font=font, fill=(0,0,0,200))
    # gradient / glass white
    draw.text((x, y), text, font=font, fill=(255,255,255,235))

# ================= MAIN =================
def create_design():

    print("🎨 Rendering PRO layout")

    W, H = 1080, 1350
    canvas = Image.new("RGB", (W,H), "#000000")

    # -------- IMAGE (FULL WIDTH, NO BARS)
    if os.path.exists(IMG_1):
        img = Image.open(IMG_1).convert("RGB")
        ratio = W / img.width
        nh = int(img.height * ratio)
        img = img.resize((W, nh), Image.Resampling.LANCZOS)

        if nh > H:
            top = int((nh - H) * 0.30)
            img = img.crop((0, top, W, top + H))

        canvas.paste(img, (0,0))

    # -------- STRONG BOTTOM GRADIENT (TEXT AREA)
    b = brightness(canvas)
    overlay = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(overlay)

    base = int(210 + (b/255)*30)

    for y in range(int(H*0.45), H):
        a = int(base * ((y-H*0.45)/(H*0.55)))
        d.line([(0,y),(W,y)], fill=(0,0,0,a))

    canvas.paste(overlay, (0,0), overlay)

    draw = ImageDraw.Draw(canvas)

    # -------- LOAD TEXT
    with open(NEWS_DATA) as f:
        data = json.load(f)

    headline = data.get("title","BREAKING NEWS").upper()
    summary  = data.get("summary","")

    # -------- POSITION (LOWER, USE FULL AREA)
    SAFE_LEFT = 80
    TEXT_WIDTH = int(W * 0.78)

    # -------- HEADLINE SIZE (CONTROLLED BIG)
    HL = 88
    while HL >= 64:
        hfont = sys_font(HL, True)
        hlines = wrap(draw, headline, hfont, TEXT_WIDTH)
        if len(hlines) <= 2:
            break
        HL -= 2

    # -------- SUMMARY SIZE (MEDIUM, CLEAR)
    SM = int(HL * 0.48)
    SM = max(34, min(44, SM))
    sfont = sys_font(SM)

    hlines = wrap(draw, headline, hfont, TEXT_WIDTH)
    slines = wrap(draw, summary, sfont, TEXT_WIDTH)

    hh = int(HL * 1.05)
    sh = int(SM * 1.25)

    # ---- stack lower (professional)
    total_height = len(hlines)*hh + len(slines)*sh + 120
    base_y = H - total_height - 40

    # -------- BREAKING NEWS BADGE (HORIZONTAL)
    badge_y = base_y
    draw.rounded_rectangle(
        [(SAFE_LEFT, badge_y), (SAFE_LEFT + 340, badge_y + 62)],
        radius=10, fill="#D10024"
    )
    glass_text(draw, (SAFE_LEFT + 20, badge_y + 14),
               "BREAKING NEWS", sys_font(36, True))

    # -------- HEADLINE (GLASS EFFECT)
    y = badge_y + 80
    for l in hlines:
        glass_text(draw, (SAFE_LEFT, y), l, hfont)
        y += hh

    # -------- SUMMARY
    y += 10
    for l in slines:
        glass_text(draw, (SAFE_LEFT, y), l, sfont)
        y += sh

    # -------- WATERMARK
    draw.text((W-260, 50), "@IPLTrackX",
              font=sys_font(30, True),
              fill=(255,255,255,150))

    # -------- FINAL SHARPEN
    canvas = ImageEnhance.Contrast(canvas).enhance(1.08)
    canvas = canvas.filter(ImageFilter.UnsharpMask(radius=1.4, percent=120, threshold=3))

    canvas.save(FINAL_IMAGE, "JPEG", quality=95, subsampling=0, optimize=True)
    print("✅ SAVED:", FINAL_IMAGE)

# ================= RUN =================
if __name__ == "__main__":
    create_design()
