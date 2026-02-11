import google.generativeai as genai
import json
import os
import re

# --- CONFIGURATION ---
# Looks for the key in the cloud environment
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBMsDM7M8BxmrS216fcMIYz68iwS74ZFws")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")

def clean_text(text):
    """Removes all Markdown stars and underscores."""
    if not text: return ""
    return re.sub(r'[\*_]', '', text).strip()

def ai_enhance_strategy(data):
    try:
        genai.configure(api_key=API_KEY)
        
        # SMART LADDER: Try the best model first
        model = None
        candidates = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-pro"]
        for name in candidates:
            try:
                model = genai.GenerativeModel(name)
                model.generate_content("test") # Test connection
                break
            except: continue
            
        if not model:
            print("⚠️ Brain: All AI models failed. Using original headline.")
            return

        prompt = f"""
        Act as a Senior Sports Editor for a TV channel.
        Input Headline: "{data['title']}"
        
        Task 1: Rewrite Headline.
           - Max 7 words.
           - MUST be Punchy, Urgent, and Impactful.
           - STRICTLY PLAIN TEXT. NO markdown, NO stars (**), NO quotes.
        
        Task 2: Create a Google Image Search Query.
           - Extract the main Team(s) and Player(s).
           - Add "match action real photo high resolution".
           - Exclude generic words like "report", "interview".

        Output JSON:
        {{
            "new_headline": "...",
            "image_query": "..."
        }}
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip().replace('```json', '').replace('```', '')
        ai_data = json.loads(text)
        
        #Apply the strict cleaner
        if ai_data.get('new_headline'): 
            data['title'] = clean_text(ai_data['new_headline'].upper())
        
        if ai_data.get('image_query'): 
            data['visual_prompt'] = clean_text(ai_data['image_query'])
            
        print(f"✅ Brain: New Headline -> {data['title']}")
            
    except Exception as e:
        print(f"⚠️ Brain Error: {e}. Using original.")

def run_brain():
    if not os.path.exists(NEWS_DATA_FILE): return False
    with open(NEWS_DATA_FILE, 'r') as f: data = json.load(f)
    print(f"🧠 BRAIN: Analyzing '{data.get('title')}'")

    # Default fallback
    data['visual_prompt'] = clean_text(data['title']) + " cricket match action"
    
    ai_enhance_strategy(data)
    
    with open(NEWS_DATA_FILE, 'w') as f: json.dump(data, f, indent=4)
    return True

if __name__ == "__main__":
    run_brain()
