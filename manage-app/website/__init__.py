from flask import Flask
from website.config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from website import home
from website import login
from website import error
from website import configure