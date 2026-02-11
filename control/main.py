import os
import sys
import time
import datetime
import json
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from control.logger import log_event, log_error
from control.error_handler import run_protected, check_json_integrity

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")
NEWS_IMAGE = os.path.join(TEMP_DIR, "news_image.jpg")
CUTOUT_IMAGE = os.path.join(TEMP_DIR, "player_cutout.png")

CYCLE_INTERVAL_HOURS = 1

def run_module(module_path, args=""):
    cmd = f"{sys.executable} -m {module_path} {args}"
    return os.system(cmd) == 0

def run_pipeline():
    start_time = datetime.datetime.now()
    log_event("SYSTEM", f"🚀 CYCLE START: {start_time.strftime('%H:%M:%S')}")
    
    # 1. CLEANUP
    if os.path.exists(NEWS_DATA): os.remove(NEWS_DATA)
    if os.path.exists(NEWS_IMAGE): os.remove(NEWS_IMAGE)
    if os.path.exists(CUTOUT_IMAGE): 
        try: os.remove(CUTOUT_IMAGE)
        except: pass

    # 2. HUNTER
    log_event("PIPELINE", "Step 1: Hunting News...")
    if not run_protected("Hunter(Text)", run_module, "core.hunter", "text"):
        log_error("E01", "Hunter", "No news found. Sleeping.")
        return False

    # 3. BRAIN
    log_event("PIPELINE", "Step 2: Developing Strategy...")
    if not run_protected("Brain", run_module, "core.brain"): return False

    # 4. VISUAL HUNT (Serper -> Backup)
    log_event("PIPELINE", "Step 3: Searching Visuals (Serper)...")
    if not run_module("core.serper_agent"):
        log_event("PIPELINE", "⚠️ Serper failed. Switching to Backup...")
        if not run_protected("Hunter(Backup)", run_module, "core.hunter", "image"):
             log_error("CRITICAL", "Visuals", "No images found.")
             return False

    # 5. DESIGN
    log_event("PIPELINE", "Step 5: Design...")
    # CRITICAL FIX: If Artist fails, ensure we don't crash next time
    if not run_protected("Artist", run_module, "core.artist", "auto"): 
        if os.path.exists(NEWS_IMAGE): os.remove(NEWS_IMAGE) # Delete corrupt image
        return False
    
    # 6. CAPTION & PUBLISH
    log_event("PIPELINE", "Step 6: Captioning...")
    run_protected("Critic", run_module, "core.critic")

    log_event("PIPELINE", "Step 7: Publishing...")
    if not run_protected("Publisher", run_module, "core.publisher"): return False

    log_event("PIPELINE", "Step 8: Learning...")
    run_module("core.analyst")

    log_event("SYSTEM", "✨ CYCLE COMPLETE.")
    return True

if __name__ == "__main__":
    print("\n" + "="*50)
    print(f"   🏏 IPLTrackX ENTERPRISE v7.0 (Anti-Crash)   ")
    print("="*50)
    
    while True:
        try:
            run_pipeline()
        except Exception as e:
            log_error("CRITICAL", "MainLoop", f"Crash Prevented: {e}")
        
        print(f"\nzzZ... Sleeping {CYCLE_INTERVAL_HOURS} hour...")
        time.sleep(CYCLE_INTERVAL_HOURS * 3600)
