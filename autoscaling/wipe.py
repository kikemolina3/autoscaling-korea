import boto3

SG_NAME = 'autoscaling-korea-sg'
ALB_NAME = 'power-price-alb'
ASG_NAME = 'power-price-asg'
LT_NAME = 'todefine'

def delete_security_group():
    ec2 = boto3.client('ec2')
    response = ec2.describe_security_groups(
        GroupNames=[SG_NAME]
    )
    for sg in response['SecurityGroups']:
        ec2.delete_security_group(
            GroupId=sg['GroupId']
        )

def delete_launch_template():
    ec2 = boto3.client('ec2')
    response = ec2.describe_launch_templates(
        LaunchTemplateNames=[LT_NAME]
    )
    for lt in response['LaunchTemplates']:
        ec2.delete_launch_template(
            LaunchTemplateName=lt['LaunchTemplateName']
        )

def delete_load_balancer():
    elb = boto3.client('elbv2')
    response = elb.describe_load_balancers(
        Names=[ALB_NAME]
    )
    for lb in response['LoadBalancers']:
        elb.delete_load_balancer(
            LoadBalancerArn=lb['LoadBalancerArn']
        )

def delete_auto_scaling_group():
    asg = boto3.client('autoscaling')
    response = asg.describe_auto_scaling_groups(
        AutoScalingGroupNames=[ASG_NAME]
    )
    for group in response['AutoScalingGroups']:
        asg.delete_auto_scaling_group(
            AutoScalingGroupName=group['AutoScalingGroupName']
        )

if __name__ == '__main__':
    # delete_auto_scaling_group()
    # delete_load_balancer()
    # delete_launch_template()
    delete_security_group()
    