import json
import os

# --- CONFIGURATION ---
BASE_DIR = os.getcwd()
TEMP_DIR = os.path.join(BASE_DIR, "temp")
NEWS_DATA_FILE = os.path.join(TEMP_DIR, "design_data.json")

# --- TEAM COLOR DATABASE (Hex Codes) ---
THEMES = {
    # IPL TEAMS
    "CSK": "#F9CD05", "CHENNAI": "#F9CD05", "SUPER KINGS": "#F9CD05",
    "RCB": "#EC1C24", "BANGALORE": "#EC1C24", "ROYAL CHALLENGERS": "#EC1C24",
    "MI": "#004BA0", "MUMBAI": "#004BA0", "INDIANS": "#004BA0",
    "KKR": "#3A225D", "KOLKATA": "#3A225D", "KNIGHT RIDERS": "#3A225D",
    "GT": "#1B2133", "GUJARAT": "#1B2133", "TITANS": "#1B2133",
    "LSG": "#00A0E3", "LUCKNOW": "#00A0E3", "SUPER GIANTS": "#00A0E3",
    "RR": "#EA1A85", "RAJASTHAN": "#EA1A85", "ROYALS": "#EA1A85",
    "DC": "#0078BC", "DELHI": "#0078BC", "CAPITALS": "#0078BC",
    "PBKS": "#DD1F2D", "PUNJAB": "#DD1F2D", "KINGS": "#DD1F2D",
    "SRH": "#F26522", "HYDERABAD": "#F26522", "SUNRISERS": "#F26522",

    # INTERNATIONAL
    "INDIA": "#0074CC", "IND": "#0074CC", "BCCI": "#0074CC", "ROHIT": "#0074CC", "KOHLI": "#0074CC",
    "AUSTRALIA": "#FFD700", "AUS": "#FFD700",
    "ENGLAND": "#152036", "ENG": "#152036",
    "PAKISTAN": "#006600", "PAK": "#006600",
    "NEW ZEALAND": "#000000", "NZ": "#000000",
    "SOUTH AFRICA": "#007A4D", "SA": "#007A4D",

    # DEFAULTS
    "BREAKING": "#D60000", # Red
    "IPL": "#1A3D92"       # IPL Blue
}

def determine_strategy():
    if not os.path.exists(NEWS_DATA_FILE):
        print("❌ No news data found. Run hunter.py first.")
        return

    with open(NEWS_DATA_FILE, 'r') as f:
        data = json.load(f)
    
    headline = data.get('title', '').upper()
    print(f"🧠 THE BRAIN: Analyzing Headline: '{headline}'")
    
    # default theme
    selected_theme = THEMES["IPL"]
    detected_key = "General IPL"

    # Scan headline for keywords
    for key, color in THEMES.items():
        # We add spaces to avoid matching substrings (e.g. 'IND' inside 'WINDOW')
        if f" {key} " in f" {headline} ": 
            selected_theme = color
            detected_key = key
            break # Stop at first match (Priority)

    # Save the Strategy
    data['theme_color'] = selected_theme
    data['theme_name'] = detected_key
    
    with open(NEWS_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"🎨 Theme Set: {detected_key} ({selected_theme})")
    print("✅ Strategy Finalized.")

if __name__ == "__main__":
    determine_strategy()
