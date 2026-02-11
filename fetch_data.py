import requests

# Free public cricket data (no API key)
url = "https://site.web.api.espn.com/apis/v2/sports/cricket/scoreboard"

try:
    r = requests.get(url, timeout=10)
    data = r.json()

    matches = data.get("events", [])

    if not matches:
        print("No live or recent matches found.")
    else:
        match = matches[0]  # latest match
        name = match.get("name")
        status = match.get("status", {}).get("type", {}).get("description")

        print("MATCH:", name)
        print("STATUS:", status)

except Exception as e:
    print("Data fetch error:", e)

