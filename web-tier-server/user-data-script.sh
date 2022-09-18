#!/bin/bash
sudo apt update
sudo apt install nodejs -y
sudo apt install npm -y
git clone https://github.com/mahathiamencherla/CSE546-IaaS-Proj1.git /home/ubuntu/CSE546-IaaS-Proj1
cd /home/ubuntu
sudo chown -R ubuntu CSE546-IaaS-Proj1
cd CSE546-IaaS-Proj1
echo 'AWS_KEY=<KEY>\nAWS_SECRET=<SECRET>' > key.env
sudo npm install pm2@latest -g
cd web-tier-server
sudo npm install
sudo -u ubuntu -i <<'EOF'
pm2 startup
pm2 start node -- CSE546-IaaS-Proj1/web-tier-server/web-tier-server.js
pm2 save
EOF