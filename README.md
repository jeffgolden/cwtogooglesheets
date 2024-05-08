# Cloudwatch Logs to Google Sheets Exercise

This is just a simple exercise for me to learn how to write CloudWatch logs to Google Sheets.

This requires setting up Google Sheets Credentials and storing them in credentials.json in the project directory before it will run.   This references a specific log group in my own
AWS account.

## Updated

This project was updated to include another method, creating an Excel file (in memory) and then uploading that to Google Drive as a Google Sheets document rather than directly to Google Sheets. This avoids the rate-limiting errors that happen with the original method and is much more efficient.
