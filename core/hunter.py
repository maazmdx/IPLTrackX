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

# Set global timeout for any socket connection
socket.setdefaulttimeout(15)

# 🚨 THE VIP LIST
PREMIUM_TEAMS = [
    "india", "australia", "england", "pakistan", "south africa", "new zealand", 
    "west indies", "sri lanka", "bangladesh", 
    "csk", "chennai super kings", "rcb", "royal challengers bengaluru", "mi", "mumbai indians",
    "kkr", "kolkata knight riders", "srh", "sunrisers hyderabad", "dc", "delhi capitals",
    "gt", "gujarat titans", "lsg", "lucknow super giants", "rr", "rajasthan royals", "pbks", "punjab kings"
]

# 🚨 VIRAL TRIGGERS
VIRAL_KEYWORDS = [
    "won", "lost", "win", "defeat", "final", "semi-final", "world cup", 
    "champions trophy", "kohli", "dhoni", "rohit", "babar", "rizwan", "bumrah", 
    "shakib", "rashid", "hasaranga", "auction", "injury", "ruled out", "captain", 
    "shock", "thriller", "super over", "controversy", "bcci", "pcb", "slc", "bcb",
    "squad", "team", "announce", "century", "ton", "five-wicket", "record"
]

RSS_FEEDS = [
    "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    "https://sports.ndtv.com/rss/cricket",
    "https://www.hindustantimes.com/feeds/rss/cricket/rssfeed.xml",
    "https://timesofindia.indiatimes.com/rssfeeds/54829575.cms"
]

def fetch_feed_safely(url):
    """Fetches RSS XML with a fake browser agent and strict timeout."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return feedparser.parse(response.content)
    except Exception as e:
        print(f"      ⚠️ Connection Failed: {e}")
        return None

def is_viral_premium(text):
    text = text.lower()
    
    # 1. Boring Filter
    if any(x in text for x in ["live score", "toss", "schedule", "weather", "preview", "training"]):
        return False

    # 2. Check Conditions
    has_premium_team = any(team in text for team in PREMIUM_TEAMS)
    has_viral_keyword = any(word in text for word in VIRAL_KEYWORDS)

    # STRICT RULE: Must match BOTH
    if has_premium_team and has_viral_keyword:
        return True
    
    return False

def search_news_text():
    print("🦅 THE HUNTER: Scanning for VIRAL VIP News...")
    
    if not os.path.exists(HISTORY_FILE): open(HISTORY_FILE, 'w').close()
    with open(HISTORY_FILE, 'r') as f: posted_titles = f.read()

    for url in RSS_FEEDS:
        print(f"   📡 Scanning: {url[:35]}...")
        
        feed = fetch_feed_safely(url)
        if not feed or not feed.entries: continue
        
        for entry in feed.entries[:10]:
            title = entry.title
            
            # CHECK 1: History
            if title[:20] in posted_titles: continue

            # CHECK 2: Strict Viral Filter
            if not is_viral_premium(title):
                continue

            # ✅ FOUND VIRAL NEWS
            news_data = {
                "title": title,
                "summary": entry.get('summary', entry.get('description', '')),
                "source": feed.feed.get('title', 'Cricket News'),
                "url": entry.link,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
            with open(NEWS_DATA_FILE, 'w') as f:
                json.dump(news_data, f, indent=4)
            
            with open(HISTORY_FILE, 'a') as f:
                f.write(title + "\n")
                
            print(f"✅ FOUND VIRAL NEWS: {news_data['title']}")
            return True

    print("❌ No VIRAL news found. Going to sleep.")
    return False

if __name__ == "__main__":
    if search_news_text(): sys.exit(0)
    else: sys.exit(1)
