from google import genai

# Put your NEW API key here
client = genai.Client(api_key="AIzaSyAr0HC-K_d5Au3tLKw4O5FY8xcYKiHLGcQ")

prompt = """
RCB beat MI by 6 wickets.
Virat Kohli scored 82 (49).
Player of the Match: Virat Kohli.
"""

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt
)

print(response.text)

