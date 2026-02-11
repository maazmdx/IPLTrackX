from PIL import Image, ImageDraw, ImageFont
import os

# Create blank image (dark background)
img = Image.new("RGB", (1080, 1080), (15, 15, 15))
draw = ImageDraw.Draw(img)

# Load font
font_path = "fonts/LeagueSpartan-Bold.ttf"

if not os.path.exists(font_path):
    print("Font not found. Check fonts folder.")
    exit()

title_font = ImageFont.truetype(font_path, 120)

# Add text
text = "IPLTrackX"
bbox = draw.textbbox((0, 0), text, font=title_font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

x = (1080 - text_width) // 2
y = (1080 - text_height) // 2

draw.text((x, y), text, font=title_font, fill=(255, 255, 255))

# Save image
output_path = "output/test_post.png"
img.save(output_path)

print("SUCCESS: Image generated at", output_path)
