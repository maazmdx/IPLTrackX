import os
import json
import feedparser
import requests
from datetime import datetime
import sys
import socket

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.txt")

socket.setdefaulttimeout(15)

# 🚨 THE VIP LIST
PREMIUM_TEAMS = [
    "india", "australia", "england", "pakistan", "south africa", "new zealand", 
    "csk", "rcb", "mi", "kkr", "srh", "gt", "lsg", "rr", "pbks", "dc"
]

# 🚨 ONLY THESE TRIGGER A POST
VIRAL_KEYWORDS = [
    "won", "lost", "win", "defeat", "tied", "draw", # Results
    "century", "hat-trick", "record", "hero", "storm", # Achievements
    "shock", "thriller", "drama", "controversy", # Viral
    "final", "semi-final", "champion", "trophy" # Big Stakes
]

# 🗑️ IGNORE LIST (Boring Stuff)
TRASH_KEYWORDS = [
    "preview", "schedule", "squad", "announce", "weather", "toss", 
    "playing xi", "live score", "warm-up", "training", "nets",
    "prediction", "scenario", "table", "points", "stats"
]

RSS_FEEDS = [
    "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    "https://sports.ndtv.com/rss/cricket",
    "https://www.hindustantimes.com/feeds/rss/cricket/rssfeed.xml",
    "https://timesofindia.indiatimes.com/rssfeeds/54829575.cms"
]

def fetch_feed_safely(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return feedparser.parse(response.content)
    except: return None

def is_viral_premium(text):
    text = text.lower()
    
    # 1. TRASH FILTER (If it contains any trash word, ignore it immediately)
    if any(x in text for x in TRASH_KEYWORDS):
        return False

    # 2. MUST BE A VIP TEAM
    has_premium_team = any(team in text for team in PREMIUM_TEAMS)
    if not has_premium_team: return False
    
    # 3. MUST CONTAIN A VIRAL TRIGGER
    has_viral_keyword = any(word in text for word in VIRAL_KEYWORDS)
    if not has_viral_keyword: return False

    return True

def search_news_text():
    print("🦅 THE HUNTER: Scanning for BIG News Only...")
    
    if not os.path.exists(HISTORY_FILE): open(HISTORY_FILE, 'w').close()
    with open(HISTORY_FILE, 'r') as f: posted_titles = f.read()

    for url in RSS_FEEDS:
        print(f"   📡 Scanning: {url[:30]}...")
        feed = fetch_feed_safely(url)
        if not feed or not feed.entries: continue
        
        for entry in feed.entries[:10]:
            title = entry.title
            
            if title[:20] in posted_titles: continue

            # Strict Check
            if not is_viral_premium(title):
                # print(f"      🗑️ Ignored: {title[:30]}...")
                continue

            # ✅ FOUND VIRAL NEWS
            news_data = {
                "title": title,
                "summary": entry.get('summary', ''),
                "url": entry.link,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
            with open(NEWS_DATA_FILE, 'w') as f: json.dump(news_data, f, indent=4)
            with open(HISTORY_FILE, 'a') as f: f.write(title + "\n")
                
            print(f"✅ FOUND BIG NEWS: {news_data['title']}")
            return True

    print("❌ No VIRAL news found. Going to sleep.")
    return False

if __name__ == "__main__":
    if search_news_text(): sys.exit(0)
    else: sys.exit(1)
