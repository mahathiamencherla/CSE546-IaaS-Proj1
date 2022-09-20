import boto3
import os
from dotenv import load_dotenv

load_dotenv('../key.env')

QUEUE_NAME = "RequestQueue"
ASG_NAME = "app-tier"

responseQueue = boto3.client('sqs', region_name="us-east-1",
        aws_access_key_id=os.environ.get('AWS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET'))
autoscalingGroup = boto3.client('autoscaling', region_name="us-east-1",
        aws_access_key_id=os.environ.get('AWS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET'))
cloudwatch = boto3.client('cloudwatch', region_name="us-east-1",
        aws_access_key_id=os.environ.get('AWS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET'))
# Get the queue URL
requestQueue_url = 'https://sqs.us-east-1.amazonaws.com/676148463056/RequestQueue'
# Fetch the ApproximateNumberOfMessages from the queue
requestQueue_attributes = responseQueue.get_queue_attributes(QueueUrl=requestQueue_url, AttributeNames=['ApproximateNumberOfMessages'])
noOfMessages = int(requestQueue_attributes['Attributes']['ApproximateNumberOfMessages'])
# Fetch the details of the autoscaling 
autoscalingGroup_detail = autoscalingGroup.describe_auto_scaling_groups(AutoScalingGroupNames=[ASG_NAME])
# Find the number of `InService` instances in the autoscaling group
autoscalingGroup_instances = autoscalingGroup_detail['AutoScalingGroups'][0]['Instances']
inService_instances = len([i for i in autoscalingGroup_instances if i['LifecycleState'] == 'InService'])
# Calculate the BacklogPerInstance metric
if inService_instances != 0:
    backlog_per_instance = noOfMessages / inService_instances
else:
    backlogPerInstance = noOfMessages
print(backlogPerInstance)
# Push the metric to Cloudwatchput_metric_data
cloudwatch.put_metric_data(
 Namespace='SQSCustomMetric',
 MetricData=[
    {
     'MetricName': 'BacklogPerInstance',
     'Dimensions': [{'Name': 'AutoScaleGroup','Value': ASG_NAME}],
     'Value': backlogPerInstance,
     'Unit': 'None'
     }
   ]
)