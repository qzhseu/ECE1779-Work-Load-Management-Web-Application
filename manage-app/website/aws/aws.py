import boto3
import json
from math import ceil
from botocore.exceptions import ClientError
import time
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class AwsClient:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.elb = boto3.client('elbv2')
        self.s3 = boto3.client('s3')
        self.bucket = 'userimages-ece1779'
        self.TargetGroupArn = \
            'arn:aws:elasticloadbalancing:us-east-1:172421290625:targetgroup/newtest/0e2eea718240f4ef'
        self.cloudwatch = boto3.client('cloudwatch')
        self.user_app_tag = 'Userapp'
        self.manager_app_tag = 'Managerapp'
        self.image_id = 'ami-01147a2ee75b5ed5a'
        self.instance_type ='t2.small'
        self.keypair_name ='ece1779'
        self.security_group=['ece1779a2']
        self.tag_specification=[{
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': self.user_app_tag
                }]
        }]
        self.monitoring = {
            'Enabled': True
        }
        self.tag_placement ={
            'AvailabilityZone': 'us-east-1a'
        }
        with open(basedir+'/Userdata.txt', 'r') as myfile:
            data = myfile.read()
        self.userdata = data
        self.IamInstanceProfile = {
            'Name': 'ece1779a2'
        }
        self.targetgroup = 'targetgroup/newtest/0e2eea718240f4ef'
        self.loadbalancer = 'app/ece1779elb-application/8ea17eb8c0921eae'
        self.availabilityzone = 'us-east-1a'

    # create instance from AMI(pre-uploaded Userapp)
    # auto start Userapp using UserData parameter
    # assign RDS and S3 previlieges with Iam role
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
                                              Placement = self.tag_placement,
                                              UserData=self.userdata,
                                              IamInstanceProfile=self.IamInstanceProfile)
            return response['Instances'][0]

        except ClientError as e:
            return None

    # get manager instance
    def get_manager_instances(self):
        instance_filter = [{
            'Name': 'tag:Name',
            'Values': [self.manager_app_tag]}]
        response = self.ec2.describe_instances(Filters=instance_filter)
        instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
        return instance_id

    # get all instances with name user_app_tag(Userapp)
    def get_tag_instances(self):
        instances = []
        instance_filter = [{
            'Name': 'tag:Name',
            'Values': [self.user_app_tag]},
            {
                'Name':'instance-state-name',
                'Values':['pending','running','stopping','stopped'],
            }
            ]
        response = self.ec2.describe_instances(Filters=instance_filter)
        reservations = response['Reservations']
        for reservation in reservations:
            if len(reservation['Instances']) > 0:
                instances.append({
                 'Id': reservation['Instances'][0]['InstanceId'],
                 'State': reservation['Instances'][0]['State']['Name']
                })
        return instances

    # get all instances in target group including idle instances
    def get_target_instances(self):
        response = self.elb.describe_target_health(
            TargetGroupArn=self.TargetGroupArn,
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

    # any instance in target group without draining status
    def get_valid_instances(self):
        target_instances = self.get_target_instances()
        target_instances_id = []
        for instance_id in target_instances:
            if instance_id['State'] != 'draining':
                target_instances_id.append(instance_id['Id'])
        return target_instances_id

    # any instance in target group with healthy status
    def get_healthy_instances(self):
        target_instances = self.get_target_instances()
        healthy_target_instances_id = []
        for instance_id in target_instances:
            if instance_id['State'] == 'healthy':
                healthy_target_instances_id.append(instance_id['Id'])
        return healthy_target_instances_id

    # get previously suspended instances
    def get_idle_instances(self):
        tagged_instances = self.get_tag_instances()
        tagged_instances_tag =[]
        # get instance with name user_app_tag(Userapp)
        for instance_id in tagged_instances:
            tagged_instances_tag.append(instance_id['Id'])
        #get instance in current target group
        targetted_instances = self.get_target_instances()
        targetted_instances_tag = []
        for instance_id in targetted_instances:
            targetted_instances_tag.append(instance_id['Id'])
        # any instance with name_tag thats not in the target group is idling
        idle_instances = []
        for instance_id in tagged_instances_tag:
            if instance_id not in targetted_instances_tag:
                idle_instances.append(instance_id)
        return idle_instances


    def grow_worker_by_one(self):
        idle_instances = self.get_idle_instances()

        workers_count=len(self.get_tag_instances())
        #grow worker by first trying to restart idle instance
        if len(idle_instances) is not 0:
            print(len(idle_instances))
            new_instance_id = idle_instances[0]
            self.ec2.start_instances(
                InstanceIds=[new_instance_id]
            )
        #if no idle instance available and instance number is smaller than 11, start new instance
        else:
            if workers_count < 10:
                response = self.create_ec2_instance()
                new_instance_id = response['InstanceId']
            else:
                return 'Worker number exceeds 10.'
        # check to see if the status of new instance changes to running
        specfic_state = self.ec2.describe_instance_status(InstanceIds=[new_instance_id])
        while len(specfic_state['InstanceStatuses']) < 1:
            time.sleep(1)
            specfic_state = self.ec2.describe_instance_status(InstanceIds=[new_instance_id])
        while specfic_state['InstanceStatuses'][0]['InstanceState']['Name'] != 'running':
            time.sleep(1)
            specfic_state = self.ec2.describe_instance_status(InstanceIds=[new_instance_id])
        # register new instance after it finishes initialization
        response = self.elb.register_targets(
            TargetGroupArn=self.TargetGroupArn,
            Targets=[
                {
                    'Id': new_instance_id,
                    'Port': 5000
                },])
        if response and 'ResponseMetadata' in response and \
                'HTTPStatusCode' in response['ResponseMetadata']:
            return response['ResponseMetadata']['HTTPStatusCode']
        else:
            return -1

    def grow_worker_by_ratio(self, ratio):
        target_instances = self.get_valid_instances()
        # determine number of instance to be added
        target_num_before = len(target_instances)
        target_num_to_increase = int(target_num_before * ratio - target_num_before)
        responses = []
        if target_num_to_increase <= 0:
            return "Ratio can not be smaller than zero."
        if len(target_instances) < 1:
            return "No available instance in target group."
        # grow worker by iteratively applying grow grow_worker_by_one()
        # upper limit of 10 is enforced within grow_worker_by_one()
        for i in range(target_num_to_increase):
            responses.append(self.grow_worker_by_one())
        return responses

    # if tag is true, worker will be stopped
    # if tag is false, worker will be terminated
    def shrink_worker_by_one(self,tag=True):
        if(tag):
            min_number=1
        else:
            min_number=0
        target_instances_id = self.get_valid_instances()
        flag, msg = True, ''
        if len(target_instances_id) > min_number:
            unregister_instance_id = target_instances_id[0]
            # unregister instance from target group
            deregister_instance_response = self.elb.deregister_targets(
                TargetGroupArn=self.TargetGroupArn,
                Targets=[
                    {
                        'Id': unregister_instance_id
                    },])
            deregister_instance_status = -1
            if deregister_instance_response and 'ResponseMetadata' in deregister_instance_response and \
                    'HTTPStatusCode' in deregister_instance_response['ResponseMetadata']:
                deregister_instance_status = deregister_instance_response['ResponseMetadata']['HTTPStatusCode']
            if int(deregister_instance_status) == 200:
                # after successful de-registration, try to stop instance
                stop_instance_status = -1
                stop_instance_response = self.ec2.stop_instances(
                    InstanceIds=[
                        unregister_instance_id,
                    ],
                    Hibernate=False,
                    Force=False
                )
                if stop_instance_response and 'ResponseMetadata' in stop_instance_response and \
                        'HTTPStatusCode' in stop_instance_response['ResponseMetadata']:
                    stop_instance_status = stop_instance_response['ResponseMetadata']['HTTPStatusCode']
                if int(stop_instance_status) == 200:
                    if (tag==False):
                        #after successful stopping, try to terminate instance when tag is false
                        terminate_instance_status = -1
<<<<<<< HEAD
                        terminate_instance_response = self.ec2.terminate_instances(InstanceIds=[unregister_instance_id])
=======
                        terminate_instance_response = self.ec2.stop_instances(InstanceIds=[unregister_instance_id])
>>>>>>> ce71bcec3eedf60f08d347f2a2bd50e63a522144
                        if terminate_instance_response and 'ResponseMetadata' in terminate_instance_response and \
                                'HTTPStatusCode' in terminate_instance_response['ResponseMetadata']:
                            terminate_instance_status = stop_instance_response['ResponseMetadata']['HTTPStatusCode']
                            if int(terminate_instance_status) != 200:
                                flag = False
                                msg = "Unable to terminate the stopped instance"
                else:
                    flag = False
                    msg = "Unable to stop the unregistered instance"
            else:
                flag = False
                msg = "Unable to unregister from target group"
        else:
            flag = False
            msg = "No workers to unregister"
        if flag == True:
            msg = "Worker was successfully unregistered"
        return [flag, msg]

    # shrink worker by ratio
    # ratio is the percentage of instances to be suspended
    def shrink_worker_by_ratio(self, ratio):
        target_instances_id = self.get_valid_instances()
        response_list = []
        target_num_before = len(target_instances_id)
        # ratio is enforced to be between 0 and 1 in forms.ConfigForm
        if len(target_instances_id) < 1:
            return [False, "Target instance group is already null", response_list]
        else:
            targets_num_after = target_num_before - ceil(target_num_before * ratio)
            for i in range(targets_num_after):
                response_list.append(self.shrink_worker_by_one(True))
            return [True, "Success", response_list]

    def stop_manager(self):
        flag, msg = True, ''
        stop_manager_instance_status = -1
        manager_instance_id = self.get_manager_instances()
        if len(manager_instance_id) > 1:
            stop_manager_instance_response = self.ec2.stop_instances(
                InstanceIds=[manager_instance_id,],
                Hibernate=False,
                Force=False
            )
            if stop_manager_instance_response and 'ResponseMetadata' in stop_manager_instance_response and \
                'HTTPStatusCode' in stop_manager_instance_response['ResponseMetadata']:
                stop_manager_instance_status = stop_manager_instance_response['ResponseMetadata']['HTTPStatusCode']
            if int(stop_manager_instance_status) != 200:
                flag = False
                msg = "Unable to stop the manager app instance"
        else:
            flag = False
            msg = "No manager instance available"
        return [flag, msg]

    # stop all instances including all users and manager
    def stop_all_instances(self):
        target_instances_id = self.get_valid_instances()
        tag_instances = self.get_tag_instances()
        response_list = []
        for item in tag_instances:
            if item['State']=='stopped':
                self.ec2.terminate_instances(InstanceIds=[item['Id']])
        if len(target_instances_id)<1:
            response_list.append(self.stop_manager())
            return [True, "Success", response_list]
        else:
            shrink_targets_num = len(target_instances_id)
            for i in range(shrink_targets_num):
                # try to terminate instance when tag for shrink_worker_by_one() is false
                response_list.append(self.shrink_worker_by_one(False))
            response_list.append(self.stop_manager())

            return [True, "Success", response_list]

    def get_cpu_utils(self, instance_id, start_time, end_time):
        response = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                },],
            StartTime=start_time,
            EndTime=end_time,
            Period=60, # detailed monitoring enabled to get CPU stats every 60s
            Statistics=[
                'Maximum',
            ],
            Unit='Percent'
        )
        if 'Datapoints' in response:
            datapoints = []
            for datapoint in response['Datapoints']:
                datapoints.append([
                    int(datapoint['Timestamp'].timestamp() * 1000),
                    float(datapoint['Maximum'])
                ])
            return json.dumps(sorted(datapoints, key=lambda x: x[0]))
        else:
            return json.dumps([[]])

    def get_healthy_count(self,start_time, end_time):
        response = self.cloudwatch.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName='HealthyHostCount',
            Dimensions=[
                {
                    'Name': 'TargetGroup',
                    'Value': self.targetgroup,
                },
                {
                    'Name': 'AvailabilityZone',
                    'Value':self.availabilityzone,
                },
                {
                    'Name': 'LoadBalancer',
                    'Value': self.loadbalancer,
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
        if 'Datapoints' in response:
            datapoints = []
            for datapoint in response['Datapoints']:
                datapoints.append([
                    int(datapoint['Timestamp'].timestamp() * 1000),
                    float(datapoint['Maximum'])
                ])
            return json.dumps(sorted(datapoints, key=lambda x: x[0]))
        else:
            return json.dumps([[]])


    def clear_s3(self):
        for key in self.s3.list_objects(Bucket=self.bucket)['Contents']:
            self.s3.delete_objects(
                Bucket=self.bucket,
                Delete={
                    'Objects': [
                        {
                            'Key': key['Key'],
                        },],
                    'Quiet': True
                },
            )
