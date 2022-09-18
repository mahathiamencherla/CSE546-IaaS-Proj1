from email.mime import image
import boto3
import image_classification
import json
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

request_queue_url = 'https://sqs.us-east-1.amazonaws.com/676148463056/RequestQueue'
response_queue_url = 'https://sqs.us-east-1.amazonaws.com/676148463056/ResponseQueue'

def read_queue():

    # Receive message from SQS queue
    response = sqs.receive_message(
        QueueUrl=request_queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=1,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=20,
        WaitTimeSeconds=10
    )
    if "Messages" not in response:
        print('No messages')
        return
    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']

    # Delete received message from queue
    sqs.delete_message(
        QueueUrl=request_queue_url,
        ReceiptHandle=receipt_handle
    )
    return json.loads(message['Body'])

class Message():
    def __init__(self, id, image, classification):
        self.id = id
        self.image = image
        self.classification = classification

def process_image(message):
    s3.download_file('iaas-proj-input', message['name'], 'downloads/'+message['name'])
    classification = image_classification.classify('downloads/'+message['name'])

    s3.put_object(
        Bucket = 'iaas-proj-output',
        Key = message['name'].split('.')[0],
        Body = str({
            message['name'].split('.')[0]: classification
        })
    )

    message = Message(message['id'], message['name'], classification)
    sqs.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/676148463056/ResponseQueue',
        MessageBody=str(json.dumps(message.__dict__))
    )
    print(message.image + " processed. Classification - " + classification)

if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    while True:
        message = read_queue()
        if message:
            process_image(message)

