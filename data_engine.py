import requests
import json

URL = "https://site.web.api.espn.com/apis/v2/sports/cricket/scoreboard"

def fetch_match():
    try:
        r = requests.get(URL, timeout=10)
        data = r.json()
    except:
        return None

    matches = data.get("events", [])
    if not matches:
        return None

    # Try to get most relevant match
    for m in matches:
        status = m.get("status", {}).get("type", {}).get("description", "").lower()

        if "final" in status or "result" in status:
            return m

    # If no finished match, return first available
    return matches[0]

def extract_basic(match):
    name = match.get("name", "Match")
    status = match.get("status", {}).get("type", {}).get("description", "Unknown")

    teams = match.get("competitions", [])[0].get("competitors", [])

    team_data = []
    for t in teams:
        team_name = t.get("team", {}).get("displayName", "")
        score = t.get("score", "")
        winner = t.get("winner", False)

        team_data.append({
            "team": team_name,
            "score": score,
            "winner": winner
        })

    return name, status, team_data

def build_output(name, status, team_data):
    winner_team = "TBD"

    for t in team_data:
        if t["winner"]:
            winner_team = t["team"]

    facts = []

    for t in team_data:
        facts.append(f'{t["team"]}: {t["score"]}')

    if winner_team != "TBD":
        facts.insert(0, f"Winner: {winner_team}")

    return {
        "match": name,
        "status": status,
        "facts": facts
    }

def main():
    match = fetch_match()
    if not match:
        print("No match data")
        return

    name, status, team_data = extract_basic(match)
    output = build_output(name, status, team_data)

    with open("real_match.json", "w") as f:
        json.dump(output, f, indent=2)

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
