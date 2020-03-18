#!/bin/bash
manage_app_dir='manage-app'
auto_scaling_dir='flaskr/aws'

source $manage_app_dir/myvenv/bin/activate
cd $manage_app_dir && python run.py &> manage_app.log &

if [ $? == 0 ]
then
        echo "manage_app start success"
else
        echo "manage_app start fail"
fi

cd $manage_app_dir/$auto_scaling_dir && python auto_scaling.py &> auto_scaling.log &

if [ $? == 0 ]
then
        echo "auto_scaling start success"
else
        echo "auto_scaling start fail"
fi
 
