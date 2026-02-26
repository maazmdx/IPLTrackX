import json
import os
from datetime import datetime

import requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")

SCOREBOARD_URL = "https://site.web.api.espn.com/apis/v2/sports/cricket/scoreboard"


def _safe_scoreboard():
    try:
        r = requests.get(SCOREBOARD_URL, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None


def _find_troll_target(data):
    events = data.get("events", []) if data else []
    for event in events:
        for comp in event.get("competitions", []):
            competitors = comp.get("competitors", [])
            losers = [c for c in competitors if c.get("winner") is False]
            winners = [c for c in competitors if c.get("winner") is True]
            if losers and winners:
                loser = losers[0].get("team", {}).get("displayName", "Team")
                winner = winners[0].get("team", {}).get("displayName", "Opponent")
                detail = comp.get("status", {}).get("type", {}).get("shortDetail", "")
                return loser, winner, detail
    return None


def build_meme_content():
    target = _find_troll_target(_safe_scoreboard())

    if target:
        loser, winner, detail = target
        caption = f"{loser} fans opening calculator before powerplay ends 💀"
        summary = f"{winner} humbled {loser}. {detail or 'Underperformance archived in 4K.'} Savage, stat-backed banter only."
        visual_prompt = f"funny cricket meme poster {loser} disappointed fans stadium"
    else:
        caption = "When your team says 'trust the process' after 6 straight dot balls 💀"
        summary = "Expectation: title run. Reality: meme template speedrun. Banter mode on, toxicity off."
        visual_prompt = "funny cricket meme dark humor safe sports design"

    payload = {
        "title": "MEME OF THE DAY",
        "summary": summary,
        "caption": caption,
        "visual_prompt": visual_prompt,
        "content_type": "meme",
        "priority": "LOW",
        "context": "Cricket Banter",
        "meme": {
            "caption": caption,
            "tone": "dark humor / savage but safe",
            "poster_style": "bold meme poster",
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(NEWS_DATA_FILE, "w") as f:
        json.dump(payload, f, indent=4)

    print("✅ Meme Engine: meme content generated.")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if build_meme_content() else 1)
