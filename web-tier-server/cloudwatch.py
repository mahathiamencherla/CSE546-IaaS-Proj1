import boto3
import os

QUEUE_NAME = "RequestQueue"
ASG_NAME = "app-tier"
sqs_client = boto3.client('sqs', region_name="us-east-1",
        aws_access_key_id=os.environ.get('AWS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET'))
asg_client = boto3.client('autoscaling', region_name="us-east-1",
        aws_access_key_id=os.environ.get('AWS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET'))
cw_client = boto3.client('cloudwatch', region_name="us-east-1",
        aws_access_key_id=os.environ.get('AWS_KEY'),
                       aws_secret_access_key=os.environ.get('AWS_SECRET'))
# Get the queue URL
sqs_queue_url = 'https://sqs.us-east-1.amazonaws.com/676148463056/RequestQueue'
# Fetch the ApproximateNumberOfMessages from the queue
sqs_queue_attributes = sqs_client.get_queue_attributes(QueueUrl=sqs_queue_url, AttributeNames=['ApproximateNumberOfMessages'])
number_of_messages = int(sqs_queue_attributes['Attributes']['ApproximateNumberOfMessages'])
# Fetch the details of the autoscaling 
asg_detail = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[ASG_NAME])
# Find the number of `InService` instances in the autoscaling group
asg_instances = asg_detail['AutoScalingGroups'][0]['Instances']
in_service_instances = len([i for i in asg_instances if i['LifecycleState'] == 'InService'])
# Calculate the BacklogPerInstance metric
if in_service_instances != 0:
    backlog_per_instance = number_of_messages / in_service_instances
else:
    backlog_per_instance = number_of_messages
print(backlog_per_instance)
# Push the metric to Cloudwatchput_metric_data
cw_client.put_metric_data(
 Namespace='SQSCustomMetric',
 MetricData=[
    {
     'MetricName': 'BacklogPerInstance',
     'Dimensions': [{'Name': 'AutoScaleGroup','Value': ASG_NAME}],
     'Value': backlog_per_instance,
     'Unit': 'None'
     }
   ]
)