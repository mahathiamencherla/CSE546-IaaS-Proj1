# CSE546-IaaS-Project-1
An elastic application that can automatically scale out and in on-demand and cost-effectively by using the AWS cloud using SQS, EC2 and S3. 

## Project Members
- Mahathi Amencherla
- Siddhant Sorann
- Vidushi Raturi

TODO - Add pem key and AWS creds and specify location here

## AWS Resources
- S3 Buckets
  - Input - input-bucket-images-cc
  - Output - output-bucket-images-cc
- SQS Queues
  - RequestQueue - https://sqs.us-east-1.amazonaws.com/246156685396/RequestQueue
  - ResponseQueue - https://sqs.us-east-1.amazonaws.com/246156685396/ResponseQueue
- Web Tier
  - URL - TODO
  - EIP - TODO

## Run locally

1. Create a key.env file to store the AWS access keys
```bash
AWS_KEY=EXAMPLE
AWS_SECRET=EXAMPLE
``` 
2. Navigate to web-tier-server folder
```bash
$ cd web-tier-server
```
3. Run this command to download all dependencies
```bash
$ npm install
```
4. Run the code
```bash
$ node web-tier-server.js
```
5. Start a new terminal and navigate to app-tier folder
```bash
$ cd app-tier
$ python3 queue-listener.py
```

6. Start a new terminal and navigate to workload-generator folder, run the code
```bash
$ cd CSE546_Sum22_workload_generator/
$ python3 workload_generator.py \
 --num_request 1 \                                    // number of images to be sent
 --url 'http://localhost:3001/api/image' \            // change ip to instance
 --image_folder "imagenet-100/"   
```