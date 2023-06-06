###################################################################################
###############   Written by Mark Snyder  Juniper Networks       ##################
###############   msnyder@juniper.net                            ##################
###################################################################################


import boto3
from datetime import datetime
from datetime import timezone
import time
import sys
import logging

def lambda_handler(event, context):
    print('###############################')
    try:
        print(event)
        organizationalUnitId=event['detail']['serviceEventDetails']['registerOrganizationalUnitStatus']['organizationalUnit']['organizationalUnitId']
        organizationalUnitName=event['detail']['serviceEventDetails']['registerOrganizationalUnitStatus']['organizationalUnit']['organizationalUnitName']
        recipientAccountId=event['detail']['serviceEventDetails']
        awsregion=event['detail']['awsRegion']
        print(' ----- Retrieved organizational registration info for Organizational Unit ', organizationalUnitName, ' with Id', organizationalUnitId, 'by account', recipientAccountId)
    except:
        print('No event data')

    print('##############################')
    main(organizationalUnitId,organizationalUnitName,awsregion)

def gtime():
    timenow=datetime.now()
    ctime=timenow.strftime('%m%d%Y-%H%M%S')
    return ctime

def setargs():
    setname='jnpr-'
    hssturl="https://ct-jnpr.s3.amazonaws.com/"
    rssturl="https://forgtest.s3.amazonaws.com/"
    args={"setname":setname, "hssturl":hssturl,"rssturl":rssturl }
    return args

def getJNPRSECVPCAccount(awsregion):
    client = AR2('ssm',awsregion)
    client.get_parameter(Name='_SSMJNPRSECVPCAccount')
    response = client.get_parameter(
        Name='_SSMJNPRSECVPCAccount'
        )
    JNPRSECVPCAccount=response['Parameter']['Value']
    return JNPRSECVPCAccount

