import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont

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

def get_dynamic_font(text, max_width, max_height, font_path, draw):
    """Calculates the best font size to fill the space."""
    size = 120 # Start big
    min_size = 40
    
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        lines = wrap_text(text, font, max_width, draw)
        
        text_h = len(lines) * (size * 1.2) # Estimate height
        text_w = max([draw.textbbox((0,0), line, font=font)[2] for line in lines])
        
        if text_w <= max_width and text_h <= max_height:
            return font, lines, size * 1.2
        
        size -= 5 # Reduce size and try again
        
    return ImageFont.truetype(font_path, min_size), wrap_text(text, font, max_width, draw), min_size * 1.2

def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split()
    current_line = words[0]
    for word in words[1:]:
        test_line = current_line + " " + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines

def create_design():
    print("🎨 ARTIST: Starting 'Master Layout' Render...")
    download_fonts()

    if not os.path.exists(NEWS_DATA): return False
    with open(NEWS_DATA, 'r') as f: data = json.load(f)

    # CANVAS (Instagram Portrait)
    W, H = 1080, 1350
    canvas = Image.new("RGB", (W, H), "#1a1a1a") # Dark gray fallback

    # 1. IMAGE PROCESSING (Force-Fill Strategy)
    if os.path.exists(NEWS_IMAGE):
        try:
            img = Image.open(NEWS_IMAGE).convert("RGB")
            
            # Calculate aspect ratios
            target_ratio = W / H
            img_ratio = img.width / img.height

            if img_ratio > target_ratio:
                # Image is wider -> Resize to height, crop width
                new_height = H
                new_width = int(new_height * img_ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Center crop
                left = (new_width - W) // 2
                img = img.crop((left, 0, left + W, H))
            else:
                # Image is taller -> Resize to width, crop height
                new_width = W
                new_height = int(new_width / img_ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Bias crop towards the bottom (for action shots)
                top = int((new_height - H) * 0.3) 
                img = img.crop((0, top, W, top + H))
            
            canvas.paste(img, (0, 0))

        except Exception as e:
            print(f"⚠️ Image Error: {e}. Using solid background.")

    # 2. DARK OVERLAY (For text readability)
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    draw_overlay = ImageDraw.Draw(overlay)
    # Solid semi-transparent block at the bottom
    draw_overlay.rectangle([(0, H - 500), (W, H)], fill=(0, 0, 0, 200))
    canvas.paste(overlay, (0,0), mask=overlay)

    # 3. TYPOGRAPHY
    draw = ImageDraw.Draw(canvas)
    headline = data.get('title', '').upper()
    
    # Layout Constants
    PAD = 60
    TEXT_AREA_W = W - (PAD * 2)
    TEXT_AREA_H = 400
    
    # Get Dynamic Headline Font
    font_headline, hl_lines, hl_line_height = get_dynamic_font(
        headline, TEXT_AREA_W, TEXT_AREA_H, FONT_BOLD, draw
    )
    
    # Badge Font
    try: font_badge = ImageFont.truetype(FONT_BOLD, 30)
    except: font_badge = ImageFont.load_default()

    # Position Elements (Bottom-Up)
    current_y = H - PAD - 20
    
    # Draw Headline
    for line in reversed(hl_lines):
        draw.text((PAD, current_y - hl_line_height + 20), line, font=font_headline, fill="white")
        current_y -= hl_line_height

    # Draw Badge
    current_y -= 70
    draw.rounded_rectangle(
        [(PAD, current_y), (PAD + 260, current_y + 45)], 
        radius=6, fill="#D10024"
    )
    draw.text((PAD + 25, current_y + 8), "BREAKING NEWS", font=font_badge, fill="white")

    # Watermark
    draw.text((W - 250, 50), "@IPLTrackX", font=font_badge, fill=(255, 255, 255, 150))

    canvas.save(FINAL_IMAGE, quality=95)
    print(f"✅ DESIGN COMPLETE: Saved to {FINAL_IMAGE}")
    return True

if __name__ == "__main__":
    create_design()
