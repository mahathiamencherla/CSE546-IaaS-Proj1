import boto3
import os
from dotenv import load_dotenv
import math

load_dotenv('../key.env')

responseQueue = boto3.client('sqs', region_name="us-east-1",
        aws_access_key_id=os.environ.get('AWS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET'))
ec2 = boto3.client('ec2', region_name="us-east-1",
        aws_access_key_id=os.environ.get('AWS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET'))
# Get the queue URL
# old queue: requestQueue_url = 'https://sqs.us-east-1.amazonaws.com/676148463056/RequestQueue'
requestQueue_url = 'https://sqs.us-east-1.amazonaws.com/983873151114/RequestQueue'
# Fetch the ApproximateNumberOfMessages from the queue
requestQueue_attributes = responseQueue.get_queue_attributes(QueueUrl=requestQueue_url, AttributeNames=['ApproximateNumberOfMessages'])
noOfMessages = int(requestQueue_attributes['Attributes']['ApproximateNumberOfMessages'])
# Fetch ids of the running instances
runningEc2 = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']},{'Name': 'tag:tier', 'Values': ['app']}])
runningEc2Ids = []
# List of IDs of running instances
if runningEc2['Reservations']:
        for instance in runningEc2['Reservations'][0]['Instances']:
                runningEc2Ids.append(instance['InstanceId'])
print(noOfMessages,runningEc2Ids)
# Total number of instance required for the messages in the queue
target = 50
requiredEc2 = math.ceil(noOfMessages/target)
noOfRunningEc2 = len(runningEc2Ids)
# Autoscaling
if noOfRunningEc2 == requiredEc2:
        print("Autoscaling not required!")
# Scaling-in
if noOfRunningEc2>requiredEc2:
        remove = noOfRunningEc2 - requiredEc2
        print(ec2.terminate_instances(InstanceIds=runningEc2Ids[:remove]))
# Scaling-out
else:
        add = requiredEc2 - noOfRunningEc2
        response=ec2.create_instances(ImageId='ami-0bb1040fdb5a076bc',InstanceType='t2.micro',KeyName='test',MinCount=add,TagSpecifications=[{
                                'ResourceType': 'instance','Tags': [
                                {
                                        'Key': 'Type',
                                        'Value': 'Autoscale'
                                },
                                {
                                        'Key': 'Name',
                                        'Value': 'AppTier'
                                },
                                ]
                        },
                        ])
        print(response)