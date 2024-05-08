import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

def get_credentials() -> Credentials:
    # Check if token.json file exists and load credentials from it
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
        
    # If credentials are not valid or expired, refresh them
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Run the local server flow to obtain new credentials
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets'])
            creds = flow.run_local_server(port=0)
            
        # Save the refreshed credentials to token.json file
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds