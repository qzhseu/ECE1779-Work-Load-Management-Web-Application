from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, StringField, PasswordField, BooleanField, SubmitField, validators

class ConfigForm(FlaskForm):
    cpu_grow = FloatField('cpu_grow', [validators.NumberRange(min=0, max=99, message="Integer in (0, 100)")], render_kw={'readonly': ''})
    cpu_shrink = FloatField('cpu_shrink', [validators.NumberRange(min=0, max=99, message="Integer in (0, 100)")], render_kw={'readonly': ''})
    ratio_expand = FloatField('ratio_expand', [validators.NumberRange(min=1, max=10, message="Float in [1, 10]")], render_kw={'readonly': ''})
    ratio_shrink = FloatField('ratio_shrink', [validators.NumberRange(min=0, max=1, message="Float in [0, 1]")], render_kw={'readonly': ''})
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')