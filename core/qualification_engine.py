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


def _extract_table(data):
    table = []
    for section in data.get("children", []):
        entries = (section.get("standings") or {}).get("entries") or []
        for e in entries:
            team = e.get("team", {})
            if not team:
                continue
            stats = {s.get("name", "").lower(): s.get("value") for s in e.get("stats", []) if isinstance(s, dict)}
            table.append(
                {
                    "team": (team.get("shortDisplayName") or team.get("displayName") or "Team"),
                    "points": float(stats.get("points", 0) or 0),
                    "nrr": float(stats.get("netrunrate", stats.get("nrr", 0)) or 0),
                    "played": float(stats.get("gamesplayed", stats.get("played", 0)) or 0),
                }
            )
    return sorted(table, key=lambda x: (x["points"], x["nrr"]), reverse=True)


def _team_lookup(table, preferred=("India", "IND", "Mumbai Indians", "Royal Challengers")):
    for p in preferred:
        for row in table:
            if p.lower() in row["team"].lower():
                return row
    return table[0] if table else None


def build_qualification_content():
    table = []
    for url in STANDINGS_URLS:
        data = _safe_get_json(url)
        if not data:
            continue
        table = _extract_table(data)
        if table:
            break

    if not table:
        print("⚠️ Qualification Engine: standings unavailable.")
        return False

    focus = _team_lookup(table)
    cutoff = table[3]["points"] if len(table) > 3 else table[-1]["points"]
    projected_if_win = focus["points"] + 2

    summary = (
        f"If {focus['team']} wins next match → {projected_if_win:.0f} points and playoff push gets real. "
        f"If NRR improves above {focus['nrr'] + 0.20:.2f}, tiebreak edge increases near {cutoff:.0f}-point cutoff."
    )

    payload = {
        "title": "QUALIFICATION SCENARIOS",
        "summary": summary,
        "visual_prompt": f"{focus['team']} qualification scenario cricket playoff race",
        "content_type": "qualification",
        "priority": "MEDIUM",
        "context": "Qualification Race",
        "qualification": {
            "focus_team": focus["team"],
            "current_points": focus["points"],
            "projected_if_win": projected_if_win,
            "current_nrr": focus["nrr"],
            "cutoff_points": cutoff,
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(NEWS_DATA_FILE, "w") as f:
        json.dump(payload, f, indent=4)

    print("✅ Qualification Engine: scenario post generated.")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if build_qualification_content() else 1)
