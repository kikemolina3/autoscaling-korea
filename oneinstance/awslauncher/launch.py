#!/bin/python

from datetime import datetime
import boto3
import os
import requests
import base64
import argparse

RAM = 8
VCPU = 4
BUCKET = 'korea-oneinstance'


def create_launch_template(date, program, duration):
    ec2 = boto3.client('ec2')

    with open('userdata.sh', 'r') as file:
        user_data = file.read().replace('[GH_TOKEN]', os.environ['GH_TOKEN'])
        user_data = user_data.replace('[PROGRAM]', program)
        user_data = user_data.replace('[DURATION]', str(duration))
        user_data = user_data.replace('[BUCKET]', BUCKET)
        user_data = user_data.replace('[DATE]', date)

    user_data_base64 = base64.b64encode(
        user_data.encode('utf-8')).decode('utf-8')

    def create_lt():
        return ec2.create_launch_template(
            LaunchTemplateName='autoscaling-korea-oneinstance',
            VersionDescription='Version 1',
            LaunchTemplateData={
                'ImageId': 'ami-0e2c8caa4b6378d8c',
                'KeyName': 'autoscaling-korea',
                'UserData': user_data_base64,
                'IamInstanceProfile': {
                    # TODO: unharcode and manage via code
                    'Name': 'lithops-iam-instance-profile'
                },
            },
        )

    try:
        response = create_lt()
    except ec2.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'InvalidLaunchTemplateName.AlreadyExistsException':
            # Delete and recreate
            ec2.delete_launch_template(
                LaunchTemplateName='autoscaling-korea-oneinstance')
            response = create_lt()

    return response['LaunchTemplate']['LaunchTemplateName']


def launch_aws_instance():
    ec2 = boto3.client('ec2')
    ec2.create_fleet(
        SpotOptions={
            'AllocationStrategy': 'lowest-price',
        },
        LaunchTemplateConfigs=[
            {
                'LaunchTemplateSpecification': {
                    'LaunchTemplateName': 'autoscaling-korea-oneinstance',
                    'Version': '1'
                },
                "Overrides": [
                    {
                        "InstanceRequirements": {
                            "VCpuCount": {
                                "Min": VCPU,
                                "Max": VCPU,
                            },
                            "MemoryMiB": {
                                "Min": RAM * 1024,
                                "Max": RAM * 1024,
                            },
                        }
                    }
                ],
            }
        ],
        TargetCapacitySpecification={
            'TotalTargetCapacity': 1,
            'OnDemandTargetCapacity': 0,
            'SpotTargetCapacity': 1,
            'DefaultTargetCapacityType': 'spot'
        },
        Type='instant',
    )


def launch_kmu_instance(policy='PPF'):
    ec2 = boto3.client('ec2')
    kmu_endpoint = "https://1od368a36h.execute-api.us-west-2.amazonaws.com/default/optimal_combination?"
    kmu_endpoint += f"InstanceTypes=%5B'c5','c6i','c7i'%5D&Regions=%5B'us-east-1'%5D&SelectBy={policy}&FunctionNum=1&MemPerFunction={RAM}"

    response = requests.get(kmu_endpoint)
    response_json = response.json()

    zone_to_az = {}
    response = ec2.describe_availability_zones()
    for az in response['AvailabilityZones']:
        zone_to_az[az['ZoneId']] = az['ZoneName']

    instance_type = list(response_json[0].keys())[0]
    instance_type = instance_type.replace(
        "'", "").replace("(", "").replace(")", "")
    instance_type, zone = instance_type.split(",")
    instance_type = instance_type.strip()
    zone = zone.strip()
    az = zone_to_az[zone]

    ec2.create_fleet(
        LaunchTemplateConfigs=[
            {
                'LaunchTemplateSpecification': {
                    'LaunchTemplateName': 'autoscaling-korea-oneinstance',
                    'Version': '1'
                },
                'Overrides': [
                    {
                        'InstanceType': instance_type,
                        'WeightedCapacity': 1,
                        'AvailabilityZone': az
                    }
                ]
            }
        ],
        TargetCapacitySpecification={
            'TotalTargetCapacity': 1,
            'OnDemandTargetCapacity': 0,
            'SpotTargetCapacity': 1,
            'DefaultTargetCapacityType': 'spot'
        },
        Type='instant',
    )

    print("*** KMU oracle response ***")
    print(response_json)

    return response_json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--program', type=str,
                        help='The program to execute', required=True)
    parser.add_argument('--duration', type=int,
                        help='The duration of the test', default=60)
    parser.add_argument('--ppcp', action='store_true',
                        help='Use ppcp oracle; otherwise use ppf')
    
    date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    args = parser.parse_args()

    assert args.program in ["compilation", "encoding"]

    create_launch_template(date, args.program, args.duration)
    oracle_response = launch_kmu_instance(policy='PPCP') if args.ppcp else launch_kmu_instance(policy='PPF')

    s3 = boto3.client('s3')
    s3.put_object(Bucket=BUCKET, Key=f'{args.program}/{date}/oracle-response.json', Body=str(oracle_response))
