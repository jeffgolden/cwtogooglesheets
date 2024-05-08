from cloudwatch import get_log_records, parse_log_records
from sheets import write_cloudwatch_to_google_sheets
from excel_to_drive import write_cloudwatch_to_google_drive
import uuid

def main():
    # Get log records from AWS CloudWatch
    log_records = get_log_records()

    # Parse log records into field names and values
    field_names, data = parse_log_records(log_records)

    # Write log records to Google Sheets
    doc_name = write_cloudwatch_to_google_sheets(field_names, data)
    print(f'Google Sheets document created: {doc_name}')
    
    # Write to Excel and upload to Google Drive
    doc_name = write_cloudwatch_to_google_drive(field_names, data)
    print(f'Google Drive document created: {doc_name}')
    
if __name__ == '__main__':
    main()
    