import io
import uuid
import pandas as pd
import logging
from google_shared import get_credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import uuid

# Get the logger from the calling module
logger = logging.getLogger(__name__)

def create_excel_file(field_names: list[str], data: list[list[str]]) -> io.BytesIO:
    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=field_names)
    
    # Create an in-memory Excel file
    excel_file = io.BytesIO()
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    
    # Reset the file pointer to the beginning of the file
    excel_file.seek(0)
    
    return excel_file

def upload_excel_to_drive(excel_file: io.BytesIO, title: str) -> str:
    # Get credentials
    creds = get_credentials()
    # Build the Google Drive service
    service = build('drive', 'v3', credentials=creds)
    
    # Create a new file in Google Drive
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    media = io.BytesIO(excel_file.read())
    media.seek(0)
    media_upload = MediaIoBaseUpload(media, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    request =  service.files().create(media_body=media_upload, body = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    })
    
    # Return the ID of the created file
    file = request.execute()
    return file['id']

def write_cloudwatch_to_google_drive(field_names: list[str], data: list[list[str]]) -> str:
    # Generate a unique ID for the file name
    uuid_string = str(uuid.uuid4().hex)
    file_name = f"demo-file-{uuid_string}.xlsx"
    
    # Create an Excel file in memory
    excel_file = create_excel_file(field_names, data)
    
    # Upload the Excel file to Google Drive
    file_id = upload_excel_to_drive(excel_file, file_name)
    
    # Log the file name
    logger.info(f"Uploaded file: {file_name}")
    
    return file_name
