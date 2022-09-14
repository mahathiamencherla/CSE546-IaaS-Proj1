import boto3

import os
from dotenv import load_dotenv

load_dotenv('../key.env')

import logging
from botocore.exceptions import ClientError
import json

# Create SQS client
sqs = boto3.client("sqs", region_name="us-east-1",
        aws_access_key_id=os.environ.get('AWS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET'))

queue_url = 'https://sqs.us-east-1.amazonaws.com/676148463056/RequestQueue'

def read_queue():

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=10
    )
    if "Messages" not in response:
        print('No messages')
        return
    print(response['Messages'][0])
    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']

    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    return message['Body']

if __name__ == "__main__":
    while True:
        print(read_queue())

