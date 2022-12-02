import boto3
import os
from dotenv import load_dotenv
import math
import time

load_dotenv('../key.env')

responseQueue = boto3.client('sqs', region_name="us-east-1",
        aws_access_key_id=os.environ.get('AWS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET'))
ec2 = boto3.client('ec2', region_name="us-east-1",
        aws_access_key_id=os.environ.get('AWS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET'))
zeroInstances = False
zero_time = time.time()
def run():
        global zeroInstances
        global zero_time
        # Get the queue URL
        requestQueue_url = 'https://sqs.us-east-1.amazonaws.com/158146116237/RequestQueue'
        # Fetch the ApproximateNumberOfMessages from the queue
        requestQueue_attributes = responseQueue.get_queue_attributes(QueueUrl=requestQueue_url, AttributeNames=['ApproximateNumberOfMessages'])
        noOfMessages = int(requestQueue_attributes['Attributes']['ApproximateNumberOfMessages'])
        # Fetch ids of the running instances
        runningEc2 = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running','pending']},{'Name': 'tag:tier', 'Values': ['app']}])
        runningEc2Ids = []
        # List of IDs of running instances
        if runningEc2['Reservations']:
                for res in runningEc2['Reservations']:
                	for instance in res['Instances']:
                        	runningEc2Ids.append(instance['InstanceId'])
        print(noOfMessages,runningEc2Ids)
        # Total number of instance required for the messages in the queue
        target = 10
        requiredEc2 = min(math.ceil(noOfMessages/target), 20)
        print("required = " + str(requiredEc2))
        noOfRunningEc2 = len(runningEc2Ids)
        print("running = " + str(noOfRunningEc2))
        if requiredEc2 == 0 and noOfRunningEc2 > 0:
                if zeroInstances:
                        mins = (time.time() - zero_time) // 60
                        if mins < 1:
                              requiredEc2 = 1
                        print("Minutes elapsed since zero instances required: " + str(mins))
                else:
                        zero_time = time.time()
                        zeroInstances = True
                        requiredEc2 = 1
                        print("First time zero instances required")
                print("New required count: " + str(requiredEc2))
        elif zeroInstances and requiredEc2 > 0:
                zeroInstances = False
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
                response=ec2.run_instances(ImageId='ami-007a2ee2e2b3f8172',InstanceType='t2.micro',KeyName='test',MinCount=add,MaxCount=add,UserData=user_data,TagSpecifications=[{
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
                
if __name__ == "__main__":
        while True:
                run()
                time.sleep(10)
                
