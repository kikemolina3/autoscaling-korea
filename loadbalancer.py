import boto3

elbv2_client = boto3.client('elbv2')

response = elbv2_client.create_load_balancer(
    Name='my-app-alb',
    Subnets=['subnet-xxxxxxxx', 'subnet-yyyyyyyy'], 
    SecurityGroups=['sg-xxxxxxxx'],  
    Scheme='internet-facing', 
    LoadBalancerType='application', 
    IpAddressType='ipv4',
)

alb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
print(f"ALB ARN: {alb_arn}")

autoscaling = boto3.client('autoscaling')

response_launch_template = autoscaling.create_launch_template(
    LaunchTemplateName='my-launch-template',
    VersionDescription='v1',
    LaunchTemplateData={
        'ImageId': 'ami-xxxxxxxx',  
        'InstanceType': 't2.micro', 
        'SecurityGroupIds': ['sg-xxxxxxxx'],
        'KeyName': 'my-key-pair', 
    }
)

response_asg = autoscaling.create_auto_scaling_group(
    AutoScalingGroupName='my-auto-scaling-group',
    LaunchTemplate={
        'LaunchTemplateName': 'my-launch-template',
        'Version': '1'
    },
    MinSize=1,
    MaxSize=5,
    DesiredCapacity=2,
    AvailabilityZones=['us-west-2a', 'us-west-2b'],  
    HealthCheckType='EC2',
    HealthCheckGracePeriod=300, 
    VPCZoneIdentifier='subnet-xxxxxxxx,subnet-yyyyyyyy',  
    LoadBalancerNames=['my-app-alb'],
)


response_health_check = elbv2_client.modify_target_group(
    TargetGroupArn='arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-target-group/xxxxxxxxxxxx',
    HealthCheckProtocol='HTTP',
    HealthCheckPort='80',
    HealthCheckPath='/health',
    HealthyThresholdCount=3,
    UnhealthyThresholdCount=3,
    HealthCheckIntervalSeconds=30,
    HealthCheckTimeoutSeconds=5,
)

response = elbv2_client.describe_target_health(
    TargetGroupArn='arn:aws:elasticloadbalancing:us-west-2:123456789012:targetgroup/my-target-group/xxxxxxxxxxxx'
)

for target in response['TargetHealthDescriptions']:
    print(f"ID de instancia: {target['Target']['Id']}, Estado de salud: {target['TargetHealth']['State']}")
