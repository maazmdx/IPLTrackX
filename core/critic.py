import google.generativeai as genai
import json
import os
import sys

# --- CONFIGURATION ---
# 🔴 PASTE YOUR API KEY HERE 🔴
API_KEY = "AIzaSyBMsDM7M8BxmrS216fcMIYz68iwS74ZFws"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")

# ✅ FIX: Save to data/caption.txt so publisher.py can find it
CAPTION_FILE = os.path.join(DATA_DIR, "caption.txt")

def clean_markdown(text):
    return text.replace('**', '').replace('__', '').strip()

def generate_caption_ai(data):
    try:
        genai.configure(api_key=API_KEY)
        
        # SMART LADDER: Try the best model first
        model = None
        candidates = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"]
        
        for name in candidates:
            try:
                model = genai.GenerativeModel(name)
                # Test call to ensure model is valid
                model.generate_content("test") 
                print(f"📝 CRITIC: Using Model -> {name}")
                break
            except:
                continue
                
        if not model:
            raise Exception("All AI models failed.")

        prompt = f"""
        Act as a Social Media Manager.
        News: "{data['title']}"
        Summary: "{data.get('summary', '')}"
        Task: Write a short, engaging Instagram caption with hashtags.
        Constraint: Do NOT use markdown bold (**). Use normal text.
        Output: Just the caption.
        """
        response = model.generate_content(prompt)
        print("📝 CRITIC: Caption Generated via AI.")
        return clean_markdown(response.text)
        
    except Exception as e:
        print(f"📝 CRITIC: AI Failed ({e}). Using Template.")
        return f"""
BREAKING NEWS 🚨

{clean_markdown(data['title'])}

#Cricket #IPL #SportsUpdate #CricketNews
"""

def run_critic():
    if not os.path.exists(NEWS_DATA_FILE): return False
    with open(NEWS_DATA_FILE, 'r') as f: data = json.load(f)

    print("📝 CRITIC: Generating Social Caption...")
    # Clean the title for safety
    if 'title' in data:
        data['title'] = clean_markdown(data['title'])

    caption = generate_caption_ai(data)
    
    # Ensure data directory exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    with open(CAPTION_FILE, 'w') as f:
        f.write(caption)
        
    print(f"📝 CRITIC: Caption Saved Successfully to {CAPTION_FILE}")
    return True

if __name__ == "__main__":
    if run_critic(): sys.exit(0)
    else: sys.exit(1)
