from PIL import Image, ImageDraw, ImageFont
import json

# ------------ LOAD FORMATTED CONTENT ------------
with open("formatted_content.json", "r") as f:
    content = json.load(f)

headline = content.get("headline", "")
sub = content.get("sub", "")
facts = content.get("facts", [])

# ------------ CANVAS (Instagram 4:5) ------------
WIDTH = 1080
HEIGHT = 1350

img = Image.new("RGB", (WIDTH, HEIGHT), (15, 15, 18))
draw = ImageDraw.Draw(img)

# ------------ FONTS ------------
title_font = ImageFont.truetype("fonts/LeagueSpartan-Bold.ttf", 80)
sub_font = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 48)
fact_font = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 44)
small_font = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 30)

# ------------ SAFE ZONES ------------
LEFT_MARGIN = 80
RIGHT_MARGIN = 1000
TOP_SAFE = 120
BOTTOM_SAFE = 1230

y = TOP_SAFE

# ------------ HEADLINE ------------
draw.text((LEFT_MARGIN, y), headline, font=title_font, fill=(255, 255, 255))
y += 200

# ------------ SUB HEADLINE ------------
draw.text((LEFT_MARGIN, y), sub, font=sub_font, fill=(210, 210, 210))
y += 140

# ------------ FACT BLOCK ------------
for fact in facts:
    draw.text((LEFT_MARGIN, y), fact, font=fact_font, fill=(230, 230, 230))
    y += 110

# ------------ SMALL NAME (NO LOGO STYLE) ------------
draw.text((WIDTH - 260, HEIGHT - 80), "IPLTrackX", font=small_font, fill=(170, 170, 170))

# ------------ SAVE ------------
img.save("output/frame_test.png")
print("Frame generated: output/frame_test.png")
