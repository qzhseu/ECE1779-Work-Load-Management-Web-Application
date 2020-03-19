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

client = aws.AwsClient()
# calculate average cpu utilization of all valid instances within target group
# over the past 2 mins (120s)
def average_cpu_utils():
    valid_instances = client.get_valid_instances()
    l = len(valid_instances)
    if l == 0:
        return -1
    else:
        end = datetime.now(timezone(app.config['ZONE']))
        start = end - timedelta(seconds=120)
        cpu_utils_sum = 0
        for i in range(l):
            response = client.get_cpu_utils(valid_instances[i], start, end)
            response = json.loads(response)
            if response and response[0]:
                cpu_utils_sum += response[0][1]
        return cpu_utils_sum / l

def auto_scaling():
    current_time = datetime.now()
    cpu_utils = average_cpu_utils()
    db.session.commit()
    config = AutoScalingConfig.query.order_by(desc(AutoScalingConfig.timestamp)).first()
    # if there is not valid instance or if auto scaling configuration is not setup, return
    if cpu_utils == -1 or config is None:
        return

    if cpu_utils > config.cpu_grow:
        client.grow_worker_by_ratio(config.ratio_expand)
    elif cpu_utils < config.cpu_shrink:
        client.shrink_worker_by_ratio(config.ratio_shrink)