#/bin/bash
aws cloudformation create-stack --region us-west-1 --stack-name s-2-s-vpn --template-body file://./west-coast.cft
aws cloudformation create-stack --region us-east-1 --stack-name s-2-s-vpn --template-body file://./east-coast.cft