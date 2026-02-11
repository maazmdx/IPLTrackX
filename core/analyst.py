import json
import os
import datetime
from collections import Counter

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Files
METADATA_FILE = os.path.join(DATA_DIR, "post_metadata.json")
PERFORMANCE_FILE = os.path.join(DATA_DIR, "performance.json")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")

def log_analyst(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"📊 ANALYST: {message}")
    if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)
    with open(os.path.join(LOG_DIR, "performance.log"), "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def load_json(filepath, default=[]):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f: return json.load(f)
        except: pass
    return default

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def analyze_performance():
    """Reads all history and calculates what works best"""
    history = load_json(METADATA_FILE, [])
    if not history: return

    total_posts = len(history)
    
    # 1. Extract Lists
    styles = [h.get('style', 'UNKNOWN') for h in history]
    players = [h.get('player', 'Unknown') for h in history if h.get('player')]
    topics = [h.get('topic', 'General') for h in history]
    priorities = [h.get('priority', 'LOW') for h in history]
    qc_scores = [h.get('qc_score', 0) for h in history]
    
    # 2. Calculate Stats
    best_style = Counter(styles).most_common(1)[0][0] if styles else "MAGAZINE"
    top_player = Counter(players).most_common(1)[0][0] if players else "Kohli"
    top_topic = Counter(topics).most_common(1)[0][0] if topics else "Cricket"
    avg_qc = sum(qc_scores) / total_posts if total_posts > 0 else 0
    
    # 3. Best Time (Simple Frequency for now)
    times = [h.get('timestamp', '').split(' ')[1][:2] for h in history if 'timestamp' in h]
    best_hour = Counter(times).most_common(1)[0][0] + ":00" if times else "18:00"

    # 4. Construct Performance Profile
    perf_data = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_posts": total_posts,
        "best_performing_style": best_style,
        "top_player": top_player,
        "best_topic": top_topic,
        "best_post_time": best_hour,
        "avg_qc_score": round(avg_qc, 1),
        "priority_distribution": dict(Counter(priorities))
    }
    
    save_json(PERFORMANCE_FILE, perf_data)
    log_analyst(f"Learning Updated. Best Style: {best_style} | Top Player: {top_player}")

def record_post_success(upload_status="SUCCESS"):
    """Called by Publisher after upload"""
    if not os.path.exists(NEWS_DATA_FILE): return

    # 1. Read the Cycle Data
    with open(NEWS_DATA_FILE, 'r') as f: news_data = json.load(f)
    
    # 2. Create Record
    record = {
        "post_id": len(load_json(METADATA_FILE, [])) + 1,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": upload_status,
        "title": news_data.get('title', 'Unknown'),
        "player": news_data.get('player', None),
        "topic": news_data.get('context', 'General'),
        "priority": news_data.get('priority', 'LOW'),
        "style": news_data.get('style_used', 'Standard'),
        "qc_score": news_data.get('qc_score', 0) # Assumes QC writes back to json
    }
    
    # 3. Append to History
    history = load_json(METADATA_FILE, [])
    history.append(record)
    # Keep last 1000 posts to save space
    if len(history) > 1000: history = history[-1000:]
    save_json(METADATA_FILE, history)
    
    log_analyst(f"Post Recorded: {record['title']} (Style: {record['style']})")
    
    # 4. Trigger Self-Learning
    analyze_performance()

if __name__ == "__main__":
    # Test Run
    analyze_performance()
