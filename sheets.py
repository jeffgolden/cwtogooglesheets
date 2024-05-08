import uuid
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import uuid
import time
import os.path

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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/spreadsheets'])
            creds = flow.run_local_server(port=0)
            
        # Save the refreshed credentials to token.json file
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return creds

def create_google_sheets_document(title: str) -> str:
    # Get credentials
    creds = get_credentials()
    # Build the Google Sheets service
    service = build('sheets', 'v4', credentials=creds)
    
    # Create a new spreadsheet with the given title
    spreadsheet = {
        'properties': {
            'title': title,
        }
    }
    
    # Send the request to create the spreadsheet
    request = service.spreadsheets().create(body=spreadsheet)
    response = request.execute()
    
    # Return the ID of the created spreadsheet
    return response['spreadsheetId']


def write_cloudwatch_to_google_sheets(field_names: list[str], data: list[list[str]]) -> str:
    # Generate a unique ID for the sheet name
    uuid_string = str(uuid.uuid4().hex)
    doc_name = f"demo-sheet-{uuid_string}"
    
    # Create a new Google Sheets document with the generated sheet name
    spreadsheet_id = create_google_sheets_document(doc_name)
    
    # Get credentials
    creds = get_credentials()
    # Build the Google Sheets service
    service = build('sheets', 'v4', credentials=creds)
    
    # Update the sheet properties to set the sheet title
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
        'requests': [
            {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': 0, 
                        'title': uuid_string
                    },
                    'fields': 'title',
                }
            }
        ]
    })
    request.execute()

    # Prepare the values to be written to the sheet
    values = [
        field_names
    ]

    # Update the header row with the field names
    request = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{uuid_string}!A1:{chr(ord('A') + len(field_names) - 1)}1",
        valueInputOption='USER_ENTERED',
        body={'values': values}
    )
    request.execute()
    
    # Append the log records to the sheet (ideally this could be done outside of a loop but the API has a rate limit of 60 requests per minute - which can be increased)
    for row in data:
        values = [row]
        request = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{uuid_string}!A2:{chr(ord('A') + len(field_names) - 1)}",
            valueInputOption='USER_ENTERED',
            body={'values': values}
        )
        
        # Exponential backoff parameters
        max_retries = 5
        retry_delay = 30
        
        for retry in range(max_retries):
            try:
                request.execute()
                break
            except Exception as e:
                if retry == max_retries - 1:
                    raise e
                else:
                    print(f"Encountered error: {e}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    
    # Autofit columns in the sheet
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
        'requests': [
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': 0,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': len(field_names)
                    }
                }
            }
        ]
    })
    request.execute()
    
    return doc_name