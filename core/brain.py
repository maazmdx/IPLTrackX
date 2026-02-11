import google.generativeai as genai
import json
import os
import re
import time

# ================= CONFIG =================
API_KEY = os.environ.get("GEMINI_API_KEY", "")
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.txt")

# ================= HELPERS =================

def normalize(text):
    return re.sub(r'[^a-z0-9]', '', text.lower()) if text else ""

def clean_text(text):
    return re.sub(r'[\*_#]', '', text).strip() if text else ""

def clamp_headline(text):
    words = clean_text(text).upper().split()
    return " ".join(words[:5])

def clamp_summary(text):
    text = clean_text(text)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentences = sentences[:2]
    combined = ". ".join(sentences)
    words = combined.split()[:25]
    s = " ".join(words)
    if s and s[-1] not in ".!?":
        s += "."
    return s

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            return None
    return None


# ================= MAIN BRAIN =================

def run_brain():

    if not os.path.exists(NEWS_DATA_FILE):
        print("❌ Brain: No news file.")
        return False

    with open(NEWS_DATA_FILE, "r") as f:
        data = json.load(f)

    original_title = data.get("title", "")
    print(f"🧠 BRAIN: Processing '{original_title}'")

    try:
        genai.configure(api_key=API_KEY)

        # Model ladder (auto fallback)
        model = None
        for name in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-pro"]:
            try:
                model = genai.GenerativeModel(name)
                break
            except:
                continue

        if not model:
            print("❌ Brain: No Gemini model available.")
            return False

        prompt = f"""
You are a professional TV cricket broadcast editor.

INPUT NEWS:
"{original_title}"

STRICT RULES:
1. HEADLINE → Max 4-5 words, STRONG, UPPERCASE.
2. SUMMARY → Exactly 2 short sentences, max 25 words.
3. IMAGE_QUERY → Player name + Team + "cricket match action".

RETURN JSON ONLY:
{{
 "headline": "...",
 "summary": "...",
 "image_query": "..."
}}
"""

        ai_data = None

        # Retry (2 attempts)
        for attempt in range(2):
            try:
                resp = model.generate_content(prompt, request_options={"timeout": 20})
                ai_data = extract_json(resp.text)
                if ai_data and ai_data.get("headline"):
                    break
            except Exception as e:
                print(f"⚠️ Brain retry {attempt+1}: {e}")
                time.sleep(1)

        # Fallback if AI fails
        if not ai_data:
            print("⚠️ Brain fallback used.")
            ai_data = {
                "headline": original_title,
                "summary": original_title,
                "image_query": original_title + " cricket"
            }

        # Clamp & clean
        headline = clamp_headline(ai_data.get("headline", original_title))
        summary = clamp_summary(ai_data.get("summary", original_title))
        image_query = clean_text(ai_data.get("image_query", headline))

        # ================= DUPLICATE BLOCK =================
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history = set(line.strip() for line in f.readlines())

            if normalize(headline) in history:
                print("🚫 Duplicate headline detected. Stop.")
                return False

        # ================= SAVE =================
        data["title"] = headline
        data["summary"] = summary
        data["visual_prompt"] = image_query

        with open(NEWS_DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        print(f"✅ Brain Success → {headline}")
        print(f"   Summary → {summary}")
        return True

    except Exception as e:
        print(f"❌ Brain Critical Error: {e}")
        return False


# ================= ENTRY =================

if __name__ == "__main__":
    run_brain()
