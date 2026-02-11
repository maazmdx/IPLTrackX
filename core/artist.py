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
    """Forcefully removes Markdown stars and clean up text."""
    if not text: return ""
    # Remove stars, underscores, and extra spaces
    text = text.replace('*', '').replace('_', '').replace('#', '')
    text = re.sub(r'\s+', ' ', text) # Collapse multiple spaces
    return text.strip()

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
    print("🎨 ARTIST: Starting 'Force-Fit' Render...")
    download_fonts()

    if not os.path.exists(NEWS_DATA): return False
    with open(NEWS_DATA, 'r') as f: data = json.load(f)

    # CANVAS (Instagram Portrait)
    W, H = 1080, 1350
    canvas = Image.new("RGB", (W, H), "black")

    # 1. IMAGE PROCESSING
    if os.path.exists(NEWS_IMAGE):
        try:
            img = Image.open(NEWS_IMAGE).convert("RGB")
            
            # FORCE FILL LOGIC
            # We want the image to cover the ENTIRE 1080x1350 canvas.
            # Calculate ratios
            target_ratio = W / H
            img_ratio = img.width / img.height

            if img_ratio > target_ratio:
                # Image is wider than canvas -> Resize by Height, Crop Width
                new_height = H
                new_width = int(new_height * img_ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Center Crop
                left = (new_width - W) // 2
                img = img.crop((left, 0, left + W, H))
            else:
                # Image is taller/narrower -> Resize by Width, Crop Height
                new_width = W
                new_height = int(new_width / img_ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Center Crop (Focus slightly higher than center for faces)
                top = (new_height - H) // 3 
                img = img.crop((0, top, W, top + H))
            
            canvas.paste(img, (0, 0))

        except Exception as e:
            print(f"⚠️ Image Error: {e}. Using Black Background.")
            # Keep black canvas
    else:
        print("⚠️ No Image Found. Using Black Background.")

    # 2. OVERLAY (Dark Gradient at bottom for text readability)
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    # Gradient from transparent to black (starting at 50% height)
    for y in range(int(H * 0.4), H):
        alpha = int(255 * ((y - H * 0.4) / (H * 0.6)) ** 1.5) # Non-linear for smoother fade
        if alpha > 240: alpha = 240 # Max darkness
        draw_overlay.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
        
    canvas.paste(overlay, (0,0), mask=overlay)

    # 3. TYPOGRAPHY
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_headline = ImageFont.truetype(FONT_BOLD, 90) # Big & Bold
        font_badge = ImageFont.truetype(FONT_BOLD, 30)
    except:
        font_headline = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    # Clean the text vigorously
    headline = clean_text(data.get('title', '').upper())

    # Padding
    PAD_X = 60
    PAD_BOTTOM = 80

    # Wrap Headline
    lines = wrap_text(headline, font_headline, W - (PAD_X * 2), draw)
    
    # Calculate Text Block Height to position it correctly
    line_height = 100
    total_text_height = len(lines) * line_height
    
    # Start position (Bottom up)
    current_y = H - PAD_BOTTOM - total_text_height

    # Badge (BREAKING NEWS)
    badge_w = 260
    badge_h = 45
    draw.rounded_rectangle(
        [(PAD_X, current_y - 70), (PAD_X + badge_w, current_y - 25)], 
        radius=5, 
        fill="#D10024" # Red
    )
    draw.text((PAD_X + 25, current_y - 62), "BREAKING NEWS", font=font_badge, fill="white")

    # Draw Headline
    for line in lines:
        draw.text((PAD_X, current_y), line, font=font_headline, fill="white")
        current_y += line_height

    # Watermark (Top Right)
    draw.text((W - 250, 40), "@IPLTrackX", font=font_badge, fill=(255, 255, 255, 180))

    canvas.save(FINAL_IMAGE, quality=100, subsampling=0)
    print(f"✅ DESIGN COMPLETE: Saved to {FINAL_IMAGE}")
    return True

if __name__ == "__main__":
    create_design()
