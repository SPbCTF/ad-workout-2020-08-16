from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, SubmitField, PasswordField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Length, Email

class SignUpForm(FlaskForm):
    firstname= TextField('First Name', validators=[InputRequired("Please enter your name."), Length(max=100, message=('Your firstname is not in 1-100.'))])
    lastname = TextField('Last Name', validators=[InputRequired("Please enter your name."), Length(max=100, message=('Your lastname is not in 1-100.'))])
    username = TextField('User Name', validators=[InputRequired("Please enter your name."), Length(min=4,max=100, message=('Your nickname is not in 4-100.'))])
    password = PasswordField('Password',validators=[InputRequired("Please enter your name."), Length(min=8,max=100, message=('Your password is not in 8-100.'))])
    email = EmailField('Email', validators=[InputRequired("Please enter your name."), Length(max=100, message=('Your email is not in 1-100.'))])
    submit = SubmitField('Sign Up')

class SignInForm(FlaskForm):
    username = TextField('Username', validators=[InputRequired("Please enter your name.")])
    password = PasswordField('Password', validators=[InputRequired("Please enter your name.")])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign In')
