import os
import sys
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from control.logger import log_event, log_error
from control.error_handler import run_protected

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
NEWS_DATA = os.path.join(DATA_DIR, "design_data.json")
NEWS_IMAGE = os.path.join(TEMP_DIR, "news_image.jpg")
CUTOUT_IMAGE = os.path.join(TEMP_DIR, "player_cutout.png")


def run_module(module_path, args=""):
    cmd = f"{sys.executable} -m {module_path} {args}"
    return os.system(cmd) == 0


def run_pipeline():
    start_time = datetime.datetime.now()
    log_event("SYSTEM", f"🚀 CYCLE START: {start_time.strftime('%H:%M:%S')}")

    # ---------- CLEANUP ----------
    if os.path.exists(NEWS_DATA):
        os.remove(NEWS_DATA)
    if os.path.exists(NEWS_IMAGE):
        os.remove(NEWS_IMAGE)
    if os.path.exists(CUTOUT_IMAGE):
        try:
            os.remove(CUTOUT_IMAGE)
        except:
            pass

    # ---------- HUNTER ----------
    log_event("PIPELINE", "Step 1: Hunting News...")
    hunter_ok = run_module("core.hunter")
    if hunter_ok:
        log_event("PIPELINE", "Hunter found usable news content.")
    else:
        log_event("PIPELINE", "No VIP/priority news. Switching to fallback content engines...")
        if not run_module("core.fallback_pipeline"):
            log_error("E01", "Fallback", "All fallback engines failed to produce content.")
            return False

    # ---------- BRAIN ----------
    log_event("PIPELINE", "Step 2: Brain...")
    if not run_module("core.brain"):
        log_event("SYSTEM", "🛑 Duplicate/Rejected → EXIT")
        return False

    # ---------- VISUAL ----------
    log_event("PIPELINE", "Step 3: Visual Search...")
    run_module("core.serper_agent")

    # ---------- DESIGN ----------
    log_event("PIPELINE", "Step 4: Design...")
    if not run_module("core.artist"):
        log_error("E04", "Artist", "Design failed.")
        return False

    # ---------- CAPTION ----------
    log_event("PIPELINE", "Step 5: Caption...")
    run_module("core.critic")

    # ---------- PUBLISH ----------
    log_event("PIPELINE", "Step 6: Publish...")
    if not run_module("core.publisher"):
        log_error("E06", "Publisher", "Upload failed.")
        return False

    log_event("SYSTEM", "✅ PIPELINE COMPLETE → AUTO SLEEP")
    return True


if __name__ == "__main__":
    print("\n" + "="*50)
    print("   🏏 IPLTrackX CLOUD MODE   ")
    print("="*50)

    try:
        run_pipeline()
    except Exception as e:
        log_error("CRITICAL", "Main", f"Crash prevented: {e}")

    sys.exit(0)
