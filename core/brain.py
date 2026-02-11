import google.generativeai as genai
import json
import os
import time

# --- CONFIGURATION ---
# 🔴 PASTE YOUR API KEY HERE 🔴
API_KEY = "AIzaSyBMsDM7M8BxmrS216fcMIYz68iwS74ZFws"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")

def ai_enhance_strategy(data):
    try:
        genai.configure(api_key=API_KEY)
        
        # SMART LADDER: Try 2.5 -> 1.5 -> Pro
        model = None
        for name in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-pro"]:
            try:
                model = genai.GenerativeModel(name)
                break
            except: continue
            
        if not model:
            print("⚠️ Brain: All AI models failed.")
            return

        prompt = f"""
        Act as a Cricket News Editor.
        Input Headline: "{data['title']}"
        
        Task 1: Rewrite Headline (Max 6 words, Bold, Impactful).
        Task 2: Write a Google Image Search Query. 
           - RULE: Extract ONLY the specific Player Name(s) OR Team Name(s).
           - RULE: Add "Cricket Match Real Photo" at the end.
           - RULE: Do NOT include "India" unless the news is actually about India.
           - Example: "Western Australia wins" -> Query: "Western Australia Cricket Team Match Real Photo"
        
        Output JSON:
        {{
            "new_headline": "...",
            "image_query": "..."
        }}
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip().replace('```json', '').replace('```', '')
        ai_data = json.loads(text)
        
        if ai_data.get('new_headline'): 
            data['title'] = ai_data['new_headline'].upper()
        
        # CRITICAL FIX: Overwrite the default prompt with the specific AI one
        if ai_data.get('image_query'): 
            data['visual_prompt'] = ai_data['image_query']
            print(f"🧠 Visual Query set to: '{data['visual_prompt']}'")
            
        print(f"✅ Brain: Headline Rewritten -> {data['title']}")
            
    except Exception as e:
        print(f"⚠️ Brain Error: {e}")

def run_brain():
    if not os.path.exists(NEWS_DATA_FILE): return False
    with open(NEWS_DATA_FILE, 'r') as f: data = json.load(f)
    print(f"🧠 BRAIN: Analyzing '{data.get('title')}'")

    # CLEAN START: Default to title, but let AI override it completely.
    # Removed the "Indian Cricket Team" fallback line.
    data['visual_prompt'] = data['title'] + " cricket match"
    
    ai_enhance_strategy(data)
    
    with open(NEWS_DATA_FILE, 'w') as f: json.dump(data, f, indent=4)
    return True

if __name__ == "__main__":
    run_brain()
