# CSE546-IaaS-Project-1
An elastic application that can automatically scale out and in on-demand and cost-effectively by using the AWS cloud using SQS, EC2 and S3. 

## Project Members
- Mahathi Amencherla
- Siddhant Sorann
- Vidushi Raturi

TODO - Add pem key and AWS creds and specify location here

## AWS Resources
- S3 Buckets
  - Input - iaas-proj-input
  - Output - iaas-proj-output
- SQS Queues
  - RequestQueue - https://sqs.us-east-1.amazonaws.com/676148463056/RequestQueue
  - ResponseQueue - https://sqs.us-east-1.amazonaws.com/676148463056/ResponseQueue
- Web Tier
  - URL - TODO
  - EIP - TODO

3 terminals

1st terminal
navigate to web-tier folder 
run node web-tier-server.js

2nd terminal
navigate to app-tier folder
run python3 queue-listener.py

3rd terminal
navigate to workload generator folder
run python3 workload_generator.py \
 --num_request 1 \                                    // number of images to be sent
 --url 'http://localhost:3001/api/image' \            // change ip to instance
 --image_folder "imagenet-100/"   

