import logging
from cloudwatch import get_log_records, parse_log_records
from sheets import write_cloudwatch_to_google_sheets
from excel_to_drive import write_cloudwatch_to_google_drive
from constants import QUERY

def main():
    # Configure logging
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

    # Get log records from AWS CloudWatch
    logging.info('Getting log records from AWS CloudWatch ...')
    query = QUERY + " | limit 100"
    log_records = get_log_records(query)

    # Parse log records into field names and values
    logging.info('Parsing log records ...')
    field_names, data = parse_log_records(log_records)

    # Write log records to Google Sheets
    logging.info('Writing log records to Google Sheets ...')
    doc_name = write_cloudwatch_to_google_sheets(field_names, data)
    logging.info(f'Google Sheets document created: {doc_name}')

    # Get log records from AWS CloudWatch
    logging.info('Getting log records from AWS CloudWatch ...')
    query = QUERY + " | limit 1000"
    log_records = get_log_records(query)

    # Parse log records into field names and values
    logging.info('Parsing log records ...')
    field_names, data = parse_log_records(log_records)


    # Write to Excel and upload to Google Drive
    logging.info('Writing log records to Google Drive ...')
    doc_name = write_cloudwatch_to_google_drive(field_names, data)
    logging.info(f'Google Drive document created: {doc_name}')

if __name__ == '__main__':
    main()
