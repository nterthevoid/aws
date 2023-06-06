###################################################################################
###############   Written by Mark Snyder  Juniper Networks       ##################
###############   msnyder@juniper.net                            ##################
###################################################################################

###  Create a stackset in Control Tower Organizational unit

import boto3
import time


def lambda_handler(event, context):
    ACTarn='mt'
    print('###############################')
    print(event)
    print('-------------------------------')
    try:
        ACTid=event['detail']['requestParameters']['accountId']
        OUid=event['detail']['requestParameters']['destinationParentId']
        client = boto3.client('organizations')
        actresponse = client.describe_account(
        AccountId=ACTid
        )
        orgresponse = client.describe_organizational_unit(
            OrganizationalUnitId=OUid
        )

        # print('>>>  Get OU info', response)

        print(' ----- Account being moved----',ACTid, 'Freindly name is', actresponse['Account']['Name'] )
        print(' ----- Account moved to ou----',OUid, 'Freindly name is', orgresponse['OrganizationalUnit']['Name'] )

    except:
        print('Error - Not found')
        OUid='Error'

    print('######################  To Do ')
    print('######################  Needs check to ensure that moved account is in a juniper securitiy org')
    print('######################  org must be a child of, since orgs have no tags')
    print('######################  needs rsst1 finished first check pre move account')




    #make sure desitnation is in vpc sec infratest
    #ACTarn=getactarn(ACTid)
    print('timer for 90 sec started needed ')
    time.sleep(90)
    ddvpc(ACTid)


def getactarn(ACTid):
    client = boto3.client('organizations')
    response = client.describe_account(
    AccountId=ACTid
    )
    ACTarn=response['Account']['Arn']
    print('-----ARN for account',ACTid,'ARN = ',ACTarn)
    return ACTarn

def ddvpc(ACTid):
    lpk=0
    InternetGatewayId2delete='mt'
    arnrole='arn:aws:iam::'+ACTid+':role/CTOUexecuterole4child'

    print('******* Starting deleting default VPC for account', ACTid)
    print('#############################################################################################################')
    print('###############............................!!!WARNING!!!...................................##################')
    print('###############..This script deletes the AWS default VPC and its Security Groups..>>>>>>>>.##################')
    print('###############----------------------------------------------------------------------------##################')
    print('###############..This script deletes ALL IGW associated with the account being moved.......##################')
    print('#############################################################################################################')

#    data=setargs()

    client = boto3.client('sts')
    response = client.assume_role(
        RoleArn=arnrole,
        RoleSessionName='Delete_default_vpc'
        )
    session = boto3.Session(aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'], region_name='us-east-1')


    client = boto3.client('ec2',aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'],region_name='us-east-1')

    response = client.describe_vpcs(
        Filters=[
            {
                'Name': 'is-default',
                'Values': ['true']
            },
        ],
    )
    print('>>>> Descripe VPC response', response)

    if response['Vpcs']:
        for item in response['Vpcs']:
            print('Found VPCid',item['VpcId'])
            vpc2delete=item['VpcId']


        IGWresponse = client.describe_internet_gateways(
            Filters=[
            {
            'Name': 'owner-id',
            'Values': [
            ACTid,
            ]
            },
            ],
            )

        print('>>internet-gateway-id>>>', IGWresponse)

        print(IGWresponse['InternetGateways'],type(IGWresponse['InternetGateways']))

        if IGWresponse['InternetGateways']:
            for item in IGWresponse['InternetGateways']:
                print('Found InternetGatewayId',item['InternetGatewayId'])
                InternetGatewayId2delete=item['InternetGatewayId']
                if IGWresponse['InternetGateways']:
                    IGWstate='mt'
                    while IGWstate != 'detached':
                        IGWstatestat = client.describe_internet_gateways(
                            Filters=[
                            {
                            'Name': 'owner-id',
                            'Values': [
                            ACTid,
                            ]
                            },
                            ],
                            )

                        ##  loop kill ion case of runaway  ##
                        lpk = lpk + 1    ######################
                        if lpk > 60:    ######################
                            IGWstate = 'detached' ##########
                        #####################################


                        if IGWstatestat['InternetGateways']:
                            time.sleep(2)
                            for item in IGWstatestat['InternetGateways']:
                                if item['Attachments']:
                                    for li in item['Attachments']:
                                        print('Curent state of attachement, checked',lpk,'times',li['State'])

                                        IGWstate=li['State']
                                        if li['State'] == 'available':
                                            IGWidresponse = client.detach_internet_gateway(
                                            InternetGatewayId=InternetGatewayId2delete,
                                            VpcId=vpc2delete
                                            )
                                            print('Detached response', IGWidresponse)
                                        else:
                                            print('IGW is not available, but in another state, trying again')
                                            whatisgoingonIGWstatestat = client.describe_internet_gateways(
                                                Filters=[
                                                {
                                                'Name': 'owner-id',
                                                'Values': [
                                                ACTid,
                                                ]
                                                },
                                                ],
                                                )

                    dIGWresponse = client.delete_internet_gateway(
                    InternetGatewayId=InternetGatewayId2delete
                    )
                    print('Delete IGW response', dIGWresponse)
        else:
            print('No Internet Gateways to remove')

        ##### delete subnets ...
        response = client.describe_subnets(
            Filters=[
                {
                    'Name': 'vpc-id',
                    'Values': [
                        vpc2delete,
                    ]
                },
            ]
        )
        print('> Describe Subnet Response',response)
        if response['Subnets']:
            for items in response['Subnets']:
                if items['SubnetId']:
                    print('>>> Subnets found', items['SubnetId'],items['CidrBlock'])
                    response = client.delete_subnet(
                        SubnetId=items['SubnetId']
                    )

        dvpcresponse = client.delete_vpc(
            VpcId=vpc2delete,
            )
        print(' >>>>Responce to delete vpc', dvpcresponse)
    else:
        print('No default VPC found')

    print('******* Finished deleting default VPC if any found for account', ACTid)
