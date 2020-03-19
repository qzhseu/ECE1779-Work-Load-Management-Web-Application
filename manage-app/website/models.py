from website import db

class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    salt = db.Column(db.String(64))
    def __repr__(self): # how to print User
        return '<User{}:{}>'.format(self.userid,self.username)

class Image(db.Model):
    imageid = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(140))
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))
    def __repr__(self):
        return '<Image{}:{}>'.format(self.imageid, self.path)

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
