import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# ================= PATHS =================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")
IMG_1 = os.path.join(TEMP_DIR, "news_image_1.jpg")
FINAL_IMAGE = os.path.join(BASE_DIR, "final_post.jpg")


# ================= CANVAS =================
W, H = 1080, 1350


def safe_load_image():
    """Always returns a valid background image"""
    if not os.path.exists(IMG_1):
        print("⚠️ No image found → using fallback")
        return Image.new("RGB", (W, H), "#0b1220")

    try:
        img = Image.open(IMG_1).convert("RGB")
    except:
        print("⚠️ Corrupt image → fallback")
        return Image.new("RGB", (W, H), "#0b1220")

    # Resize to fill height
    ratio = H / img.height
    new_w = int(img.width * ratio)
    img = img.resize((new_w, H), Image.Resampling.LANCZOS)

    # Center crop
    if new_w > W:
        left = (new_w - W) // 2
        img = img.crop((left, 0, left + W, H))

    return img


def darken_bottom(image):
    """Broadcast dark gradient for text readability"""
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for y in range(int(H * 0.55), H):
        alpha = int(200 * ((y - H * 0.55) / (H * 0.45)))
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    image.paste(overlay, (0, 0), overlay)
    return image


def wrap_text(draw, text, font, max_width):
    """Pixel-based wrapping"""
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = current + (" " if current else "") + word
        w = draw.textbbox((0, 0), test, font=font)[2]
        if w <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_post():
    print("🎨 Rendering Broadcast Post...")

    # ---------- LOAD DATA ----------
    if not os.path.exists(NEWS_DATA):
        print("No news data.")
        return

    with open(NEWS_DATA, "r") as f:
        data = json.load(f)

    headline = data.get("title", "BREAKING NEWS")
    summary = data.get("summary", "")

    # ---------- BACKGROUND ----------
    canvas = Image.new("RGB", (W, H), "#000000")
    bg = safe_load_image()
    canvas.paste(bg, (0, 0))

    canvas = darken_bottom(canvas)

    draw = ImageDraw.Draw(canvas)

    # ---------- FONTS (System Default) ----------
    font_headline = ImageFont.load_default()
    font_summary = ImageFont.load_default()
    font_badge = ImageFont.load_default()

    # ---------- BREAKING BAR ----------
    bar_y = int(H * 0.62)

    draw.rectangle([(80, bar_y), (520, bar_y + 70)], fill="#e10600")
    draw.text((110, bar_y + 18), "BREAKING NEWS", fill="white", font=font_badge)

    # ---------- HEADLINE ----------
    max_width = W - 160
    headline_lines = wrap_text(draw, headline.upper(), font_headline, max_width)

    y = bar_y + 100
    for line in headline_lines:
        draw.text((80, y), line, font=font_headline, fill="white")
        y += 60

    # ---------- SUMMARY ----------
    y += 10
    summary_lines = wrap_text(draw, summary, font_summary, max_width)

    for line in summary_lines[:3]:
        draw.text((80, y), line, font=font_summary, fill="#dddddd")
        y += 45

    # ---------- WATERMARK ----------
    draw.text((W - 260, 40), "@IPLTrackX", fill=(255, 255, 255), font=font_summary)

    # ---------- SAVE ----------
    canvas.save(FINAL_IMAGE, quality=95)
    print("✅ Saved:", FINAL_IMAGE)


if __name__ == "__main__":
    draw_post()
