from flask import Flask
import os

app=Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

from managerapp import routes