import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'ece1779-a2-secretkey'
    BUCKET_NAME = 'userimages-ece1779'
    SQLALCHEMY_DATABASE_URI = 'mysql://ece1779database:ece1779database@ece1779database.cpt3hodccygr.us-east-1.rds.amazonaws.com/testtable'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ZONE = 'Canada/Eastern'