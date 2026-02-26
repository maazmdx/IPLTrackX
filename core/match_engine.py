import json
import os
from datetime import datetime

import requests

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_DATA_FILE = os.path.join(DATA_DIR, "design_data.json")

SCOREBOARD_URLS = [
    "https://site.web.api.espn.com/apis/v2/sports/cricket/scoreboard",
    "https://site.api.espn.com/apis/site/v2/sports/cricket/scoreboard",
]


def _safe_get_json(url):
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None


def _extract_match(event):
    competitions = event.get("competitions") or []
    if not competitions:
        return None

    comp = competitions[0]
    status = comp.get("status", {}).get("type", {})
    state = (status.get("state") or "").lower()
    description = status.get("shortDetail") or status.get("detail") or ""

    # Keep only in-progress/recently completed fixtures.
    if state not in {"in", "post"}:
        return None

    teams = []
    score_bits = []
    top_performer = "Top performer unavailable"

    competitors = comp.get("competitors", [])
    for team in competitors:
        t = team.get("team", {})
        short = t.get("shortDisplayName") or t.get("displayName") or "Team"
        teams.append(short)

        score = team.get("score")
        if score is not None:
            score_bits.append(f"{short} {score}")

        leaders = team.get("leaders") or []
        for leader in leaders:
            if leader.get("name", "").lower() in {"top run scorers", "top wicket takers"}:
                athletes = leader.get("leaders") or []
                if athletes:
                    athlete = athletes[0]
                    top_performer = f"{athlete.get('athlete', {}).get('displayName', 'Player')} ({athlete.get('displayValue', '')})"
                    break

    winner = ""
    for team in competitors:
        if team.get("winner"):
            winner = team.get("team", {}).get("displayName", "")
            break

    headline = "LIVE MATCH UPDATE" if state == "in" else "MATCH RESULT"
    margin = description or "Result margin unavailable"
    scoreline = " vs ".join(score_bits) if score_bits else "Score unavailable"

    # Prefer official note when available.
    notes = comp.get("notes") or []
    if notes:
        margin = notes[0].get("headline") or margin

    return {
        "title": headline,
        "summary": f"{' vs '.join(teams)}: {scoreline}. {winner or 'Match in progress'}. {margin}.",
        "visual_prompt": f"{' vs '.join(teams)} cricket match action",
        "source": event.get("link", {}).get("href", SCOREBOARD_URLS[0]),
        "content_type": "match_result",
        "priority": "HIGH" if state == "post" else "MEDIUM",
        "context": "Match Center",
        "match_data": {
            "teams": teams,
            "score": scoreline,
            "winner": winner or "In progress",
            "margin": margin,
            "top_performer": top_performer,
            "state": state,
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def build_match_content():
    for url in SCOREBOARD_URLS:
        payload = _safe_get_json(url)
        if not payload:
            continue

        for event in payload.get("events", []):
            structured = _extract_match(event)
            if structured:
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(NEWS_DATA_FILE, "w") as f:
                    json.dump(structured, f, indent=4)
                print("✅ Match Engine: Structured match content generated.")
                return True

    print("⚠️ Match Engine: No ongoing/recent match found.")
    return False


if __name__ == "__main__":
    raise SystemExit(0 if build_match_content() else 1)
