#!/bin/bash

# Install python3-dev for generating executables
sudo apt-get update
sudo apt-get install -y python3-dev

# Install dependencies
pip3 install -r requirements.txt
