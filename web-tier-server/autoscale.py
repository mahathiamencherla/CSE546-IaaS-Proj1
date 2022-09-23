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
requestQueue_url = 'https://sqs.us-east-1.amazonaws.com/246156685396/RequestQueue'
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
print("required = " + str(requiredEc2))
noOfRunningEc2 = len(runningEc2Ids)
print("running = " + str(noOfRunningEc2))

user_data = '''#!/bin/bash
sudo -u ubuntu -i <<'EOF'
pm2 resurrect
EOF'''

# Autoscaling
if noOfRunningEc2 == requiredEc2:
        print("Autoscaling not required!")
# Scaling-in
elif noOfRunningEc2>requiredEc2:
        remove = noOfRunningEc2 - requiredEc2
        print(ec2.terminate_instances(InstanceIds=runningEc2Ids[:remove]))
# Scaling-out
else:
        add = requiredEc2 - noOfRunningEc2
        response=ec2.run_instances(ImageId='ami-02a102f25a59e9a46',InstanceType='t2.micro',KeyName='cloud-proj',MinCount=add,MaxCount=add,UserData=user_data,TagSpecifications=[{
                                'ResourceType': 'instance','Tags': [
                                {
                                        'Key': 'tier',
                                        'Value': 'app'
                                },
                                {
                                        'Key': 'Name',
                                        'Value': 'app-tier'
                                },
                                ]
                        },
                        ])
        print(response)