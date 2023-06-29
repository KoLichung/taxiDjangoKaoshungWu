#!/bin/bash

sudo yum update -y
sudo yum install python3
sudo yum install python3-pip
sudo pip3 install Django
sudo yum install git -y

sudo yum install gcc
sudo yum install python3-devel

echo "DEBUG=0" >> /etc/environment
echo 'DB_NAME=TaxiDB' >> /etc/environment

sudo cd ~
sudo git clone https://gitlab.com/jason310/taxidjango.git
sudo cd taxiDjango/
sudo pip3 install -r requirements.txt


