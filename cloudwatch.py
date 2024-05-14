import boto3
from datetime import datetime, timedelta
from constants import LOG_GROUP
import time

# Function to get log records from AWS CloudWatch
def get_log_records(query: str) -> list[dict[str:str]]:
    # Create a client for AWS CloudWatch Logs
    client = boto3.client('logs')

    # Start a query to fetch logs from the past 90 days
    start_query_response = client.start_query(
        logGroupName=LOG_GROUP,
        startTime=int((datetime.now() - timedelta(days=120)).timestamp()),
        endTime=int(datetime.now().timestamp()),
        queryString=query,
    )

    # Extract the query ID from the response
    query_id = start_query_response['queryId']

    response = None

    # Poll the query status until it's no longer 'Running'
    while response == None or response['status'] == 'Running':
        print('Waiting for query to complete ...')
        time.sleep(1)
        response = client.get_query_results(
            queryId=query_id
        )
        
    # If the response contains 'results', return them
    if 'results' in response:
        return response['results']
    
# Function to parse log records into field names and values
def parse_log_records(log_records : list[dict[str:str]]) -> tuple[list[str], list[list[str]]]:
    # Extract field names from the first log record
    field_names = [f['field'] for f in log_records[0]]
    # Extract field values from all log records
    field_values = [[f['value'] for f in record] for record in log_records]
    
    # Return field names and values as a tuple
    return field_names, field_values