def tgwid(awsregion):
    tgwid='empty'
    arg=setargs()
    numberoftgw=0

    client = boto3.client('sts')
    response = client.assume_role(
        RoleArn='arn:aws:iam::766484772322:role/AWSControlTowerExecution',
        RoleSessionName='jnpr-describe-tgwid'
        )
    print (response["Credentials"]['AccessKeyId'], response["Credentials"]['SecretAccessKey'], response["Credentials"]['SessionToken'])
    session = boto3.Session(aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'], region_name=awsregion)

    client = boto3.client('sts')
    data = client.get_caller_identity()
    print('UserId=',data['UserId'], 'Account=', data['Account'], 'Arn=', data['Arn'] )
    client = boto3.client('ec2',aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'],region_name=awsregion)
    response = client.describe_transit_gateways()
    print('Describe_transit_gateways >>',response)

    for TGWs in response['TransitGateways']:
        numberoftgw=numberoftgw+1
        if TGWs['State'] == 'available':
            for tgwtags in TGWs['Tags']:
                if tgwtags['Key'] == 'JNPRSECVPClogicalid':
                    if tgwtags['Value'] == '101':
                        tgwid = TGWs['TransitGatewayId']
                        print(' >>> Transit Gateway ID found =', tgwid)
                        return tgwid

    print(' Number of TGWs found ', numberoftgw)

def tgwrouteid(awsregion):
    arg=setargs()
    print('**Starteded getting tgw route table ID')
    jnprtgwid=tgwid(awsregion)
    print('jnprtgwid >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',jnprtgwid)
    client = boto3.client('sts')
    response = client.assume_role(
        RoleArn='arn:aws:iam::766484772322:role/AWSControlTowerExecution',
        RoleSessionName='jnpr-describe-tgwid'
        )
    print (response["Credentials"]['AccessKeyId'], response["Credentials"]['SecretAccessKey'], response["Credentials"]['SessionToken'])
    session = boto3.Session(aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'], region_name=awsregion)

    client = boto3.client('sts')
    data = client.get_caller_identity()
    print('UserId=',data['UserId'], 'Account=', data['Account'], 'Arn=', data['Arn'] )
    client = boto3.client('ec2',aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'],region_name=awsregion)
    print('Executing describe tgw route table ID')
    response = client.describe_transit_gateway_route_tables(
            Filters=[
                {
                    'Name': 'transit-gateway-id',
                    'Values': [
                        jnprtgwid,
                    ]
                },
            ],
            MaxResults=123
    )

    for listitem in response['TransitGatewayRouteTables']:
        print('list ', listitem)
        if listitem['TransitGatewayId'] == jnprtgwid:
            jnprtgwroutetbleid = listitem['TransitGatewayRouteTableId']
            print(' >>> TGW Route Table Id  ', jnprtgwroutetbleid)
            return jnprtgwroutetbleid

def hstackadd(ctime,organizationalUnitId,awsregion):
    args=setargs()
    JNPRSECVPCAccount=getJNPRSECVPCAccount(awsregion)
    client = boto3.client('organizations')
    response = client.describe_organizational_unit(
    OrganizationalUnitId=organizationalUnitId
    )

    arnou=response['OrganizationalUnit']['Arn']
    print('>>>>>>>> ARN for target OU is', arnou, 'Freindly name is', response['OrganizationalUnit']['Name'] )
    client = boto3.client('cloudformation')
    response = client.create_stack_set(
        StackSetName=args["setname"]+'hstackadd-'+organizationalUnitId+'-'+ctime,
        Description='testing',
            TemplateURL="https://ct-jnpr.s3.amazonaws.com/hstackadd.json",
            Parameters=[
                {
                    'ParameterKey': 'ARNOU',
                    'ParameterValue': arnou,
                },
            ],
            Tags=[
                {
                'Key': 'Juniper',
                'Value': 'testing123'
                },
            ],
            PermissionModel='SELF_MANAGED',
            )
    print('>>>>>>>>>>>>>> region',awsregion,'JNPRSECVPCAccount', JNPRSECVPCAccount )
    response = client.create_stack_instances(
    StackSetName=args["setname"]+'hstackadd-'+organizationalUnitId+'-'+ctime,
            Accounts=[
            JNPRSECVPCAccount
            ],
            Regions=[
            awsregion,
            ]
    )

def rsst1(ctime, organizationalUnitId, CIDRblocks,awsregion):  #
    print('#  **Starting rsst1 deployment')
    jnprtgwid=tgwid(awsregion)
    tgwrtbleid=tgwrouteid(awsregion)
    args=setargs()
    client = boto3.client('cloudformation')
    response = client.create_stack_set(
        StackSetName=args["setname"]+'rsst1-'+organizationalUnitId+'-'+ctime,
        Description='testing',
            TemplateURL=args["hssturl"]+'rsst1.json',
            Parameters=[
                {
                    'ParameterKey': 'jnprtgwidremote',
                    'ParameterValue': jnprtgwid,
                },
                {
                    'ParameterKey': 'CIDR',
                    'ParameterValue': CIDRblocks[0]+'/16',
                },
                {
                    'ParameterKey': 'CIDRsub0',
                    'ParameterValue': CIDRblocks[0]+'/24',
                },
                {
                    'ParameterKey': 'CIDRsub1',
                    'ParameterValue': CIDRblocks[1]+'/24',
                },
                {
                    'ParameterKey': 'CIDRsub2',
                    'ParameterValue': CIDRblocks[2]+'/24',
                },
                {
                    'ParameterKey': 'CIDRsub3',
                    'ParameterValue': CIDRblocks[3]+'/24',
                },
            ],
            Capabilities=[
            'CAPABILITY_IAM','CAPABILITY_NAMED_IAM','CAPABILITY_AUTO_EXPAND',
            ],

            PermissionModel='SERVICE_MANAGED',

            AutoDeployment={
            'Enabled': True,
            'RetainStacksOnAccountRemoval': True
            }
    )
    print('response >>>', response)
    response = client.create_stack_instances(
    StackSetName=args["setname"]+'rsst1-'+organizationalUnitId+'-'+ctime,
    DeploymentTargets={
    'OrganizationalUnitIds': [
    organizationalUnitId,
    ]
    },

    Regions=[
    awsregion,
    ]
    )
    print('#  Finished rsst1 deployment')

def rsstd(ctime, organizationalUnitId, CIDRblocks,awsregion):  #
    print('#  **Starting rsst-d deployment')
    jnprtgwid=tgwid(awsregion)
    tgwrtbleid=tgwrouteid(awsregion)
    args=setargs()
    client = boto3.client('cloudformation')
    response = client.create_stack_set(
        StackSetName=args["setname"]+'rsst-d-'+organizationalUnitId+'-'+ctime,
        Description='testing',
            TemplateURL=args["hssturl"]+'rsst-d.json',
            Parameters=[
                {
                    'ParameterKey': 'jnprtgwidremote',
                    'ParameterValue': jnprtgwid,
                },
                {
                    'ParameterKey': 'CIDR',
                    'ParameterValue': CIDRblocks[0]+'/16',
                },
                {
                    'ParameterKey': 'CIDRsub0',
                    'ParameterValue': CIDRblocks[0]+'/24',
                },
                {
                    'ParameterKey': 'CIDRsub1',
                    'ParameterValue': CIDRblocks[1]+'/24',
                },
                {
                    'ParameterKey': 'CIDRsub2',
                    'ParameterValue': CIDRblocks[2]+'/24',
                },
                {
                    'ParameterKey': 'CIDRsub3',
                    'ParameterValue': CIDRblocks[3]+'/24',
                },
            ],
            Capabilities=[
            'CAPABILITY_IAM','CAPABILITY_NAMED_IAM','CAPABILITY_AUTO_EXPAND',
            ],

            PermissionModel='SERVICE_MANAGED',

            AutoDeployment={
            'Enabled': True,
            'RetainStacksOnAccountRemoval': True
            }
    )
    print('response >>>', response)
    response = client.create_stack_instances(
    StackSetName=args["setname"]+'rsst-d-'+organizationalUnitId+'-'+ctime,
    DeploymentTargets={
    'OrganizationalUnitIds': [
    organizationalUnitId,
    ]
    },

    Regions=[
    awsregion,
    ]
    )
    print('#  Finished rsst-d deployment')


def AR(awsregion):
    arg=setargs()
    client = boto3.client('sts')
    response = client.assume_role(
        RoleArn='arn:aws:iam::766484772322:role/AWSControlTowerExecution',
        RoleSessionName='jnpr-describe-tgwid'
        )
    print (response["Credentials"]['AccessKeyId'], response["Credentials"]['SecretAccessKey'], response["Credentials"]['SessionToken'])
    session = boto3.Session(aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'], region_name=awsregion)
    client = boto3.client('sts')
    data = client.get_caller_identity()
    print('UserId=',data['UserId'], 'Account=', data['Account'], 'Arn=', data['Arn'] )
    client = boto3.client('ec2',aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'],region_name=awsregion)
    return client

def AR2(service,awsregion):
    client = boto3.client('sts')
    response = client.assume_role(
        RoleArn='arn:aws:iam::766484772322:role/marks-allow-secvpc-toaccess-ssm-parms',
        RoleSessionName='delete-stacksets'
        )
    session = boto3.Session(aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'], region_name=awsregion)
    client = boto3.client('sts')
    if service=='cloudformation':
        client = boto3.client('cloudformation',aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'],region_name=awsregion)
    if service=='ec2':
        client = boto3.client('ec2',aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'],region_name=awsregion)
    if service=='ssm':
        client = boto3.client('ssm',aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'],region_name=awsregion)
    return client

def gettgnetwattid(awsregion):
    print('begin script gettgnetwattid   >>>')
    jnprtgwid=tgwid(awsregion)
    numberofatt=0
    tgwatachid='mt'
    client=AR(awsregion)
    response = client.describe_transit_gateway_attachments(
    Filters=[
        {
            'Name': 'transit-gateway-id',
            'Values': [
                jnprtgwid,
            ]
        },
    ],
    )
    print ('response', response)
    for attachments in response['TransitGatewayAttachments']:
        numberofatt=numberofatt+1
        print(attachments)
        print('Found attachments ', attachments['TransitGatewayAttachmentId'], attachments['State'])
        if attachments['State'] == 'available':
            print('>>> Transit Gateway Attackment Id ', attachments['TransitGatewayAttachmentId'])
            for atttags in attachments['Tags']:
                if atttags['Key'] == 'JNPRSECVPClogicalid':
                    if atttags['Value'] == '101':
                        tgwatachid = attachments['TransitGatewayAttachmentId']

    print(' >>> TGW attachment found', tgwatachid)
    return tgwatachid
    print(' Number of TGW atachments found ', numberofatt)

def rCIDR():
    client = boto3.client('ssm')

    try:
        client.get_parameter(Name='rCIDR')
        CIDRblocks=[]
        response = client.get_parameter(
        Name='rCIDR'
        )

        value=response['Parameter']['Value']
        addspace=(value.split(','))
        oct1=addspace[0]
        oct2int=int(addspace[1])
        oct3int=int(addspace[2])
        oct4=addspace[3]

        oct2int=oct2int+1
        oct2=str(oct2int)
        CIDRb=oct1+'.'+oct2+'.'+str(oct3int)+'.'+'/24'
        print(CIDRb)

        print('Existing network CIDRs found. Networks 10.1.0.0/24 -', CIDRb,'/24 in use')

        i=0
        oct3int=0
        while i <= 3:
        #    print('Creating additonal CIDR network value = ', '10.10.',valint,'.0/24')
            oct3=str(oct3int)
            CIDRb=oct1+'.'+oct2+'.'+oct3+'.'+oct4
            print(CIDRb)
            CIDRblocks.append(CIDRb)
            oct3int=oct3int+64
            i=i+1

        CIDRbstr=CIDRb.replace('.',',')
        response = client.put_parameter(
        Name='rCIDR',
        Value=CIDRbstr,
        Type='StringList',
        Overwrite=True,
        )

    except:
        # if client.get_parameter(Name='rCIDR') == True:
        print('*****Initializing networks CIDR range for the first time****')
        oct1=10
        oct2=1
        oct3=0
        oct4=0
        mask='/24'
        while oct3 <= 192:
            print('Creating CIDR network value = ', '10.1.',oct3,'.0/24')
            oct3=oct3+64

            response = client.put_parameter(
            Name='rCIDR',
            Description='Do not delete, used for Control Tower IP address CIDR block for Child Organizational Units',
            Value='10,1,0,0',
            Type='StringList',
            Overwrite=True,
            )
            CIDRblocks=('10.1.0.0','10.1.64.0','10.1.128.0','10.1.192.0','/24 VPC /16')

    print('>>>>Address to be used >>>', CIDRblocks, '/24')
    # needs tags but, can't do overwrite and tags at the same time.

    print(' >>>>>> Completed CIDR >>>>>>>>')
    return CIDRblocks

def addDG4TGW(awsregion):
    print('**Starteded TGW routing table updatefor remote   >>>')
    arg=setargs()
    tgwrtbleid=tgwrouteid(awsregion)
    tgwattid=gettgnetwattid(awsregion)
    client = boto3.client('sts')
    response = client.assume_role(
        RoleArn='arn:aws:iam::766484772322:role/AWSControlTowerExecution',
        RoleSessionName='jnpr-describe-tgwid'
        )
    session = boto3.Session(aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'], region_name=awsregion)
    client = boto3.client('sts')
    try:
        client = boto3.client('ec2',aws_access_key_id=response["Credentials"]['AccessKeyId'], aws_secret_access_key=response["Credentials"]['SecretAccessKey'], aws_session_token=response["Credentials"]['SessionToken'],region_name=awsregion)

        #client = boto3.client('ec2')
        response = client.create_transit_gateway_route(
        DestinationCidrBlock='0.0.0.0/0',
        TransitGatewayRouteTableId=tgwrtbleid,
        TransitGatewayAttachmentId=tgwattid
        )
        print(response)
    except:
        print('******Static route 0.0.0.0/0 update was not performed.  Does it already exist**********')

def main(organizationalUnitId,organizationalUnitName,awsregion):
    ctime=gtime()
    print('**Starting deployment at '+ctime, '>', organizationalUnitId,'>',organizationalUnitName, '>', awsregion )
    hstackadd(ctime,organizationalUnitId,awsregion)
    time.sleep(90)  # needs get status rather than timer
    CIDRblocks=rCIDR()
    #rsst1(ctime, organizationalUnitId, CIDRblocks,awsregion)  # centralized model
    rsstd(ctime, organizationalUnitId, CIDRblocks,awsregion)  # Micro Model
    addDG4TGW(awsregion)
    time.sleep(100) # needs get status rather than timer
    print('###################>>>>>>>>>>>>>>>Ending deployment Bye<<<<<<<<<<<<<<<<<<<<#######################')
