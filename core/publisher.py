import os
import json
import hashlib
from datetime import datetime

# ================= PATHS =================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")

NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")

# Your system saves image here (from artist log)
FINAL_IMAGE = os.path.join(BASE_DIR, "final_post.jpg")

# Your critic saves caption here
CAPTION_FILE = os.path.join(DATA_DIR, "caption.txt")

# Spam lock file
POST_LOG_FILE = os.path.join(DATA_DIR, "posted.json")


# ================= HASH GENERATOR =================
def generate_post_hash(image_path, caption):
    h = hashlib.sha256()

    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            h.update(f.read())

    h.update(caption.encode())
    return h.hexdigest()


# ================= LOAD POST HISTORY =================
def load_post_history():
    if not os.path.exists(POST_LOG_FILE):
        return set()

    try:
        with open(POST_LOG_FILE, "r") as f:
            data = json.load(f)
            return set(data)
    except:
        return set()


# ================= SAVE POST HISTORY =================
def save_post_history(post_hash):
    history = load_post_history()
    history.add(post_hash)

    with open(POST_LOG_FILE, "w") as f:
        json.dump(list(history), f, indent=4)


# ================= MAIN PUBLISHER =================
def run_publisher():

    print("🚀 Publisher: Preparing post...")

    # ---------------- IMAGE CHECK ----------------
    if not os.path.exists(FINAL_IMAGE):
        print("❌ Image not found:", FINAL_IMAGE)
        return False

    # ---------------- CAPTION CHECK ----------------
    if not os.path.exists(CAPTION_FILE):
        print("❌ Caption file not found:", CAPTION_FILE)
        return False

    with open(CAPTION_FILE, "r") as f:
        caption = f.read().strip()

    if not caption:
        print("❌ Caption empty.")
        return False

    # ---------------- LOAD TITLE ----------------
    title = ""
    if os.path.exists(NEWS_DATA_FILE):
        try:
            with open(NEWS_DATA_FILE, "r") as f:
                data = json.load(f)
                title = data.get("title", "")
        except:
            pass

    # ================= SPAM CHECK =================
    post_hash = generate_post_hash(FINAL_IMAGE, caption)
    history = load_post_history()

    if post_hash in history:
        print("⚠️ DUPLICATE POST BLOCKED (Spam Protection)")
        return False

    # ================= SAVE OUTPUT FOR MAKE =================
    output = {
        "image": FINAL_IMAGE,
        "caption": caption,
        "title": title,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    out_file = os.path.join(DATA_DIR, "final_post.json")
    with open(out_file, "w") as f:
        json.dump(output, f, indent=4)

    # ================= LOCK THIS POST =================
    save_post_history(post_hash)

    print("✅ Publisher: Post Ready & Locked (No Spam)")
    return True


# ================= ENTRY =================
if __name__ == "__main__":
    run_publisher()
