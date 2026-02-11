import os
from google_auth_oauthlib.flow import InstalledAppFlow

# This allows the bot to manage files in your Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    print("🚀 Launching Browser for Login...")
    
    if not os.path.exists('credentials.json'):
        print("❌ Error: 'credentials.json' not found!")
        print("   -> Please download it from Google Cloud Console and put it here.")
        return

    # Start Login Flow
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    
    # This will open a window. Log in with YOUR Google Account.
    creds = flow.run_local_server(port=0)
    
    # Save the "Master Key" (Token)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
        
    print("\n✅ SUCCESS! 'token.json' created.")
    print("   -> The bot is now authenticated as YOU.")
    print("   -> You can restart 'main.py' now.")

if __name__ == '__main__':
    authenticate()
