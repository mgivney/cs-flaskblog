from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flaskblog.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Username', 
            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
            validators=[DataRequired(), Email()]) 
    password = PasswordField('Password', 
            validators=[DataRequired()])
    pwd_conf = PasswordField('Confirm Password', 
            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():        
           raise ValidationError('Username already exists.')     

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():        
           raise ValidationError(f'User already exists with email {self.email.data}.')     



class LoginForm(FlaskForm):
    email = StringField('Email', 
            validators=[DataRequired(), Email()]) 
    password = PasswordField('Password', 
            validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')    


class AccountForm(FlaskForm):
    username = StringField('Username', 
            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
            validators=[DataRequired(), Email()]) 
    picture = FileField('Update Avatar',
            validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')
        
    def validate_username(self, username):
        if username.data != current_user.username:
                if User.query.filter_by(username=username.data).first():        
                        raise ValidationError('Username already exists.')     

    def validate_email(self, email):
        if email.data != current_user.email:
                if User.query.filter_by(email=email.data).first():        
                        raise ValidationError(f'User already exists with email {self.email.data}.')     


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first() is None:
           raise ValidationError(
               f'There is no account with the email: {self.email.data}. Please register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
            validators=[DataRequired()])
    pwd_conf = PasswordField('Confirm Password', 
            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
