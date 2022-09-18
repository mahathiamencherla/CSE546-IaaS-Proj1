# CSE546-IaaS-Proj1
Handling scaling in EC2 and SQS

3 terminals

1st terminal
navigate to web-tier folder 
run node web-tier-server.js

2nd terminal
navigate to app-tier folder
run python3 queue-listener.py

3rd terminal
nagivate to workload generator folder
run python3 workload_generator.py \
 --num_request 1 \                                    // number of images to be sent
 --url 'http://localhost:3001/api/image' \            // change ip to instance
 --image_folder "imagenet-100/"                       
