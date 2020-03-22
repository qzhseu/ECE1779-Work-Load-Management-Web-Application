import sys
sys.path.append('../../')
import schedule
import time
from datetime import datetime, timedelta
from pytz import timezone
from website import app
from website import db
from website.models import AutoScalingConfig, RequestPerMinute
from sqlalchemy import desc
import aws
import json
import logging

awscli = aws.AwsClient()

# get start_time and end_time of latest 1 minute
def get_time_span(latest):
    end_time = datetime.now(timezone(app.config['ZONE']))
    start_time = end_time - timedelta(seconds=latest)
    return start_time, end_time

def average_cpu_utils():
    valid_instances_id = awscli.get_valid_instances()
    l = len(valid_instances_id)
    logging.warning('valid_instances_id:{}'.format(valid_instances_id))
    start_time, end_time = get_time_span(60)
    logging.warning('start:{}'.format(start_time))
    logging.warning('start:{}'.format(end_time))
    cpu_sum = 0
    for i in range(l):
        response = awscli.get_cpu_utils(valid_instances_id[i], start_time, end_time)
        logging.warning(response)
        response = json.loads(response)
        if response and response[0]:
            cpu_sum += response[0][1]

    return cpu_sum / l if l else -1


def auto_scaling():
    logging.warning('-----------auto_scaling------------')
    current_time = datetime.now()
    cpu_utils = average_cpu_utils()
    db.session.commit()
    config = AutoScalingConfig.query.order_by(desc(AutoScalingConfig.timestamp)).first()
    logging.warning(cpu_utils)

    # if there is no valid instances, then do nothing.
    if cpu_utils == -1:
        logging.warning('{} no workers in the pool'.format(current_time))
        return

    if not config:
        logging.warning('{} no auto scaling configuration'.format(current_time))
        return

    #cpu_grow, cpu_shrink, ratio_expand, ratio_shrink
    if cpu_utils > config.cpu_grow:
        response = awscli.grow_worker_by_ratio(config.ratio_expand)
        logging.warning('{} grow workers: {}'.format(current_time, response))
        #time.sleep(60)
    elif cpu_utils < config.cpu_shrink:
        response = awscli.shrink_worker_by_ratio(config.ratio_shrink)
        logging.warning('{} shrink workers: {}'.format(current_time, response))
        #time.sleep(60)
    else:
        logging.warning('{} nothing change'.format(current_time))


def clear_requests():
    # clear the records 2 hours ago
    start_time, end_time = get_time_span(7260)
    RequestPerMinute.query.filter(RequestPerMinute.timestamp < start_time).delete()
    db.session.commit()
    logging.warning('{} delete records two hours go'.format(end_time))


if __name__ == '__main__':
    # start auto-scaling
    schedule.every(60).seconds.do(auto_scaling)
    schedule.every(60).minutes.do(clear_requests)
    while True:
        schedule.run_pending()
        time.sleep(1)
