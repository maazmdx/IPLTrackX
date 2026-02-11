import google.generativeai as genai
import json
import os
import re

API_KEY = os.environ.get("GEMINI_API_KEY", "PASTE_KEY_HERE")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")

def clean_text(text): return re.sub(r'[\*_#]', '', text).strip() if text else ""

def run_brain():
    if not os.path.exists(NEWS_DATA_FILE): return False
    with open(NEWS_DATA_FILE, 'r') as f: data = json.load(f)
    print(f"🧠 BRAIN: Analyzing '{data.get('title')}'")

    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""
        Act as a Sports Editor.
        Input News: "{data['title']}"
        
        Task 1: HEADLINE (Max 6 words, Uppercase, Punchy).
        Task 2: SUMMARY (20-25 words. Engaging. No "Read more").
        Task 3: IMAGE QUERY (Team names + 'match action').

        Output JSON: {{"headline": "...", "summary": "...", "image_query": "..."}}
        """
        
        resp = model.generate_content(prompt)
        ai_data = json.loads(resp.text.replace('```json', '').replace('```', ''))
        
        data['title'] = clean_text(ai_data.get('headline', data['title'])).upper()
        data['summary'] = clean_text(ai_data.get('summary', ''))
        data['visual_prompt'] = clean_text(ai_data.get('image_query', data['title']))
        
        print(f"✅ Brain: Headline -> {data['title']}")
    except: pass
    
    with open(NEWS_DATA_FILE, 'w') as f: json.dump(data, f, indent=4)
    return True

if __name__ == "__main__":
    run_brain()
