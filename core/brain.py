import google.generativeai as genai
import json
import os
import re
import time

# --- CONFIGURATION ---
API_KEY = os.environ.get("GEMINI_API_KEY", "PASTE_YOUR_KEY_HERE_IF_LOCAL")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")

def clean_text(text):
    """Removes all Markdown stars, hashes, and underscores."""
    if not text: return ""
    return re.sub(r'[\*_#]', '', text).strip()

def extract_json(text):
    """Robustly extracts JSON object from text using regex."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None

def clamp_headline(text):
    """Forces headline to be max 5 words and uppercase."""
    clean = clean_text(text)
    words = clean.upper().split()
    return " ".join(words[:5])

def clamp_summary(text):
    """Forces exactly 2 sentences and max 25 words."""
    clean = clean_text(text)
    # Split by . ! ? to find sentence boundaries
    sentences = re.split(r'[.!?]+', clean)
    # Remove empty strings and whitespace
    sentences = [s.strip() for s in sentences if s.strip()]
    # Keep only the first 2 sentences
    sentences = sentences[:2]
    
    combined = ". ".join(sentences)
    # Hard clamp to 25 words
    words = combined.split()[:25]
    s = " ".join(words)
    
    # Ensure it ends with punctuation
    if s and s[-1] not in ['.', '!', '?']:
        s += "."
    return s

def clean_image_query(text):
    """Removes special chars for cleaner search results."""
    clean = clean_text(text)
    # Remove anything that isn't a letter, number, or space
    return re.sub(r'[^a-zA-Z0-9\s]', '', clean)

def run_brain():
    if not os.path.exists(NEWS_DATA_FILE):
        print("❌ Brain Error: Missing news data file.")
        return False

    with open(NEWS_DATA_FILE, 'r') as f:
        data = json.load(f)

    print(f"🧠 BRAIN: Processing '{data.get('title', 'Unknown')}'")

    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        You are a professional TV sports broadcast editor (Star Sports style).
        
        INPUT NEWS: "{data['title']}"
        
        STRICT RULES:
        1. HEADLINE: Max 4-5 words. STRONG, PUNCHY, UPPERCASE. (e.g., "INDIA DOMINATE TEST").
        2. SUMMARY: Exactly 2 short sentences. Max 25 words total. Professional broadcast tone. No "Read more".
        3. IMAGE_QUERY: Specific Team names + "cricket match action" + key player name.
        
        RETURN STRICT JSON ONLY:
        {{
            "headline": "...",
            "summary": "...",
            "image_query": "..."
        }}
        """

        ai_data = None
        
        # Retry Loop (2 Attempts)
        for attempt in range(2):
            try:
                # Added Timeout Protection (20 seconds)
                resp = model.generate_content(prompt, request_options={"timeout": 20})
                ai_data = extract_json(resp.text)
                
                # Validation: Check if headline exists
                if ai_data and ai_data.get("headline"):
                    break 
                else:
                    raise ValueError("AI returned empty headline")
                    
            except Exception as e:
                print(f"⚠️ Brain: Attempt {attempt+1} failed ({e}). Retrying...")
                time.sleep(1)

        if not ai_data:
            print("❌ Brain: AI failed after retries. Using fallback data.")
            ai_data = {
                "headline": clamp_headline(data['title']),
                "summary": "Full match details and score updates available on our website.",
                "image_query": data['title'] + " cricket"
            }

        # --- SAFETY CLAMPING & PROCESSING ---
        headline = clamp_headline(ai_data.get("headline", data["title"]))
        summary = clamp_summary(ai_data.get("summary", ""))
        image_query = clean_image_query(ai_data.get("image_query", headline))

        # --- DUPLICATE GUARD ---
        # If the AI generated the exact same headline as the previous run, add a tag
        if headline == data.get("last_headline"):
            headline += " UPDATE"

        # --- SAVE DATA ---
        data["title"] = headline
        data["summary"] = summary
        data["visual_prompt"] = image_query
        data["last_headline"] = headline # Store for next time check

        with open(NEWS_DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        print(f"✅ Brain Success: {headline}")
        print(f"   Summary: {summary}")
        return True

    except Exception as e:
        print(f"❌ Brain Critical Error: {e}")
        return False

if __name__ == "__main__":
    run_brain()
