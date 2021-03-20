from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from CloudExp.models import users

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Присоединиться')

    def validate_username(self, username):
        user = users.query.filter_by(name=username.data).first()
        if user:
            raise ValidationError('This nickname is used. Please choose a deffererent one.')

    def validate_email(self, email):
        email = users.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('This email is used. Please enter a deffererent one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Присоединиться')