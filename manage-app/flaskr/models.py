from flaskr import db

class AutoScalingConfig(db.Model):
    __tablename__ = 'autoscalingconfig'
    ascid = db.Column(db.Integer, primary_key=True)
    cpu_grow = db.Column(db.Float)
    cpu_shrink = db.Column(db.Float)
    ratio_expand = db.Column(db.Float)
    ratio_shrink = db.Column(db.Float)
    timestamp = db.Column(db.DateTime) # A type for datetime.datetime() objects.
    def __repr__(self): # how to print User
        return '<AutoScalingConfig {}>'.format(self.ascid)

class RequestPerMinute(db.Model):
    __tablename__ = 'requestperminute'
    requestid = db.Column(db.Integer, primary_key=True)
    instance_id = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)  # A type for datetime.datetime() objects.

    def __repr__(self):
        return '<RequestPerMinute {}>'.format(self.instance_id)

class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    salt = db.Column(db.String(64))

    def __repr__(self): # how to print User
        return '<User {}>'.format(self.username)

    def serialize(self):
        return {
            'userid': self.userid,
            'username': self.username,
        }

class Image(db.Model):
    imageid = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(140))
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'))

    def __repr__(self):
        return '<Post {}>'.format(self.path)
