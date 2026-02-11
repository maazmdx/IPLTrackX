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

# ================= SYSTEM FONT (NO FILE NEEDED) =================
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

def shadow(draw, xy, text, font, fill, off=4):
    x,y = xy
    draw.text((x+off, y+off), text, font=font, fill=(0,0,0))
    draw.text((x, y), text, font=font, fill=fill)

# ================= MAIN =================
def create_design():
    print("🎨 Rendering with SYSTEM FONT")

    W, H = 1080, 1350
    canvas = Image.new("RGB", (W,H), "#000000")

    # ---- IMAGE (NO BLACK BARS)
    if os.path.exists(IMG_1):
        img = Image.open(IMG_1).convert("RGB")
        ratio = W / img.width
        nh = int(img.height * ratio)
        img = img.resize((W, nh), Image.Resampling.LANCZOS)
        if nh > H:
            top = int((nh - H) * 0.35)
            img = img.crop((0, top, W, top + H))
        canvas.paste(img, (0,0))

    # ---- STRONG GRADIENT FOR TEXT
    b = brightness(canvas)
    overlay = Image.new("RGBA", (W,H), (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    base = int(210 + (b/255)*30)

    for y in range(int(H*0.40), H):
        a = int(base * ((y-H*0.40)/(H*0.60)))
        d.line([(0,y),(W,y)], fill=(0,0,0,a))

    canvas.paste(overlay, (0,0), overlay)

    draw = ImageDraw.Draw(canvas)

    # ---- LOAD TEXT FROM GEMINI (brain.py output)
    with open(NEWS_DATA) as f:
        data = json.load(f)

    headline = data.get("title","BREAKING NEWS").upper()
    summary  = data.get("summary","")

    SAFE_LEFT = 70
    SAFE_BOTTOM = H - 110
    TEXT_W = int(W*0.50)

    # ---- HEADLINE BIG
    HL = 96
    while HL >= 70:
        hfont = sys_font(HL, bold=True)
        hlines = wrap(draw, headline, hfont, TEXT_W)
        if len(hlines) <= 4:
            break
        HL -= 2

    # ---- SUMMARY BIG & READABLE
    SM = int(HL * 0.65)
    SM = max(44, min(60, SM))
    sfont = sys_font(SM)

    hlines = wrap(draw, headline, hfont, TEXT_W)
    slines = wrap(draw, summary, sfont, TEXT_W)

    hh = int(HL*1.05)
    sh = int(SM*1.30)

    sy = SAFE_BOTTOM - len(slines)*sh
    hy = sy - 30 - len(hlines)*hh
    by = hy - 75

    # ---- BREAKING BADGE
    draw.rounded_rectangle([(SAFE_LEFT,by),(SAFE_LEFT+300,by+60)], radius=8, fill="#D10024")
    shadow(draw, (SAFE_LEFT+20, by+12), "BREAKING NEWS", sys_font(34,True), "white", off=2)

    # ---- HEADLINE
    y = hy
    for l in hlines:
        shadow(draw, (SAFE_LEFT,y), l, hfont, "white", off=5)
        y += hh

    # ---- SUMMARY
    y = sy
    for l in slines:
        shadow(draw, (SAFE_LEFT,y), l, sfont, "white", off=3)
        y += sh

    # ---- WATERMARK
    draw.text((W-260, 45), "@IPLTrackX", font=sys_font(32,True), fill=(255,255,255,150))

    # ---- FINAL SHARPEN
    canvas = ImageEnhance.Contrast(canvas).enhance(1.10)
    canvas = canvas.filter(ImageFilter.UnsharpMask(radius=1.5, percent=130, threshold=3))

    canvas.save(FINAL_IMAGE, "JPEG", quality=95, subsampling=0, optimize=True)
    print("✅ POST SAVED")

if __name__ == "__main__":
    create_design()
