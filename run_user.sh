#!/bin/bash
user_app_dir='user-app'

cd $user_app_dir && myvenv/bin/python run.py &> user_app.log &

if [ $? == 0 ]
then
        echo "user_app start success"
else
        echo "user_app start fail"
fi
