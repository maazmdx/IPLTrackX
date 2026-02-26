import json
import os
from datetime import datetime

import requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")

STANDINGS_URLS = [
    "https://site.web.api.espn.com/apis/v2/sports/cricket/standings",
    "https://site.api.espn.com/apis/site/v2/sports/cricket/standings",
]


def _safe_get_json(url):
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None


def _team_row(entry):
    team = entry.get("team", {})
    name = team.get("shortDisplayName") or team.get("displayName") or "Team"
    stats = {s.get("name", "").lower(): s.get("value") for s in entry.get("stats", []) if isinstance(s, dict)}
    pts = stats.get("points", 0)
    nrr = stats.get("netrunrate", stats.get("nrr", 0))
    played = stats.get("gamesplayed", stats.get("played", 0))
    return {"team": name, "points": pts, "nrr": nrr, "played": played}


def build_standings_content():
    table = []
    for url in STANDINGS_URLS:
        data = _safe_get_json(url)
        if not data:
            continue

        children = data.get("children") or []
        for section in children:
            standings = section.get("standings", {})
            entries = standings.get("entries") or []
            table = [_team_row(e) for e in entries if e.get("team")]
            if table:
                break
        if table:
            break

    if not table:
        print("⚠️ Standings Engine: table unavailable.")
        return False

    table = sorted(table, key=lambda x: (x["points"], x["nrr"]), reverse=True)
    top = ", ".join([f"{r['team']} ({r['points']})" for r in table[:4]])
    bubble = ", ".join([f"{r['team']} {r['points']}pts" for r in table[3:7]]) if len(table) > 4 else "Race tightening"

    payload = {
        "title": "POINTS TABLE WATCH",
        "summary": f"Top 4 today: {top}. Qualification race: {bubble}.",
        "visual_prompt": "ipl points table cricket standings graphics",
        "content_type": "standings",
        "priority": "MEDIUM",
        "context": "Tournament Standings",
        "standings": table,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(NEWS_DATA_FILE, "w") as f:
        json.dump(payload, f, indent=4)

    print("✅ Standings Engine: Standings post generated.")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if build_standings_content() else 1)
