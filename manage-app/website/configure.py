from flask import render_template, url_for, session, redirect, request, flash
from website import app
from website import db
from website.models import AutoScalingConfig, RequestPerMinute, User, Photo
from website import forms
from datetime import datetime
import traceback
import json
from sqlalchemy import desc
from website.aws.aws import AwsClient
import logging

client = AwsClient()
#configuration for auto scaler
@app.route('/configure')
def configure():
    if 'user' in session:
        user = session['user']
    else:
        user = None
    if user is None:
        return redirect(url_for('login'))
    else:
        try:
            form = forms.ConfigForm()
            values = AutoScalingConfig.query.order_by(desc(AutoScalingConfig.timestamp)).first()
            if values is None:
                values = {
                    'cpu_grow': -1,
                    'cpu_shrink': -1,
                    'ratio_expand': -1,
                    'ratio_shrink': -1
                }
            return render_template('configure.html', form=form, values=values)
        except Exception as e:
            traceback.print_tb(e.__traceback__)
            return render_template('error.html', msg='something goes wrong~')


@app.route('/configure_auto_scaling', methods=['GET', 'POST'])
def configure_auto_scaling():
    if 'user' in session:
        user = session['user']
    else:
        user = None
    if user is None:
        return redirect(url_for('login'))
    else:
        try:
            form = forms.ConfigForm()
            if form.validate_on_submit():
                cpu_grow = form.cpu_grow.data
                cpu_shrink = form.cpu_shrink.data
                ratio_expand = form.ratio_expand.data
                ratio_shrink = form.ratio_shrink.data
                # check input
                if cpu_grow > cpu_shrink:
                    # add into database
                    value = AutoScalingConfig(cpu_grow=cpu_grow, cpu_shrink=cpu_shrink,
                                              ratio_expand=ratio_expand, ratio_shrink=ratio_shrink,
                                              timestamp=datetime.now())
                    db.session.add(value)
                    db.session.commit()
                    flash("Configuration has been updated!", "success")
                else:
                    flash("cpu_grow should not lower than cpu_shrink", "error")

            else:
                if form.cpu_grow.errors:
                    flash("cpu_grow: " + ", ".join(form.cpu_grow.errors), "error")
                elif form.cpu_shrink.errors:
                    flash("cpu_shrink: " + ", ".join(form.cpu_shrink.errors), "error")
                elif form.ratio_expand.errors:
                    flash("ratio_expand: " + ", ".join(form.ratio_expand.errors), "error")
                elif form.ratio_shrink.errors:
                    flash("ratio_shrink: " + ", ".join(form.ratio_shrink.errors), "error")
                else: pass

            return redirect(url_for('configure'))

        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)
            return render_template('error.html', msg='something goes wrong~')

@app.route('/stop_manager_terminate_intances',methods=['GET','POST'])
def stop_manager_terminate_intances():
    current_time = datetime.now()
    if 'user' in session:
        user = session['user']
    else:
        user = None
    if user is None:
        return redirect(url_for('login'))
    else:
        try:
            response=client.stop_all_instances()
            logging.warning('{} terminate all workers: {}'.format(current_time, response))
            return json.dumps({
                'flag': True,
                'msg': 'Success'
            })
        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)
            return json.dumps({
            'flag': False,
            'msg': 'Fail to stop instances'
            })

@app.route('/clear_data', methods=['GET', 'POST'])
def clear_data():
    if 'user' in session:
        user = session['user']
    else:
        user = None
    if user is None:
        return redirect(url_for('login'))
    else:
        try:
            AutoScalingConfig.query.delete()
            db.session.commit()
            RequestPerMinute.query.delete()
            db.session.commit()
            User.query.delete()
            db.session.commit()
            Photo.query.delete()
            db.session.commit()
            client.clear_s3()
            return json.dumps({
                'flag': True,
                'msg': 'Success'
            })
        except Exception as e:
            print(e)
            traceback.print_tb(e.__traceback__)
            return json.dumps({
                'flag': False,
                'msg': 'Fail to clear the data'
            })