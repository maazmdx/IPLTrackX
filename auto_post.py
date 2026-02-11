import json
import requests
from google import genai
from PIL import Image, ImageDraw, ImageFont
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ---------- FETCH MATCH DATA ----------
url = "https://site.web.api.espn.com/apis/v2/sports/cricket/scoreboard"

try:
    r = requests.get(url, timeout=10)
    data = r.json()
except:
    data = {}

matches = data.get("events", [])

ipl_matches = []

for m in matches:
    name = m.get("name", "").lower()
    comp = m.get("season", {}).get("slug", "").lower()

    # IPL detection (safe)
    if "ipl" in name or "indian premier league" in name or "ipl" in comp:
        ipl_matches.append(m)

# Fallback if no IPL match found
if not ipl_matches:
    match_name = "IPL Update"
    status = "No IPL match currently"
else:
    match = ipl_matches[0]
    match_name = match.get("name", "IPL Match")
    status = match.get("status", {}).get("type", {}).get("description", "Unknown")

# Safe fallback if no match
if not matches:
    match_name = "IPL Update"
    status = "No live match currently"
else:
    match = matches[0]
    match_name = match.get("name", "Unknown Match")
    status = match.get("status", {}).get("type", {}).get("description", "Unknown")

# ---------- DUPLICATE CHECK ----------
try:
    with open("data/posted_log.json", "r") as f:
        log = json.load(f)
except:
    log = {}

if log.get("last_match") == match_name:
    print("No new update. Skipping post.")
    exit()

# ---------- AI CONTENT ----------
API_KEY = "AIzaSyAr0HC-K_d5Au3tLKw4O5FY8xcYKiHLGcQ"
client = genai.Client(api_key=API_KEY)

prompt = f"""
You are generating content for IPLTrackX sports media page.

Match: {match_name}
Status: {status}

Generate structured output:

1. MATCH RESULT (short headline)
2. PLAYER OF THE MATCH
3. TOP BATTER
4. TOP BOWLER
5. SHORT MATCH SUMMARY

Keep it professional, short, sports-media style.
"""


response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt
)

ai_text = response.text if response.text else "IPL latest update."

# ---------- TEAM GRADIENT COLORS ----------
team_colors = {
    "rcb": ((213, 0, 0), (0, 0, 0)),
    "mi": ((0, 75, 160), (0, 28, 61)),
    "csk": ((255, 215, 0), (255, 140, 0)),
    "kkr": ((58, 12, 163), (201, 162, 39)),
    "srh": ((255, 106, 0), (0, 0, 0)),
    "dc": ((23, 68, 155), (239, 28, 37)),
    "rr": ((255, 105, 180), (30, 144, 255)),
    "pbks": ((237, 28, 36), (192, 192, 192)),
    "gt": ((11, 31, 58), (201, 162, 39)),
    "lsg": ((0, 180, 216), (255, 140, 0))
}

# Default fallback
color1, color2 = (20, 20, 20), (40, 40, 40)

for team in team_colors:
    if team in match_name.lower():
        color1, color2 = team_colors[team]
        break

# ---------- IMAGE GENERATION ----------
img = Image.new("RGB", (1080, 1080))
for y in range(1080):
    ratio = y / 1080
    r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
    g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
    b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
    for x in range(1080):
        img.putpixel((x, y), (r, g, b))

# ---- Load player image (placeholder for now) ----
player_img_path = "assets/player.png"   # temporary test image

try:
    player = Image.open(player_img_path).convert("RGBA")

    player_ratio = player.width / player.height
    target_height = 1080
    target_width = int(player_ratio * target_height)

    player = player.resize((target_width, target_height))

    # If wider than left zone → crop center
    if target_width > 480:
        left = (target_width - 480) // 2
        player = player.crop((left, 0, left + 480, 1080))

    # Create fade mask (left strong → right transparent)
    mask = Image.new("L", (480, 1080))
    for x in range(480):
        fade = int(255 * (1 - (x / 480)))
        for y in range(1080):
            mask.putpixel((x, y), fade)

    player.putalpha(mask)
    img.paste(player, (0, 0), player)

except Exception as e:
    print("Player image skipped:", e)

draw = ImageDraw.Draw(img)

title_font = ImageFont.truetype("fonts/LeagueSpartan-Bold.ttf", 55)
body_font = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 42)
small_font = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 28)

# Small logo (fixed)
draw.text((900, 40), "IPLTrackX", font=small_font, fill=(230, 230, 230))

# Facts layout (no border)
draw.text((520, 200), match_name, font=title_font, fill=(255, 255, 255))
draw.text((520, 290), status, font=body_font, fill=(230, 230, 230))
draw.text((520, 420), ai_text[:260], font=body_font, fill=(255, 255, 255))
image_path = "output/auto_post.png"
img.save(image_path)


# ---------- DRIVE UPLOAD ----------
SCOPES = ['https://www.googleapis.com/auth/drive.file']
import os
from google.oauth2.credentials import Credentials

TOKEN_FILE = "data/token.json"

creds = None

if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file('data/oauth.json', SCOPES)
    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())

drive_service = build('drive', 'v3', credentials=creds)

FOLDER_ID = "130zHH0Khnlbz6ki3F3b_NQTjMy64s8cF"

file_metadata = {
    'name': 'auto_post.png',
    'parents': [FOLDER_ID]
}

media = MediaFileUpload(image_path, mimetype='image/png')

file = drive_service.files().create(
    body=file_metadata,
    media_body=media,
    fields='id'
).execute()

print("Uploaded:", file.get("id"))

# ---------- UPDATE LOG ----------
log["last_match"] = match_name
with open("data/posted_log.json", "w") as f:
    json.dump(log, f, indent=2)

print("Automation completed successfully.")

