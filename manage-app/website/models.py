from website import db

class User(db.Model):
    __tablename__ = 'testtable'
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100), primary_key=True, unique=True)
    password = db.Column(db.String(300))
    def __repr__(self): # how to print User
        return '<User:{}>'.format(self.username)

class Photo(db.Model):
    __tablename__ = 'photos'
    usrname = db.Column(db.String(100))
    photourl = db.Column(db.String(300), primary_key=True)
    def __repr__(self):
        return '<Image{}:{}>'.format(self.username, self.photourl)

class AutoScalingConfig(db.Model):
    __tablename__ = 'autoscalingconfig'
    ascid = db.Column(db.Integer, primary_key=True)
    cpu_grow = db.Column(db.Float)
    cpu_shrink = db.Column(db.Float)
    ratio_expand = db.Column(db.Float)
    ratio_shrink = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)
    def __repr__(self):
        return '<AutoScalingConfig {}>'.format(self.ascid)

class RequestPerMinute(db.Model):
    __tablename__ = 'requestperminute'
    requestid = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)
    def __repr__(self):
        return '<RequestPerMinute {}>'.format(self.instance_id)
