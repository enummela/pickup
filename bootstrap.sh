#!/bin/sh

apt-get update
apt-get install -y python3-pip
pip3 install --upgrade pip
pip3 install -r pickup/requirements.txt
