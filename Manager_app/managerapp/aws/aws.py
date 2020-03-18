import boto3
import json
from math import ceil
import logging
from botocore.exceptions import ClientError
import time
from operator import itemgetter

class Awsclient:
    def __init__(self):
        self.ec2=boto3.client('ec2')
        self.s3 = boto3.client('s3')
        self.elb = boto3.client('elbv2')
        self.bucket = 'userimages-ece1779'
        self.TargetgroupARN='arn:aws:elasticloadbalancing:us-east-1:172421290625:targetgroup/newtest/0e2eea718240f4ef'
        self.cloudwatch = boto3.client('cloudwatch')
        self.image_id = 'ami-0f47fdcfbeac2985d'
        self.instance_type = 't2.micro'
        self.user_app_tag = 'Userapp'
        self.keypair_name = 'ece1779'
        self.security_group = ['ece1779a2']
        self.monitoring = {
            'Enabled': False
        }
        self.tag_specification = [{
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': self.user_app_tag
                }]
        }]
        self.zone = {
            'AvailabilityZone': 'us-east-1a'
        }
        with open('Userdata.txt', 'r') as myfile:
            data=myfile.read()
        self.userdata=data

        # self.IamInstanceProfile = {
        #                          'Arn': 'arn:aws:iam::172421290625:instance-profile/ece1779a2',
        #                          'Name': 'ece1779a2'
        # }
        self.IamInstanceProfile = {
            'Name': 'ece1779a2'
        }



    def create_ec2_instance(self):
        try:
            response = self.ec2.run_instances(ImageId=self.image_id,
                                                InstanceType=self.instance_type,
                                                KeyName=self.keypair_name,
                                                MinCount=1,
                                                MaxCount=1,
                                                SecurityGroups=self.security_group,
                                                TagSpecifications=self.tag_specification,
                                                Monitoring = self.monitoring,
                                                Placement = self.zone,
                                                UserData=self.userdata,
                                                IamInstanceProfile=self.IamInstanceProfile)
            return response['Instances'][0]

        except ClientError as e:
            logging.error(e)
            return None

    def get_Userapp_instances(self):
        instances = []
        custom_filter = [{
            'Name': 'tag:Name',
            'Values': [self.user_app_tag]}]
        response = self.ec2.describe_instances(Filters=custom_filter)
        reservations = response['Reservations']
        for reservation in reservations:
            if (len(reservation['Instances']) > 0) and (reservation['Instances'][0]['State']['Name']!='terminated'):
                instances.append({
                 'Id': reservation['Instances'][0]['InstanceId'],
                 'State': reservation['Instances'][0]['State']['Name']
                })
        return instances

    def get_targetgroup_instances(self):
        response = self.elb.describe_target_health(
            TargetGroupArn=self.TargetgroupARN,
        )
        instances = []
        if 'TargetHealthDescriptions' in response:
            for target in response['TargetHealthDescriptions']:
                instances.append({
                    'Id': target['Target']['Id'],
                    'Port': target['Target']['Port'],
                    'State': target['TargetHealth']['State']
                })
        return instances

    def get_valid_targetgroup_instances(self):
        target_instances = self.get_targetgroup_instances()
        target_instances_id = []
        for item in target_instances:
            if item['State'] != 'draining':
                target_instances_id.append(item['Id'])
        return target_instances_id

    def get_stopped_instances(self):
        """
        return idle instances
        :return: instances: list
        """
        instances_tag_raw = self.get_Userapp_instances()
        instances_target_raw = self.get_targetgroup_instances()
        instances_tag = []
        instances_target = []
        for item in instances_tag_raw:
            instances_tag.append(item['Id'])
        for item in instances_target_raw:
            instances_target.append(item['Id'])
        diff_list = []
        for item in instances_tag:
            if item not in instances_target:
                diff_list.append(item)

        return diff_list


    def get_instance_state(self,instance_id):
        response=self.ec2.describe_instance_status(InstanceIds=[instance_id])
        return response

    def increase_worker_by_one(self):

        stopped_instances = self.get_stopped_instances()

        newinstanceId = None
        if stopped_instances:
            newinstanceId = stopped_instances[0]
            # start instance
            self.ec2.start_instances(
                InstanceIds=[newinstanceId]
            )
        else:
            response = self.create_ec2_instance()
            newinstanceId = response['InstanceId']


        current_state=self.get_instance_state(newinstanceId)
        while len(current_state['InstanceStatuses'])<1:
            time.sleep(1)
            current_state=self.get_instance_state(newinstanceId)

        while current_state['InstanceStatuses'][0]['InstanceState']['Name']!='running':
            time.sleep(1)
            current_state=self.get_instance_state(newinstanceId)

        response = self.elb.register_targets(
            TargetGroupArn=self.TargetgroupARN,
            Targets=[
                {
                    'Id': newinstanceId,
                    'Port': 5000
                },
            ]
        )

        if response and 'ResponseMetadata' in response and 'HTTPStatusCode' in response['ResponseMetadata']:
            return response['ResponseMetadata']['HTTPStatusCode']
        else:
            return -1

    def get_healthy_count(self, targetgroup_id,loadbalancer_id,availabilityzone_id,start_time, end_time):
        response = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='HealthyHostCount',
            Dimensions=[
                {
                    'Name': 'TargetGroup',
                    'Value': targetgroup_id,
                },
                {
                    'Name': 'AvailabilityZone',
                    'Value':availabilityzone_id,
                },
                {
                    'Name': 'LoadBalancer',
                    'Value': loadbalancer_id,
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=[
                'Maximum',
            ],
            Unit='Count'
        )
        ec2_count_stats = []
        for point in response['Datapoints']:
            hour = point['Timestamp'].hour
            minute = point['Timestamp'].minute
            time = hour + minute / 60
            # time=minute
            ec2_count_stats.append([time, point['Maximum']])
        print(ec2_count_stats)
        ec2_count_stats = sorted(ec2_count_stats, key=itemgetter(0))
        if (ec2_count_stats[0][0]):
            init_net = ec2_count_stats[0][0]
            for i in range(len(ec2_count_stats)):
                ec2_count_stats[i][0] = (ec2_count_stats[i][0] - init_net) * 60

        return ec2_count_stats
    #    if 'Datapoints' in response:
    #        datapoints = []
    #        for datapoint in response['Datapoints']:
    #            datapoints.append([
    #                int(datapoint['Timestamp'].timestamp() * 1000),
    #                float(datapoint['Maximum'])
    #            ])
    #        return json.dumps(sorted(datapoints, key=lambda x: x[0]))
    #    else:
    #        return json.dumps([[]])

