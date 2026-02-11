import os
import json
import re
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")
NEWS_IMAGE = os.path.join(TEMP_DIR, "news_image.jpg")
FINAL_IMAGE = os.path.join(BASE_DIR, "final_post.jpg")

# Font Paths
FONT_BOLD = os.path.join(FONTS_DIR, "Anton-Regular.ttf") 
FONT_REGULAR = os.path.join(FONTS_DIR, "Roboto-Regular.ttf")

def download_fonts():
    if not os.path.exists(FONTS_DIR): os.makedirs(FONTS_DIR)
    fonts = {
        "Anton-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",
        "Roboto-Regular.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"
    }
    for font_name, url in fonts.items():
        font_path = os.path.join(FONTS_DIR, font_name)
        if not os.path.exists(font_path):
            try:
                r = requests.get(url)
                with open(font_path, 'wb') as f: f.write(r.content)
            except: pass

def clean_text(text):
    """Removes Markdown stars, HTML tags, and extra spaces."""
    if not text: return ""
    # Remove HTML
    text = re.sub(re.compile('<.*?>'), '', text)
    # Remove Markdown Bold (**)
    text = text.replace('**', '').replace('__', '')
    # Remove quotes at ends
    text = text.strip().strip('"').strip("'")
    return text.strip()

def create_gradient(width, height):
    gradient = Image.new('L', (width, height), color=0)
    draw = ImageDraw.Draw(gradient)
    for y in range(height):
        alpha = int(255 * (y / height) ** 1.2)
        draw.line((0, y, width, y), fill=alpha)
    return gradient

def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split()
    current_line = words[0]
    for word in words[1:]:
        test_line = current_line + " " + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def create_design():
    print("🎨 ARTIST: Starting 'Smart Layout' Render...")
    download_fonts()

    if not os.path.exists(NEWS_DATA): return False
    with open(NEWS_DATA, 'r') as f: data = json.load(f)

    # CANVAS
    W, H = 1080, 1350
    canvas = Image.new("RGB", (W, H), "black")

    if os.path.exists(NEWS_IMAGE):
        try:
            img = Image.open(NEWS_IMAGE).convert("RGB")
            
            # --- SMART IMAGE SCALING ---
            # If image is small (low res), DO NOT STRETCH. Use Blur BG.
            if img.width < 900 or img.height < 900:
                print("🎨 Artist: Low-Res Image Detected. Using Blur Background.")
                
                # 1. Background (Stretched & Blurred)
                bg = img.resize((W, H), Image.Resampling.LANCZOS)
                bg = bg.filter(ImageFilter.GaussianBlur(radius=40))
                # Darken the background
                overlay = Image.new('RGBA', (W, H), (0, 0, 0, 100))
                bg.paste(overlay, (0, 0), overlay)
                canvas.paste(bg, (0, 0))

                # 2. Foreground (Sharp & Centered)
                # Resize to fit width 1080, maintaining aspect ratio
                fg_ratio = img.width / img.height
                new_w = W
                new_h = int(new_w / fg_ratio)
                
                # If height is too tall, fit by height instead
                if new_h > H:
                    new_h = H
                    new_w = int(new_h * fg_ratio)
                
                fg = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                # Center paste
                x_pos = (W - new_w) // 2
                y_pos = (H - new_h) // 2
                canvas.paste(fg, (x_pos, y_pos))
                
            else:
                # High Res: Standard Fill Crop
                print("🎨 Artist: High-Res Image Detected. Using Full Crop.")
                aspect_ratio = img.width / img.height
                target_ratio = W / H
                if aspect_ratio > target_ratio:
                    new_height = H
                    new_width = int(new_height * aspect_ratio)
                else:
                    new_width = W
                    new_height = int(new_width / aspect_ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                left = (new_width - W) / 2
                top = (new_height - H) / 2
                img = img.crop((left, top, left + W, top + H))
                canvas.paste(img, (0, 0))
                
        except Exception as e:
            print(f"⚠️ Image Error: {e}")
    
    # GRADIENT (Bottom 75% for better text contrast)
    grad_height = int(H * 0.75)
    grad = create_gradient(W, grad_height)
    grad_layer = Image.new("RGBA", (W, grad_height), (0, 0, 0, 0))
    black_fill = Image.new("RGBA", (W, grad_height), (0, 0, 0, 250)) 
    grad_layer.putalpha(grad)
    canvas.paste(black_fill, (0, H - grad_height), grad_layer)

    draw = ImageDraw.Draw(canvas)

    # TYPOGRAPHY
    try:
        font_headline = ImageFont.truetype(FONT_BOLD, 95)
        font_summary = ImageFont.truetype(FONT_REGULAR, 40)
        font_badge = ImageFont.truetype(FONT_BOLD, 32)
    except:
        font_headline = ImageFont.load_default()
        font_summary = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    # CLEAN TEXT (Removes ** and HTML)
    headline = clean_text(data.get('title', '').upper())
    summary = clean_text(data.get('summary', ''))
    
    if len(summary) > 200: summary = summary[:200].rsplit(' ', 1)[0] + "..."

    PADDING = 65
    summary_lines = wrap_text(summary, font_summary, W - (PADDING * 2), draw)
    headline_lines = wrap_text(headline, font_headline, W - (PADDING * 2), draw)
    
    summary_h = len(summary_lines) * 50
    headline_h = len(headline_lines) * 105
    badge_h = 60
    gap = 35
    
    total_text_h = summary_h + gap + headline_h + gap + badge_h
    start_y = H - PADDING - total_text_h - 60 

    current_y = start_y

    # Badge
    draw.rounded_rectangle([(PADDING, current_y), (PADDING + 280, current_y + 50)], radius=8, fill="#D10024")
    draw.text((PADDING + 25, current_y + 8), "BREAKING NEWS", font=font_badge, fill="white")
    current_y += 80 

    # Headline
    for line in headline_lines:
        draw.text((PADDING, current_y), line, font=font_headline, fill="white")
        current_y += 105

    # Summary
    current_y += 10
    for line in summary_lines:
        draw.text((PADDING, current_y), line, font=font_summary, fill="#DDDDDD") 
        current_y += 50

    # Watermark
    try: wm_font = ImageFont.truetype(FONT_BOLD, 30)
    except: wm_font = ImageFont.load_default()
    draw.text((W - 250, 50), "@IPLTrackX", font=wm_font, fill=(255, 255, 255, 140))

    canvas.save(FINAL_IMAGE, quality=100, subsampling=0)
    print(f"✅ DESIGN COMPLETE: Saved to {FINAL_IMAGE}")
    return True

if __name__ == "__main__":
    create_design()
