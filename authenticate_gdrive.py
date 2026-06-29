import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    print("\n--- Google Drive OAuth 2.0 Authorization Utility ---")
    client_secrets = 'google_drive_client_secrets.json'
    
    if not os.path.exists(client_secrets):
        print(f"Error: {client_secrets} file not found in the project root directory!")
        print("\nTo generate this file:")
        print("1. Go to Google Cloud Console > Credentials.")
        print("2. Click 'Create Credentials' -> 'OAuth client ID'.")
        print("3. Set Application Type to 'Desktop app' and click Create.")
        print("4. Download the JSON, rename it to 'google_drive_client_secrets.json', and save it here.")
        return
        
    try:
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
        print("\nStarting local authentication server...")
        print("A web browser window should open automatically to complete the authorization.")
        creds = flow.run_local_server(port=0)
        
        token_path = 'token.json'
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
            
        print("\nSUCCESS: Authorization completed successfully!")
        print(f"Credentials saved to '{token_path}'!")
        print("The AIMS portal is now authorized to upload directly to your personal Google Drive!")
    except Exception as e:
        print("\nError during authorization:", e)

if __name__ == "__main__":
    main()
