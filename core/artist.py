import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageEnhance, ImageFilter

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")
IMG_1 = os.path.join(TEMP_DIR, "news_image_1.jpg")
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

def calculate_brightness(image):
    """Returns the average brightness of the image (0-255)."""
    greyscale = image.convert('L')
    stat = ImageStat.Stat(greyscale)
    return stat.mean[0]

def wrap_text_pixel(text, font, max_width, draw):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line = test_line
        else:
            if current_line: lines.append(current_line)
            current_line = word
    if current_line: lines.append(current_line)
    return lines

def draw_shadow_text(draw, xy, text, font, fill="white", shadow_color="black", offset=3):
    x, y = xy
    # Hard Shadow (Broadcast Style)
    draw.text((x + offset, y + offset), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fill)

def create_design():
    print("🎨 ARTIST: Starting FINAL PRODUCTION Render...")
    download_fonts()
    
    W, H = 1080, 1350
    canvas = Image.new("RGB", (W, H), "#111111")
    
    # 1. SMART CROP (Top-Center Bias)
    if os.path.exists(IMG_1):
        try:
            img = Image.open(IMG_1).convert("RGB")
            # Resize to fill Height
            ratio = H / img.height
            new_w = int(img.width * ratio)
            img = img.resize((new_w, H), Image.Resampling.LANCZOS)
            
            # Crop Logic: Keep action on right, but prioritize center
            if new_w > W:
                left = (new_w - W) // 2
                img = img.crop((left, 0, left + W, H))
            
            canvas.paste(img, (0, 0))
        except: pass

    # 2. ADAPTIVE GRADIENT (Smart Vision)
    crop_box = (0, int(H*0.5), int(W*0.6), H)
    region = canvas.crop(crop_box)
    brightness = calculate_brightness(region)
    
    # Adaptive Opacity: Darker gradient for bright images
    base_opacity = int(180 + (brightness / 255) * 60)
    
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    draw_ov = ImageDraw.Draw(overlay)
    
    # Vertical Gradient
    for y in range(int(H * 0.4), H):
        factor = (y - H * 0.4) / (H * 0.6)
        alpha = int(255 * (factor ** 1.5))
        if alpha > base_opacity: alpha = base_opacity
        draw_ov.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
        
    # Side Gradient
    for x in range(0, int(W * 0.6)):
        factor = 1 - (x / (W * 0.6))
        alpha = int(base_opacity * 0.9 * factor)
        draw_ov.line([(x, 0), (x, H)], fill=(0, 0, 0, alpha))

    canvas.paste(overlay, (0,0), mask=overlay)
    
    # 3. TEXT ENGINE (With Safety Clamps)
    draw = ImageDraw.Draw(canvas)
    
    with open(NEWS_DATA, 'r') as f: data = json.load(f)
    headline = data.get('title', "BREAKING NEWS").upper()
    summary = data.get('summary', "Full details available shortly.")
    
    # Layout Constants
    SAFE_LEFT = 60
    SAFE_BOTTOM = H - 100
    TEXT_BLOCK_W = int(W * 0.46)
    
    # A. HEADLINE (Auto-Scale with Min Clamp 68)
    HL_SIZE = 95
    hl_font = None
    hl_lines = []
    
    while True:
        try: hl_font = ImageFont.truetype(FONT_BOLD, HL_SIZE)
        except: hl_font = ImageFont.load_default(); break
        
        test_lines = wrap_text_pixel(headline, hl_font, TEXT_BLOCK_W, draw)
        
        # Stop shrinking if lines fit OR size hits minimum (68)
        if len(test_lines) <= 4 or HL_SIZE <= 68:
            hl_lines = test_lines
            break
        HL_SIZE -= 4
    
    # B. SUMMARY
    SM_SIZE = 38
    try: sm_font = ImageFont.truetype(FONT_REGULAR, SM_SIZE)
    except: sm_font = ImageFont.load_default()
    sm_lines = wrap_text_pixel(summary, sm_font, TEXT_BLOCK_W, draw)
    
    # C. STACK CALCULATIONS
    hl_line_h = int(HL_SIZE * 1.0)
    sm_line_h = int(SM_SIZE * 1.3)
    
    total_hl_h = len(hl_lines) * hl_line_h
    total_sm_h = len(sm_lines) * sm_line_h
    
    # Check Overflow
    max_text_height = H * 0.4
    if (total_hl_h + total_sm_h + 80) > max_text_height:
        sm_lines = sm_lines[:2] # Truncate summary
        total_sm_h = len(sm_lines) * sm_line_h

    # Initial Positions
    summary_y = SAFE_BOTTOM - total_sm_h
    headline_y = summary_y - 30 - total_hl_h
    badge_y = headline_y - 70

    # D. SAFETY CLAMP (Prevent off-screen badge)
    # Ensure badge doesn't go higher than 40px from top
    if badge_y < 40:
        shift = 40 - badge_y
        badge_y += shift
        headline_y += shift
        summary_y += shift

    # 4. RENDER ELEMENTS
    
    # Badge
    draw.rounded_rectangle([(SAFE_LEFT, badge_y), (SAFE_LEFT + 290, badge_y + 55)], radius=5, fill="#D10024")
    try: badge_font = ImageFont.truetype(FONT_BOLD, 32)
    except: badge_font = ImageFont.load_default()
    draw_shadow_text(draw, (SAFE_LEFT + 18, badge_y + 8), "BREAKING NEWS", badge_font, fill="white", offset=1)

    # Headline
    curr_y = headline_y
    for line in hl_lines:
        draw_shadow_text(draw, (SAFE_LEFT, curr_y), line, hl_font, "white", offset=4)
        curr_y += hl_line_h

    # Summary
    curr_y = summary_y
    for line in sm_lines:
        draw_shadow_text(draw, (SAFE_LEFT, curr_y), line, sm_font, "#DDDDDD", offset=2)
        curr_y += sm_line_h

    # Watermark (Professional Align)
    try: wm_font = ImageFont.truetype(FONT_BOLD, 30)
    except: wm_font = ImageFont.load_default()
    
    wm_text = "@IPLTrackX"
    bbox = draw.textbbox((0, 0), wm_text, font=wm_font)
    wm_w = bbox[2] - bbox[0]
    draw.text((W - wm_w - 50, 50), wm_text, font=wm_font, fill=(255, 255, 255, 110))
    
    # 5. INSTAGRAM OPTIMIZATION (The Secret Sauce)
    # A. Contrast Boost
    enhancer = ImageEnhance.Contrast(canvas)
    canvas = enhancer.enhance(1.06)
    
    # B. Micro-Sharpening (Unsharp Mask)
    canvas = canvas.filter(ImageFilter.UnsharpMask(radius=1.2, percent=110, threshold=3))
    
    # C. Save with JPEG Optimization
    canvas.save(FINAL_IMAGE, format="JPEG", quality=95, subsampling=0, optimize=True)
    print(f"✅ DESIGN SAVED: {FINAL_IMAGE}")
    return True

if __name__ == "__main__":
    create_design()
