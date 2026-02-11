import os
import json
import feedparser
import requests
import re
import sys
import socket
from datetime import datetime, timedelta

# ================= CONFIG =================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.txt")

socket.setdefaulttimeout(15)

# -------- TOP TEAMS (Whitelist) --------
TOP_TEAMS = [
    "india", "pakistan", "sri lanka", "bangladesh", "afghanistan",
    "australia", "england", "new zealand", "south africa", "west indies",
    "mumbai indians", "mi", "chennai super kings", "csk",
    "royal challengers", "rcb", "kolkata knight riders", "kkr",
    "sunrisers hyderabad", "srh", "delhi capitals", "dc",
    "rajasthan royals", "rr", "lucknow super giants", "lsg",
    "gujarat titans", "gt", "punjab kings", "pbks"
]

# -------- FILTERS --------
BLOCK_WORDS = [
    "squad", "preview", "weather", "pitch report", "toss", "probable xi",
    "fantasy", "injury update", "dream11", "practice", "training",
    "press conference", "live score", "warm-up", "nets", "prediction",
    "scenario", "points table"
]

REJECT_WORDS = ["u19", "under-19", "women", "a team", "academy", "emerging"]

IMPORTANT_WORDS = [
    "win", "beat", "defeat", "thriller", "century",
    "record", "final", "knockout", "eliminated",
    "champion", "historic", "series", "title", "victory"
]

# -------- RSS SOURCES --------
RSS_FEEDS = [
    "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    "https://sports.ndtv.com/rss/cricket",
    "https://www.hindustantimes.com/feeds/rss/cricket/rssfeed.xml",
    "https://timesofindia.indiatimes.com/rssfeeds/54829575.cms"
]

# ================= HELPERS =================

def normalize(text):
    if not text:
        return ""
    return re.sub(r'[^a-z0-9]', '', text.lower())


def clean_summary(text):
    if not text:
        return ""
    clean = re.sub(r'<[^<]+?>', '', text)
    return clean.strip()


def is_top_match(title):
    t = title.lower()
    if any(r in t for r in REJECT_WORDS):
        return False
    return any(team in t for team in TOP_TEAMS)


def is_important(title):
    t = title.lower()
    return any(w in t for w in IMPORTANT_WORDS)


def fetch_feed_safely(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return feedparser.parse(response.content)
    except:
        return None


def entry_time(e):
    if hasattr(e, "published_parsed") and e.published_parsed:
        return datetime(*e.published_parsed[:6])
    return datetime.min


# ================= MAIN HUNTER =================

def search_news_text():
    print("🦅 THE HUNTER: Scanning for BIG News Only...")

    if not os.path.exists(HISTORY_FILE):
        open(HISTORY_FILE, 'w').close()

    # Load normalized history
    with open(HISTORY_FILE, 'r') as f:
        posted_set = set(line.strip() for line in f.readlines())

    for url in RSS_FEEDS:
        print(f"   📡 Scanning: {url[:40]}...")
        feed = fetch_feed_safely(url)
        if not feed or not feed.entries:
            continue

        entries = sorted(feed.entries, key=entry_time, reverse=True)

        for entry in entries[:20]:
            title = entry.title.strip()
            link = entry.link.strip()

            if len(title) < 12:
                continue

            norm_title = normalize(title)
            norm_link = normalize(link)

            # -------- HARD DUPLICATE BLOCK --------
            if norm_title in posted_set or norm_link in posted_set:
                continue

            # -------- SOFT DUPLICATE BLOCK --------
            # Prevent near-same headline repost
            for old in posted_set:
                if len(old) > 25 and old[:25] == norm_title[:25]:
                    continue

            # -------- TIME FILTER --------
            if not hasattr(entry, "published_parsed") or not entry.published_parsed:
                continue

            pub_time = datetime(*entry.published_parsed[:6])
            if datetime.now() - pub_time > timedelta(hours=18):
                continue

            # -------- TRASH FILTER --------
            if any(word in title.lower() for word in BLOCK_WORDS):
                continue

            # -------- TEAM WHITELIST --------
            if not is_top_match(title):
                continue

            # -------- IMPORTANCE FILTER --------
            if not is_important(title):
                continue

            # -------- SUMMARY CLEAN --------
            raw_summary = entry.get('summary') or entry.get('description') or ""
            summary = clean_summary(raw_summary)
            if len(summary) < 40:
                summary = title

            # ================= ACCEPT NEWS =================
            news_data = {
                "title": title,
                "summary": summary,
                "url": link,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR)

            with open(NEWS_DATA_FILE, 'w') as f:
                json.dump(news_data, f, indent=4)

            # Save normalized fingerprint ONLY
            with open(HISTORY_FILE, 'a') as f:
                f.write(norm_title + "\n")
                f.write(norm_link + "\n")

            print(f"   ✔ ACCEPTED: {title[:70]}...")
            return True

    print("❌ No VIP news found.")
    return False


# ================= ENTRY =================

if __name__ == "__main__":
    if search_news_text():
        sys.exit(0)
    else:
        sys.exit(1)
