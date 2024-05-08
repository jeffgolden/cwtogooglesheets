import logging
import uuid
from google_shared import get_credentials
from googleapiclient.discovery import build
import time

# Create a logger instance
logger = logging.getLogger(__name__)

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
                    logger.error(f"Encountered error: {e}. Retrying in {retry_delay} seconds...")
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
