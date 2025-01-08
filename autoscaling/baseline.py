import boto3

ASG_NAME = 'lowest-price-asg'
LT_NAME = 'todefine'

# TODO: add launch template creation

autoscaling = boto3.client('autoscaling')

response = autoscaling.create_auto_scaling_group(
    AutoScalingGroupName=ASG_NAME,
    MixedInstancesPolicy={
        'InstancesDistribution': {
            'SpotAllocationStrategy': 'lowestPrice',
            'OnDemandBaseCapacity': 0,
            'SpotInstancePools': 1, 
        },
        'LaunchTemplate': {
            'LaunchTemplateName': LT_NAME, 
            'Version': '1'
        }
    },
    MinSize=1, 
    MaxSize=10,
    DesiredCapacity=1,
    HealthCheckType='EC2',  
    HealthCheckGracePeriod=60
)

autoscaling.put_scaling_policy(
    AutoScalingGroupName=ASG_NAME,
    PolicyName='ScaleUpPolicy',
    AdjustmentType='ChangeInCapacity',
    ScalingAdjustment=1,
    Cooldown=60
)

autoscaling.put_scaling_policy(
    AutoScalingGroupName=ASG_NAME,
    PolicyName='ScaleDownPolicy',
    AdjustmentType='ChangeInCapacity',
    ScalingAdjustment=-1,  
    Cooldown=60
)


cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_alarm(
    AlarmName='ScaleUpAlarm',
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=1,
    MetricName='CPUUtilization',
    Namespace='AWS/EC2',
    Period=60, 
    Statistic='Average',
    Threshold=75, 
    ActionsEnabled=True,
    AlarmActions=[
        # TODO: add the ARN of the scaling up policy
    ],
    Dimensions=[
        {
            'Name': 'AutoScalingGroupName',
            'Value': ASG_NAME
        }
    ]
)

cloudwatch.put_metric_alarm(
    AlarmName='ScaleDownAlarm',
    ComparisonOperator='LessThanThreshold',
    EvaluationPeriods=1,
    MetricName='CPUUtilization',
    Namespace='AWS/EC2',
    Period=60,
    Statistic='Average',
    Threshold=30,
    ActionsEnabled=True,
    AlarmActions=[
        # TODO: add the ARN of the scaling down policy
    ],
    Dimensions=[
        {
            'Name': 'AutoScalingGroupName',
            'Value': ASG_NAME
        }
    ]
)

