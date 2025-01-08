#!/bin/python

import boto3
import os
import requests

RAM = 8
VCPU = 4


def create_launch_template():
    ec2 = boto3.client('ec2')
    response = ec2.create_launch_template(
        LaunchTemplateName='autoscaling-korea-oneinstance',
        VersionDescription='Version 1',
        LaunchTemplateData={
            'ImageId': 'ami-0e2c8caa4b6378d8c',
            'KeyName': 'autoscaling-korea',
            'UserData': open('userdata.sh').read().replace('<GH_TOKEN>', os.environ['GH_TOKEN']),
        }
    )

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
            'SpotTargetCapacity': 1
        },
        Type='instant',
    )


def launch_kmu_instance():
    ec2 = boto3.client('ec2')
    kmu_endpoint = "https://1od368a36h.execute-api.us-west-2.amazonaws.com/default/optimal_combination?"
    kmu_endpoint += f"InstanceTypes=%5B'c5','c6i','c7i'%5D&Regions=%5B'us-east-1'%5D&SelectBy=PPCP&FunctionNum=1&MemPerFunction={RAM}"

    response = requests.get(kmu_endpoint)
    response_json = response.json()

    zone_to_az = {}
    response = ec2.describe_availability_zones()
    for az in response['AvailabilityZones']:
        zone_to_az[az['ZoneId']] = az['ZoneName']

    instance_type = list(response_json[0].keys())[0]
    instance_type = instance_type.replace("'", "").replace("(", "").replace(")", "")
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
            'SpotTargetCapacity': 1
        },
        Type='instant',
    )


if __name__ == '__main__':
    create_launch_template()
    launch_aws_instance()

