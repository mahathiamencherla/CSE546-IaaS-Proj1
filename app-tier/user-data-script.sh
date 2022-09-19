#!/bin/bash
sudo apt update
sudo apt install nodejs -y
sudo apt install npm -y
sudo apt install python3-pip -y
git clone https://github.com/mahathiamencherla/CSE546-IaaS-Proj1.git /home/ubuntu/CSE546-IaaS-Proj1
cd /home/ubuntu
sudo chown -R ubuntu CSE546-IaaS-Proj1
cd CSE546-IaaS-Proj1
echo $'AWS_KEY=<KEY>\nAWS_SECRET=<SECRET>' > key.env
sudo npm install pm2@latest -g
sudo -u ubuntu -i <<'EOF'
cd CSE546-IaaS-Proj1/app-tier
pip3 install torchvision --no-cache-dir
pip3 install boto3 --no-cache-dir
pip3 install python-dotenv --no-cache-dir
pm2 startup
pm2 start queue-listener.py --interpreter python3
pm2 save
EOF