from wtforms import Form, StringField, TextAreaField, PasswordField, validators, BooleanField, ValidationError
from flask_wtf import FlaskForm


class LoginForm(FlaskForm):
    username = StringField('Username', [
        validators.DataRequired(message="Plese input your username"),
        validators.Length(min=1, max=25),
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.Length(min=6, max=255),
    ])

