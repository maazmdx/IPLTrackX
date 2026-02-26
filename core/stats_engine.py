import json
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
PERFORMANCE_FILE = os.path.join(DATA_DIR, "performance.json")
POST_LOG_FILE = os.path.join(DATA_DIR, "posted_log.json")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default


def build_stats_content():
    perf = _load_json(PERFORMANCE_FILE, {})
    logs = _load_json(POST_LOG_FILE, [])

    total_posts = perf.get("total_posts", len(logs))
    best_time = perf.get("best_post_time", "18:00")
    best_style = perf.get("best_performing_style", "MAGAZINE")

    if total_posts <= 0 and not logs:
        print("⚠️ Stats Engine: insufficient system stats.")
        return False

    payload = {
        "title": "STATS SNAPSHOT",
        "summary": f"{total_posts} tracked posts so far. Best engagement window around {best_time}; best style trend: {best_style}.",
        "visual_prompt": "cricket analytics dashboard graph stats",
        "content_type": "stats",
        "priority": "LOW",
        "context": "Performance Stats",
        "stats": {
            "total_posts": total_posts,
            "best_post_time": best_time,
            "best_style": best_style,
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(NEWS_DATA_FILE, "w") as f:
        json.dump(payload, f, indent=4)

    print("✅ Stats Engine: stats post generated.")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if build_stats_content() else 1)
