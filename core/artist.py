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
IMG_1 = os.path.join(TEMP_DIR, "news_image_1.jpg") # We stick to single/dual logic if needed
IMG_2 = os.path.join(TEMP_DIR, "news_image_2.jpg")
FINAL_IMAGE = os.path.join(BASE_DIR, "final_post.jpg")

# Fonts
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

def fill_aspect(img, target_w, target_h):
    """Smart Crop to fill dimensions completely"""
    ratio = max(target_w / img.width, target_h / img.height)
    new_size = (int(img.width * ratio), int(img.height * ratio))
    img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Center Crop
    left = (img.width - target_w) // 2
    top = (img.height - target_h) // 3 # Bias towards top (faces)
    return img.crop((left, top, left + target_w, top + target_h))

def create_design():
    print("🎨 ARTIST: Starting Pro-Journalist Render...")
    download_fonts()
    
    # 1. SETUP CANVAS
    W, H = 1080, 1350
    canvas = Image.new("RGB", (W, H), "#111111")
    
    # 2. IMAGE LOGIC (Dual or Single)
    if os.path.exists(IMG_1) and os.path.exists(IMG_2):
        # Split Screen
        i1 = fill_aspect(Image.open(IMG_1).convert("RGB"), W, H//2)
        i2 = fill_aspect(Image.open(IMG_2).convert("RGB"), W, H//2)
        canvas.paste(i1, (0, 0))
        canvas.paste(i2, (0, H//2))
        ImageDraw.Draw(canvas).line([(0, H//2), (W, H//2)], fill="white", width=8)
    elif os.path.exists(IMG_1):
        # Full Screen
        img = fill_aspect(Image.open(IMG_1).convert("RGB"), W, H)
        canvas.paste(img, (0, 0))
    
    # 3. GRADIENT OVERLAY (Crucial for readability)
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    draw_ov = ImageDraw.Draw(overlay)
    # Strong gradient at bottom
    for y in range(int(H * 0.4), H):
        alpha = int(255 * ((y - H * 0.4) / (H * 0.6)) ** 2)
        draw_ov.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    canvas.paste(overlay, (0,0), mask=overlay)
    
    # 4. TEXT RENDERING
    draw = ImageDraw.Draw(canvas)
    
    with open(NEWS_DATA, 'r') as f: data = json.load(f)
    headline = data.get('title', "BREAKING NEWS").upper()
    summary = data.get('summary', "")
    
    # A. HEADLINE CONFIG
    hl_font_size = 90
    try: hl_font = ImageFont.truetype(FONT_BOLD, hl_font_size)
    except: hl_font = ImageFont.load_default()
    
    # Wrap Headline (15 chars per line for massive font)
    hl_lines = textwrap.wrap(headline, width=16) 
    
    # B. SUMMARY CONFIG
    sm_font_size = 40
    try: sm_font = ImageFont.truetype(FONT_REGULAR, sm_font_size)
    except: sm_font = ImageFont.load_default()
    
    # Wrap Summary (50 chars per line)
    sm_lines = textwrap.wrap(summary, width=50)
    
    # 5. POSITIONING CALCULATOR (Bottom-Up)
    # We calculate total height to know where to start drawing
    
    padding_bottom = 80
    summary_line_h = sm_font_size * 1.3
    headline_line_h = hl_font_size * 1.1
    gap = 30 # Space between headline and summary
    
    total_summary_h = len(sm_lines) * summary_line_h
    total_headline_h = len(hl_lines) * headline_line_h
    
    # Start Y position for the Summary (Bottom of canvas - padding - summary height)
    summary_start_y = H - padding_bottom - total_summary_h
    
    # Start Y position for Headline (Above summary - gap - headline height)
    headline_start_y = summary_start_y - gap - total_headline_h
    
    # Start Y position for Badge (Above headline)
    badge_start_y = headline_start_y - 80
    
    # 6. DRAW ELEMENTS
    
    # Badge
    draw.rounded_rectangle(
        [(50, badge_start_y), (310, badge_start_y + 55)], 
        radius=5, fill="#D10024"
    )
    draw.text((75, badge_start_y + 8), "BREAKING NEWS", font=ImageFont.truetype(FONT_BOLD, 30), fill="white")
    
    # Headline
    curr_y = headline_start_y
    for line in hl_lines:
        draw.text((50, curr_y), line, font=hl_font, fill="white")
        curr_y += headline_line_h
        
    # Summary
    curr_y = summary_start_y
    for line in sm_lines:
        draw.text((50, curr_y), line, font=sm_font, fill="#dddddd") # Slightly grey for hierarchy
        curr_y += summary_line_h
        
    # Watermark
    draw.text((W - 250, 50), "@IPLTrackX", font=ImageFont.truetype(FONT_BOLD, 30), fill=(255, 255, 255, 150))
    
    canvas.save(FINAL_IMAGE, quality=100)
    print(f"✅ Design Saved: {FINAL_IMAGE}")
    return True

if __name__ == "__main__":
    create_design()
