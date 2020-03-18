from flask import render_template, redirect, url_for, request,session,flash
from flask_login import current_user
from managerapp import app
import boto3
from datetime import datetime, timedelta
from operator import itemgetter
from managerapp.aws import aws
import numpy as np
from managerapp.form import LoginForm
from managerapp.login import login,logout

awsClient = aws.Awsclient()
targetgroup='targetgroup/newtest/0e2eea718240f4ef'
loadbalancer='app/ece1779elb-application/8ea17eb8c0921eae'
availabilityzone='us-east-1a'

@app.route('/',methods=['GET'])
@app.route('/home')
# Display an HTML page with links
def home():
    user = session['user'] if 'user' in session else None
    if not user:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('ec2_list'))

@app.route('/instance')
def ec2_list():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.all()
    response=awsClient.get_stopped_instances()
    print(response)
    return render_template("list.html", instances = instances)

#
@app.route('/instance/creat',methods=['POST'])
def increase_one_worker():
    response=awsClient.increase_worker_by_one()
    if int(response) == 200:
        print("A new worker was registered")

    else:
        print( "Unable to register a new worker")
    return redirect(url_for('ec2_list'))


@app.route('/ec2_examples/<id>',methods=['GET'])
#Display details about a specific instance.
def ec2_view(id):
    ec2 = boto3.resource('ec2')

    instance = ec2.Instance(id)

    client = boto3.client('cloudwatch')

    ##   CPUUtilization, NetworkIn, NetworkOut, NetworkPacketsIn,
    #    NetworkPacketsOut, DiskWriteBytes, DiskReadBytes, DiskWriteOps,
    #    DiskReadOps, CPUCreditBalance, CPUCreditUsage, StatusCheckFailed,
    #    StatusCheckFailed_Instance, StatusCheckFailed_System


    namespace = 'AWS/EC2'
    # could be Sum,Maximum,Minimum,SampleCount,Average

    cpu = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=30 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='CPUUtilization',
        Namespace=namespace,  # Unit='Percent',
        Statistics=['Average'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )
    #print(cpu)

    cpu_stats =[]

    for point in cpu['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time=hour+minute/60
        cpu_stats.append([time,point['Average']])

    cpu_stats = sorted(cpu_stats, key=itemgetter(0))
    if(cpu_stats[0][0]):
        init_cpu=cpu_stats[0][0]
        for i in range(len(cpu_stats)):
            cpu_stats[i][0]=(cpu_stats[i][0]-init_cpu)*60


     # could be Sum,Maximum,Minimum,SampleCount,Average

    network_in = client.get_metric_statistics(
        Period=1 * 60,
        StartTime=datetime.utcnow() - timedelta(seconds=30 * 60),
        EndTime=datetime.utcnow() - timedelta(seconds=0 * 60),
        MetricName='NetworkIn',
        Namespace=namespace,
        Statistics=['Sum'],
        Dimensions=[{'Name': 'InstanceId', 'Value': id}]
    )

    net_in_stats = []

    for point in network_in['Datapoints']:
        hour = point['Timestamp'].hour
        minute = point['Timestamp'].minute
        time = hour + minute/60
        #time=minute
        net_in_stats.append([time,point['Sum']])

    net_in_stats = sorted(net_in_stats, key=itemgetter(0))
    if(net_in_stats[0][0]):
        init_net=net_in_stats[0][0]
        for i in range(len(net_in_stats)):
            net_in_stats[i][0]=(net_in_stats[i][0]-init_net)*60

    EC2_count = awsClient.get_healthy_count(targetgroup,loadbalancer,availabilityzone,datetime.utcnow() - timedelta(seconds=30 * 60),datetime.utcnow() - timedelta(seconds=0 * 60))
    print(EC2_count)




    return render_template("view.html",title="Instance Info",
                           instance=instance,
                           cpu_stats=cpu_stats,
                           net_in_stats=net_in_stats,
                           healthy_workers_states=EC2_count)
