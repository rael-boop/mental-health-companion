#!/bin/bash

rsync -avz -e "ssh -i mhc_rsa.pem" \
--exclude venv --exclude 'mhc_rsa.pem' --exclude '.git/'  \
. ec2-user@ec2-52-73-178-161.compute-1.amazonaws.com:.