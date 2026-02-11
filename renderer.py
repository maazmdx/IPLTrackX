from PIL import Image, ImageDraw, ImageFont
import json

# -------- LOAD DESIGN + CONTENT --------
with open("brain_output.json", "r") as f:
    design = json.load(f)

with open("formatted_content.json", "r") as f:
    content = json.load(f)

template = design.get("template", "card")

headline = content.get("headline", "")
sub = content.get("sub", "")
facts = content.get("facts", [])

# -------- CANVAS --------
WIDTH, HEIGHT = 1080, 1350
img = Image.new("RGB", (WIDTH, HEIGHT), (12, 12, 16))
draw = ImageDraw.Draw(img)

# -------- FONTS --------
title_font = ImageFont.truetype("fonts/LeagueSpartan-Bold.ttf", 78)
sub_font = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 48)
fact_font = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 42)
small_font = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 28)

# -------- TEMPLATE ROUTER --------

if template == "winner":
    # Result Template
    draw.text((80, 150), headline, font=title_font, fill=(255, 255, 255))
    draw.text((80, 300), sub, font=sub_font, fill=(210, 210, 210))

    y = 500
    for fact in facts:
        draw.text((80, y), fact, font=fact_font, fill=(230, 230, 230))
        y += 110

elif template == "hybrid_vs":
    # VS Hybrid Layout
    draw.text((80, 150), headline, font=title_font, fill=(255, 255, 255))
    draw.text((420, 350), "VS", font=title_font, fill=(180, 180, 180))

    draw.text((80, 700), sub, font=sub_font, fill=(210, 210, 210))

    y = 880
    for fact in facts:
        draw.text((80, y), fact, font=fact_font, fill=(230, 230, 230))
        y += 100

elif template == "hero":
    # Player Highlight
    draw.text((80, 150), headline, font=title_font, fill=(255, 255, 255))
    draw.text((80, 350), sub, font=sub_font, fill=(210, 210, 210))

    y = 550
    for fact in facts:
        draw.text((80, y), fact, font=fact_font, fill=(230, 230, 230))
        y += 110

elif template == "grid":
    # Stats Card
    draw.text((80, 150), headline, font=title_font, fill=(255, 255, 255))

    y = 350
    for fact in facts:
        draw.text((80, y), fact, font=fact_font, fill=(230, 230, 230))
        y += 140

else:
    # News / Fallback Card
    draw.text((80, 200), headline, font=title_font, fill=(255, 255, 255))
    draw.text((80, 380), sub, font=sub_font, fill=(210, 210, 210))

    y = 580
    for fact in facts:
        draw.text((80, y), fact, font=fact_font, fill=(230, 230, 230))
        y += 120

# -------- SMALL BRAND TEXT --------
draw.text((900, 1280), "IPLTrackX", font=small_font, fill=(160, 160, 160))

# -------- SAVE --------
img.save("output/render_test.png")
print("Rendered:", template)
