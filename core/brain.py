import google.generativeai as genai
import json
import os
import re

# --- CONFIGURATION ---
API_KEY = os.environ.get("GEMINI_API_KEY", "PASTE_KEY_HERE_IF_LOCAL")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")

def clean_text(text):
    if not text: return ""
    return re.sub(r'[\*_#]', '', text).strip()

def ai_enhance_strategy(data):
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        prompt = f"""
        Act as a Lead Sports Editor.
        Input News: "{data['title']}"
        
        Task 1: Write a HEADLINE (Max 6 words, Punchy, Uppercase).
        Task 2: Write a SUMMARY (Max 15 words, Lowercase sentence case).
        Task 3: Create an Image Search Query (Team names + 'match action').

        Output JSON:
        {{
            "headline": "...",
            "summary": "...",
            "image_query": "..."
        }}
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip().replace('```json', '').replace('```', '')
        ai_data = json.loads(text)
        
        # Update Data Structure
        data['title'] = clean_text(ai_data.get('headline', data['title'])).upper()
        data['summary'] = clean_text(ai_data.get('summary', ''))
        data['visual_prompt'] = clean_text(ai_data.get('image_query', data['title']))
            
        print(f"✅ Brain: Headline -> {data['title']}")
        print(f"✅ Brain: Summary  -> {data['summary']}")
            
    except Exception as e:
        print(f"⚠️ Brain Error: {e}")
        # Fallback if AI fails
        data['summary'] = "Read the full story on our page."

def run_brain():
    if not os.path.exists(NEWS_DATA_FILE): return False
    with open(NEWS_DATA_FILE, 'r') as f: data = json.load(f)
    print(f"🧠 BRAIN: Analyzing '{data.get('title')}'")

    ai_enhance_strategy(data)
    
    with open(NEWS_DATA_FILE, 'w') as f: json.dump(data, f, indent=4)
    return True

if __name__ == "__main__":
    run_brain()
