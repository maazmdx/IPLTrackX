import os
import json
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---
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

def download_fonts():
    if not os.path.exists(FONTS_DIR): os.makedirs(FONTS_DIR)
    fonts = {
        "Anton-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",
        "Roboto-Regular.ttf": "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"
    }
    for name, url in fonts.items():
        path = os.path.join(FONTS_DIR, name)
        if not os.path.exists(path):
            try:
                r = requests.get(url)
                with open(path, 'wb') as f: f.write(r.content)
            except: pass

def create_design():
    print("🎨 ARTIST: Starting BIG TEXT Render...")
    download_fonts()
    
    W, H = 1080, 1350
    canvas = Image.new("RGB", (W, H), "#111111")
    
    # 1. IMAGE (Zoom & Crop)
    if os.path.exists(IMG_1):
        try:
            img = Image.open(IMG_1).convert("RGB")
            # Fill Height
            ratio = H / img.height
            new_size = (int(img.width * ratio), H)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Center Crop Width
            left = (img.width - W) // 2
            img = img.crop((left, 0, left + W, H))
            canvas.paste(img, (0, 0))
        except: pass
    
    # 2. GRADIENT (Darker & Higher for better readability)
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    draw_ov = ImageDraw.Draw(overlay)
    # Start gradient at 30% height instead of 40%
    for y in range(int(H * 0.3), H):
        alpha = int(255 * ((y - H * 0.3) / (H * 0.7)) ** 1.5)
        if alpha > 240: alpha = 240
        draw_ov.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    canvas.paste(overlay, (0,0), mask=overlay)
    
    # 3. TEXT ENGINE
    draw = ImageDraw.Draw(canvas)
    
    with open(NEWS_DATA, 'r') as f: data = json.load(f)
    headline = data.get('title', "BREAKING NEWS").upper()
    summary = data.get('summary', "Full story loading...")
    
    # --- FONT SIZES (BIGGER) ---
    HL_SIZE = 100
    SM_SIZE = 55  # Increased from 40
    
    try: hl_font = ImageFont.truetype(FONT_BOLD, HL_SIZE)
    except: hl_font = ImageFont.load_default()
    
    try: sm_font = ImageFont.truetype(FONT_REGULAR, SM_SIZE)
    except: sm_font = ImageFont.load_default()
    
    # WRAPPING (Adjust width for bigger font)
    # Headline: ~14 chars per line
    hl_lines = textwrap.wrap(headline, width=14) 
    # Summary: ~35 chars per line
    sm_lines = textwrap.wrap(summary, width=35)
    
    # HEIGHT CALCULATIONS
    hl_line_h = HL_SIZE * 1.1
    sm_line_h = SM_SIZE * 1.3
    
    total_hl_h = len(hl_lines) * hl_line_h
    total_sm_h = len(sm_lines) * sm_line_h
    
    # SPACING
    GAP = 40
    BOTTOM_MARGIN = 120
    
    # Start drawing from bottom up
    summary_y = H - BOTTOM_MARGIN - total_sm_h
    headline_y = summary_y - GAP - total_hl_h
    badge_y = headline_y - 90
    
    # 4. DRAW ELEMENTS
    
    # Badge
    draw.rounded_rectangle([(50, badge_y), (350, badge_y + 60)], radius=8, fill="#D10024")
    draw.text((75, badge_y + 10), "BREAKING NEWS", font=ImageFont.truetype(FONT_BOLD, 35), fill="white")
    
    # Headline
    curr_y = headline_y
    for line in hl_lines:
        draw.text((50, curr_y), line, font=hl_font, fill="white")
        curr_y += hl_line_h
        
    # Summary
    curr_y = summary_y
    for line in sm_lines:
        draw.text((50, curr_y), line, font=sm_font, fill="#e0e0e0") # Light grey
        curr_y += sm_line_h
        
    # Watermark
    draw.text((W - 250, 50), "@IPLTrackX", font=ImageFont.truetype(FONT_BOLD, 30), fill=(255, 255, 255, 150))
    
    canvas.save(FINAL_IMAGE, quality=100)
    print(f"✅ DESIGN SAVED: {FINAL_IMAGE}")
    return True

if __name__ == "__main__":
    create_design()
