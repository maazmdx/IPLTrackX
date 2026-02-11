import os
import json
import feedparser
from datetime import datetime
import sys

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.txt")

# 🚨 THE VIP LIST (Big Markets Only)
PREMIUM_TEAMS = [
    # International
    "india", "australia", "england", "pakistan", "south africa", "new zealand", 
    "west indies", "sri lanka", "bangladesh", 
    # IPL
    "csk", "chennai super kings", "rcb", "royal challengers bengaluru", "mi", "mumbai indians",
    "kkr", "kolkata knight riders", "srh", "sunrisers hyderabad", "dc", "delhi capitals",
    "gt", "gujarat titans", "lsg", "lucknow super giants", "rr", "rajasthan royals", "pbks", "punjab kings"
]

# 🚨 VIRAL TRIGGERS (Must have one of these to wake up)
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

def is_viral_premium(text):
    """Strict Filter: Must be VIP Team + Viral Keyword."""
    text = text.lower()
    
    # 1. Boring Filter
    if any(x in text for x in ["live score", "toss", "schedule", "weather", "preview", "training"]):
        return False

    # 2. Check Conditions
    has_premium_team = any(team in text for team in PREMIUM_TEAMS)
    has_viral_keyword = any(word in text for word in VIRAL_KEYWORDS)

    # STRICT RULE: Must match BOTH to be worth posting
    if has_premium_team and has_viral_keyword:
        return True
    
    return False

def search_news_text():
    print("🦅 THE HUNTER: Scanning for VIRAL VIP News...")
    
    if not os.path.exists(HISTORY_FILE): open(HISTORY_FILE, 'w').close()
    with open(HISTORY_FILE, 'r') as f: posted_titles = f.read()

    for url in RSS_FEEDS:
        try:
            print(f"   📡 Scanning: {url[:30]}...")
            feed = feedparser.parse(url)
            
            if not feed.entries: continue
            
            for entry in feed.entries[:8]:
                title = entry.title
                
                # CHECK 1: History
                if title[:20] in posted_titles: continue

                # CHECK 2: Strict Viral Filter
                if not is_viral_premium(title):
                    # print(f"      🗑️ Ignored (Not Viral): {title[:30]}...")
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
                
        except Exception as e:
            print(f"   ⚠️ Feed Error: {e}")
            continue

    print("❌ No VIRAL news found. Going to sleep.")
    return False

if __name__ == "__main__":
    if search_news_text(): sys.exit(0)
    else: sys.exit(1)
