from flask import render_template, url_for, session, redirect, request
from website import app
from website.aws.aws import AwsClient
from website.models import RequestPerMinute
from datetime import datetime, timedelta
from pytz import timezone,utc
import collections
import traceback
import json
import logging

client = AwsClient()

@app.route('/')
@app.route('/home')
def home():
    if 'user' in session:
        user = session['user']
    else:
        user = None
    if user is None:
        return redirect(url_for('login'))
    else:
        try:
            valid_workers=client.get_valid_instances()
            if len(valid_workers)<1:
                client.grow_worker_by_one()
            return render_template('home.html')
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            return render_template('error.html', msg='something goes wrong~')

@app.route('/fetch_workers')
# get all instances in target group including idle instances
def fetch_workers():
    target_instances = client.get_target_instances()
    ret = {'data': target_instances}
    return json.dumps(ret)


@app.route('/fetch_cpu_utils', methods=['GET', 'POST'])
# get CPU utilization for past 2 hours for plotting purposes
def fetch_cpu_utils():
    end_time = datetime.now(timezone(app.config['ZONE']))
    start_time = end_time - timedelta(seconds=7200)
    instances = json.loads(request.data.decode('utf-8'))
    series = []
    for instance in instances:
        series.append({
            "name": instance,
            "data": client.get_cpu_utils(instance, start_time, end_time)
        })
    return json.dumps(series)

@app.route('/number_of_workers')
# get the figure for the number of workers for the past 2 hours
def show_number_of_workers():
    if 'user' in session:
        user = session['user']
    else:
        user = None
    if user is None:
        return redirect(url_for('login'))
    else:
        try:
            return render_template('numberofworkers.html')
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            return render_template('error.html', msg='something goes wrong~')

@app.route('/fetch_number_of_workers',methods=['GET', 'POST'])
# fetch data in json format for number of workers
def fetch_number_of_workers():
    end_time = datetime.now(timezone(app.config['ZONE']))
    start_time = end_time - timedelta(seconds=7200)
    series = []
    series.append({
            "name": "Numberofworkers",
            "data": client.get_healthy_count(start_time, end_time)
        })
    return json.dumps(series)

@app.route('/fetch_requests_rate', methods=['GET', 'POST'])
# fetch data in json format for number of http requests for past 2 hours
def fetch_reqeusts_rate():
    end_time = datetime.now(timezone(app.config['ZONE']))
    start_time = end_time - timedelta(seconds=7200)
    instances = json.loads(request.data.decode('utf-8'))
    series = []
    for instance in instances:
        series.append({
            "name": instance,
            "data": get_requests_per_minute(instance, start_time, end_time)
        })
    return json.dumps(series)

@app.route('/grow_one_worker', methods=['GET', 'POST'])
def grow_one_worker():
    response = client.grow_worker_by_one()
    if int(response) == 200:
        msg = "A new worker was registered"
        flag = True
    elif str(response)=='Worker number exceeds 10.':
        msg = str(response)
        flag = False
    else:
        msg = "Unable to register a new worker"
        flag = False
    return json.dumps({
        'flag': flag,
        'msg': msg
    })

@app.route('/shrink_one_worker', methods=['GET', 'POST'])
def shrink_one_worker():
    flag, msg = client.shrink_worker_by_one()
    return json.dumps({
        'flag': flag,
        'msg': msg
    })

# get http requests record within start_time end_time
def get_requests_per_minute(instance, start_time, end_time):
    datetimes = RequestPerMinute.query.filter(RequestPerMinute.instance_id == instance) \
        .filter(RequestPerMinute.timestamp <= end_time) \
        .filter(RequestPerMinute.timestamp >= start_time) \
        .with_entities(RequestPerMinute.timestamp).all()

    localtime=timezone(app.config['ZONE'])


    timestamps = list(map(lambda x: int(round(datetime.timestamp\
                (localtime.localize(x[0],is_dst=None).astimezone(utc)))), datetimes))

    requests_record = []
    timestamp_counter = collections.Counter(timestamps)

    start_timestamp = int(round(datetime.timestamp(start_time)))
    end_timestamp = int(round(datetime.timestamp(end_time)))


    for i in range(start_timestamp, end_timestamp, 60):
        count = 0
        for j in range(i, i + 60):
            count += timestamp_counter[j]
            #logging.warning('inloop:{}'.format(timestamp_counter[j]))
        requests_record.append([i*1000, count])
        #logging.warning('outloop:{}'.format(count))
    return json.dumps(requests_record)
