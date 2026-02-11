import json
import os
import requests
import time

# --- CONFIGURATION ---
BASE_DIR = os.getcwd()
TEMP_DIR = os.path.join(BASE_DIR, "temp")
DESIGN_JSON = os.path.join(TEMP_DIR, "design_data.json")
NEWS_IMAGE = os.path.join(TEMP_DIR, "news_image.jpg")

def download_image(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        if response.status_code == 200:
            with open(NEWS_IMAGE, 'wb') as out_file:
                out_file.write(response.content)
            print("✅ New Image Downloaded.")
            return True
    except Exception as e:
        print(f"❌ Download Failed: {e}")
        return False

def manual_fix():
    if not os.path.exists(DESIGN_JSON):
        print("❌ No active post found to fix. Run main.py first.")
        return

    # 1. Load Current Data
    with open(DESIGN_JSON, 'r') as f:
        data = json.load(f)
    
    print("\n🛠️  IPLTrackX DIRECTOR'S MODE 🛠️")
    print("--------------------------------")
    print(f"1. Headline:  {data.get('title')}")
    print(f"2. Color:     {data.get('theme_color')}")
    print("--------------------------------")

    # 2. Ask for Changes
    new_title = input("👉 Enter New Headline (or press Enter to keep): ").strip()
    if new_title:
        data['title'] = new_title.upper()

    new_color = input("👉 Enter New Hex Color (e.g. #FF0000) (or Enter to keep): ").strip()
    if new_color:
        data['theme_color'] = new_color

    new_image_url = input("👉 Paste New Image URL (or Enter to keep): ").strip()
    if new_image_url:
        print("⬇️  Downloading new image...")
        download_image(new_image_url)

    # 3. Save Updates
    with open(DESIGN_JSON, 'w') as f:
        json.dump(data, f, indent=4)
    
    print("\n🔄 Regenerating Image...")
    os.system("python designer.py")
    
    # Optional: Run Boss Check again
    print("👮‍♂️ Asking the Boss...")
    exit_code = os.system("python boss.py")
    
    if exit_code == 0:
        print("☁️  Uploading to Drive...")
        os.system("python drive.py")
        print("\n✅ FIXED & UPLOADED!")
    else:
        print("\n❌ Boss Rejected the Fix. Try changing the headline length.")

if __name__ == "__main__":
    manual_fix()
