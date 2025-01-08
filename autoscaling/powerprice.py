import boto3
from botocore.exceptions import ClientError
import threading
from datetime import datetime, timedelta

SG_NAME = 'autoscaling-korea-sg'
ALB_NAME = 'power-price-alb'
ASG_NAME = 'power-price-asg'
LT_NAME = 'todefine'


def start_new_instance():
    # TODO: call kmu oracle and attach instance to ASG
    return 'i-xxxxxxxxxxxxxxxxx'


def terminate_instance():
    # TODO: call kmu oracle and detach instance from ASG
    return 'i-yyyyyyyyyyyyyyy'


def power_price_monitor():
    cloudwatch = boto3.client('cloudwatch')

    now = datetime.now()
    min_ago = now - timedelta(minutes=1)

    response = cloudwatch.get_metric_statistics(
        Period=60,
        StartTime=min_ago.strftime('%Y-%m-%dT%H:%M:%SZ'),
        EndTime=now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistics=['Average'],
        Dimensions=[{'Name': 'AutoScalingGroupName', 'Value': ASG_NAME}]
    )

    cpu_data = response['Datapoints']
    average_cpu = cpu_data[0]['Average'] if cpu_data else 0

    autoscaling = boto3.client('autoscaling')

    if average_cpu > 80:
        instance_id = start_new_instance()
        autoscaling.attach_instances(
            AutoScalingGroupName=ASG_NAME,
            InstanceIds=[instance_id]
        )
    elif average_cpu < 30:
        instance_id = terminate_instance()
        autoscaling.detach_instances(
            AutoScalingGroupName=ASG_NAME,
            InstanceIds=[instance_id],
            ShouldDecrementDesiredCapacity=True
        )
    else:
        print("No action required.")


def init_autoscaling():
    autoscaling = boto3.client('autoscaling')

    try:
        autoscaling.create_auto_scaling_group(
            AutoScalingGroupName=ASG_NAME,
            MixedInstancesPolicy={
                'LaunchTemplate': {
                    'LaunchTemplateSpecification': {
                        'LaunchTemplateName': LT_NAME,
                        'Version': '1'
                    },
                    'Overrides': [
                        {
                            'InstanceRequirements': {
                                'VCpuCount': {
                                    'Min': 0
                                },
                                'MemoryMiB': {
                                    'Min': 0
                                },
                                'MemoryGiBPerVCpu': {
                                    'Min': 2,
                                    'Max': 2
                                }
                            }
                        }
                    ]
                },
            },
            MinSize=1,
            MaxSize=10,
            DesiredCapacity=1,
            HealthCheckType='EC2',
            HealthCheckGracePeriod=60,
            AvailabilityZones=list(
                map(lambda x: f'us-east-1{x}', ['a', 'b', 'c', 'd', 'e', 'f'])),
            # LoadBalancerNames=[ALB_NAME]
        )

        print(f"Auto scaling group {ASG_NAME} created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'AlreadyExists':
            print(f"Auto scaling group {ASG_NAME} already exists.")
        else:
            raise e


def init_load_balancer(sg_id):
    elbv2_client = boto3.client('elbv2')

    ec2 = boto3.client('ec2')

    response = ec2.describe_vpcs()
    default_vpc_id = None

    for vpc in response['Vpcs']:
        if vpc.get('IsDefault'):
            default_vpc_id = vpc['VpcId']
            break

    if default_vpc_id:
        response = ec2.describe_subnets(
            Filters=[{'Name': 'vpc-id', 'Values': [default_vpc_id]}]
        )
        subnet_ids = [subnet['SubnetId'] for subnet in response['Subnets']]
    else:
        raise Exception("No default vpc found.")

    try:
        elbv2_client.create_load_balancer(
            Name=ALB_NAME,
            Subnets=subnet_ids,
            SecurityGroups=[sg_id],
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4',
        )
        print(f"Load balancer {ALB_NAME} created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'DuplicateLoadBalancerName':
            print(f"Load balancer {ALB_NAME} already exists.")
        else:
            raise e


def init_security_group():
    ec2 = boto3.client('ec2')

    try:
        response = ec2.create_security_group(
            GroupName=SG_NAME,
            Description='Security Group for Power Price ASG'
        )

        ec2.authorize_security_group_ingress(
            GroupId=response['GroupId'],
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '172.31.0.0/16'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        print(f"Security group {SG_NAME} created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidGroup.Duplicate':
            print(f"Security group {SG_NAME} already exists.")
            response = ec2.describe_security_groups(GroupNames=[SG_NAME])[
                'SecurityGroups'][0]
        else:
            raise e
    return response['GroupId']


def init_launch_template():
    ec2 = boto3.client('ec2')

    try:
        ec2.create_launch_template(
            LaunchTemplateName=LT_NAME,
            LaunchTemplateData={
                'ImageId': 'ami-0e2c8caa4b6378d8c',  # Ubuntu 24.04; x86_64
                'KeyName': 'autoscaling-korea',
                'SecurityGroups': [SG_NAME]
            }
        )
        print(f"Launch template {LT_NAME} created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidLaunchTemplateName.AlreadyExistsException':
            print(f"Launch template {LT_NAME} already exists.")
        else:
            raise e


if __name__ == '__main__':
    # Start the power price monitor thread
    # with threading.Thread(target=power_price_monitor) as thread:
    #     thread.start()

    # Initialize the ASG and other resources
    sg_id = init_security_group()
    init_launch_template()
    init_load_balancer(sg_id)
    init_autoscaling()
