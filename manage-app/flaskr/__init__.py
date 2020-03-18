from flask import Flask
from flaskr.config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from flaskr import home
from flaskr import login
from flaskr import error
from flaskr import configure