import boto3
import image_classification

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
s3 = boto3.client("s3", region_name="us-east-1",
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
    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']

    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    return message['Body']

def process_image(imageName):
    s3.download_file('iaas-proj-input', imageName, 'downloads/'+imageName)
    classification = image_classification.classify('downloads/'+imageName)
    data = {
        imageName.split('.')[0]: classification
    }

    s3.put_object(
        Bucket = 'iaas-proj-output',
        Key = imageName.split('.')[0],
        Body = str({
            imageName.split('.')[0]: classification
        })
    )

if __name__ == "__main__":
    while True:
        imageName = read_queue()
        if imageName:
            process_image(imageName)

