import os

# Define the correct header that works for ALL agents
CORRECT_HEADER = """import os
import sys
import json

# Ensure we can find other core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- ENTERPRISE PATH CONFIGURATION ---
# Get the Project Root Directory (one level up from 'core')
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Define Standard Folders
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# Define Standard Files
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
NEWS_IMAGE_FILE = os.path.join(TEMP_DIR, "news_image.jpg")
FINAL_IMAGE = os.path.join(BASE_DIR, "final_post.jpg")
FONT_PATH = os.path.join(BASE_DIR, "SportsFont.ttf")
"""

def patch_file(filename):
    filepath = os.path.join("core", filename)
    if not os.path.exists(filepath):
        print(f"⚠️ Skipping {filename} (Not found)")
        return

    with open(filepath, 'r') as f:
        content = f.read()

    # We look for the marker where configuration usually starts
    # and replace the top chunk with our new robust header
    
    # Split content to keep imports if possible, but for safety, 
    # we will keep the original specific imports and replace the config block.
    
    # NAIVE REPLACEMENT: We will just replace the old path definitions
    # This covers the specific error you saw.
    
    new_content = content.replace(
        'NEWS_DATA_FILE = os.path.join(TEMP_DIR, "data/design_data.json")',
        'NEWS_DATA_FILE = os.path.join(BASE_DIR, "data", "design_data.json")'
    )
    
    new_content = new_content.replace(
        'HISTORY_FILE = os.path.join(BASE_DIR, "data/history.json")',
        'HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.json")'
    )

    # Force correct BASE_DIR definition if it was relying on os.getcwd()
    if "BASE_DIR = os.getcwd()" in new_content:
        new_content = new_content.replace(
            "BASE_DIR = os.getcwd()",
            "BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))"
        )

    with open(filepath, 'w') as f:
        f.write(new_content)
    print(f"✅ Patched {filename}")

# Run patch on critical files
files_to_fix = ["hunter.py", "brain.py", "artist.py", "critic.py", "publisher.py"]

for f in files_to_fix:
    patch_file(f)

print("\n🚀 REPAIR COMPLETE. Try running main.py now.")
