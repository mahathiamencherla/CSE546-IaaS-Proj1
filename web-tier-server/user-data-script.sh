#!/bin/bash
sudo apt update
sudo apt install nodejs -y
sudo apt install npm -y
git clone https://github.com/mahathiamencherla/CSE546-IaaS-Proj1.git /home/ubuntu/CSE546-IaaS-Proj1
cd CSE546-IaaS-Proj1/web-tier-server
node web-tier-server.js 
