# Known issues and limitations

Summary: This is a list of known issues and limitations with the integrations here.  This list is not a complete nor exhausting list but issues that are known at the time of writing

## 1. vSRX - Network Interfaces
The vSRX will need to be rebooted after initial start in order for the vSRX to see the additional interfaces added by the CloudFormation templates.

## 2. Setup
For HSST1 you will want to change your CIDR for access. It currently allows any address ssh
You will want to create your preshared keys and advance and  update the key name.

## 3. Security Groups, Route tables, Transit Gateways
Not all security groups are mapped to Network segments correctly. At the moment, only the last security group (SECG2) is configured. SECG0, SEC1 and SECG2 ... Same for Route Tables.  The reason for this behavior, the core of the project was an import (copy paste & make work and continue) from another project that I was working on.  the Transit gateway is only connected to the last network segment for each Org VPC 10.VPC.192.0/24.

## 4. One Central Security VPC
There is only one central security VPC for the moment. Future plan may include Tags that can be reviewed to allow more than one Central VPC.

## 5. Moving of accounts
For the moment any account move with trigger EventBridge and WILL delete the default VPC for that account!!!!!

## 6. Re-register
For the moment the reregistration for any OU will trigger the EventBridge and will create a stack set and address group.  Testing need to happen to determine what happens to an exist OU, if re-registered.  A check tag if exist needs to be written.

## 7. Updating Landing Zones
Updating landing zone may trigger Event bridge

## 8. Market Place vSRX image
Is currently hard coded to PAYG for the us-east-1 region

## 9. AWS region
Currently hard coded to us-east-1.  Should be noted that AWS Control Tower, is not offered in all AWS regions.

## 10. CIDRs
There should be 5 cidr class b blocks for each account. 1 block for each available VPC. At this time, there is no plan for integrating AWS IPAM. 
