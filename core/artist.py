import os
import json
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")
IMG_1 = os.path.join(TEMP_DIR, "news_image_1.jpg")
IMG_2 = os.path.join(TEMP_DIR, "news_image_2.jpg")
FINAL_IMAGE = os.path.join(BASE_DIR, "final_post.jpg")

FONT_BOLD = os.path.join(FONTS_DIR, "Anton-Regular.ttf")

def download_fonts():
    if not os.path.exists(FONTS_DIR): os.makedirs(FONTS_DIR)
    if not os.path.exists(FONT_BOLD):
        r = requests.get("https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf")
        with open(FONT_BOLD, 'wb') as f: f.write(r.content)

def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.resize((crop_width, crop_height), Image.Resampling.LANCZOS)

def create_design():
    print("🎨 ARTIST: Starting Dynamic Render...")
    download_fonts()
    
    # 1. Canvas Setup
    W, H = 1080, 1350
    canvas = Image.new("RGB", (W, H), "#111111")
    
    # 2. Image Logic (The Splitter)
    has_img1 = os.path.exists(IMG_1)
    has_img2 = os.path.exists(IMG_2)
    
    if has_img1 and has_img2:
        print("   🖼️ Dual Image Layout")
        # Split Top/Bottom
        i1 = Image.open(IMG_1).convert("RGB")
        i2 = Image.open(IMG_2).convert("RGB")
        
        # Top Half (0 to 675)
        canvas.paste(crop_center(i1, W, H//2), (0, 0))
        # Bottom Half (675 to 1350)
        canvas.paste(crop_center(i2, W, H//2), (0, H//2))
        
        # Add a "VS" divider line
        draw = ImageDraw.Draw(canvas)
        draw.line([(0, H//2), (W, H//2)], fill="white", width=10)
        
    elif has_img1:
        print("   🖼️ Single Hero Layout")
        # Full Screen
        i1 = Image.open(IMG_1).convert("RGB")
        
        # Smart Resize (Fill Height)
        ratio = H / i1.height
        new_w = int(i1.width * ratio)
        if new_w < W: ratio = W / i1.width # Fallback if width is too small
        
        final_size = (int(i1.width * ratio), int(i1.height * ratio))
        i1 = i1.resize(final_size, Image.Resampling.LANCZOS)
        
        # Center Crop
        left = (i1.width - W) // 2
        canvas.paste(i1.crop((left, 0, left + W, H)), (0, 0))
        
    else:
        print("   ⚠️ No Images. Using Text-Only Mode.")
        
    # 3. The Shadow (Readability Layer)
    # Heavier gradient at bottom for text
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    d_over = ImageDraw.Draw(overlay)
    
    # Gradient starts at 40% height
    for y in range(int(H * 0.4), H):
        alpha = int(255 * ((y - H * 0.4) / (H * 0.6)) ** 2)
        d_over.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
        
    canvas.paste(overlay, (0,0), mask=overlay)
    
    # 4. Elastic Text Engine
    draw = ImageDraw.Draw(canvas)
    
    with open(NEWS_DATA, 'r') as f: data = json.load(f)
    text = data.get('title', "BREAKING NEWS").upper().replace('*', '')
    
    # Constraints
    MAX_W = W - 100 # 50px padding on sides
    MAX_H = 500     # Max height for text block
    START_Y = H - 100 # Bottom anchor
    
    font_size = 110 # Start Huge
    min_font_size = 45
    final_font = None
    final_lines = []
    
    # Binary Shrink Loop
    while font_size >= min_font_size:
        try:
            font = ImageFont.truetype(FONT_BOLD, font_size)
        except:
            font = ImageFont.load_default()
            break
            
        # Wrap text based on average char width
        avg_char_w = font_size * 0.5
        chars_per_line = int(MAX_W / avg_char_w)
        lines = textwrap.wrap(text, width=chars_per_line)
        
        # Calculate Height
        line_height = font_size * 1.1
        total_h = len(lines) * line_height
        
        # Check if it fits
        if total_h <= MAX_H:
            final_font = font
            final_lines = lines
            break
            
        font_size -= 5 # Shrink and retry
        
    # If text is STILL too long after shrinking to 45px, truncate it
    if font_size < min_font_size:
        font = ImageFont.truetype(FONT_BOLD, min_font_size)
        lines = textwrap.wrap(text, width=40)
        final_lines = lines[:5] # Keep first 5 lines
        final_lines[-1] += "..." # Add ellipsis
        final_font = font

    # 5. Render Text
    current_y = START_Y - (len(final_lines) * (font_size * 1.1))
    
    # Badge
    draw.rounded_rectangle(
        [(50, current_y - 70), (320, current_y - 15)], 
        radius=8, fill="#D10024"
    )
    draw.text((75, current_y - 62), "BREAKING NEWS", font=ImageFont.truetype(FONT_BOLD, 30), fill="white")
    
    for line in final_lines:
        draw.text((50, current_y), line, font=final_font, fill="white")
        current_y += (font_size * 1.1)
        
    # Watermark
    draw.text((W - 250, 50), "@IPLTrackX", font=ImageFont.truetype(FONT_BOLD, 30), fill=(255, 255, 255, 128))
    
    canvas.save(FINAL_IMAGE, quality=100)
    print("✅ Dynamic Layout Rendered.")
    return True

if __name__ == "__main__":
    create_design()
