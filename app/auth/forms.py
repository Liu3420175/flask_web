"""
用户登陆，注册表单
"""
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

from app.models import OwnUser


class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username',
                           validators=[Required(), Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                         'Usernames must have only letters,'
                                                                         'numbers,dots or underscores')])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    @staticmethod
    def validate_email(field):
        if OwnUser.query.filter_by(contact_email=field.data).first():
            raise ValidationError('Email already registered.')

    @staticmethod
    def validate_username(field):
        if OwnUser.query.filter_by(user_name=field.data).first():
            raise ValidationError('Username already in use.')


class LoginForm(Form):
    username = StringField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in', default=True)
    submit = SubmitField('Log In')

