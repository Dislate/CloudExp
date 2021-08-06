import logging
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from CloudExp.models import User, Language, Part


logging.basicConfig(filename='forms_logs.log', level=logging.DEBUG)
logger_forms = logging.getLogger(__name__)


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Присоединиться')

    def validate_username(self, username):
        user = User.query.filter_by(name=username.data).first()
        if user:
            logger_forms.info("Name is taken")
            raise ValidationError('Это имя занято')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            logger_forms.info("Email is taken")
            raise ValidationError('Эта почта уже используется')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Вход')

    def validate_username(self, username):
        user = User.query.filter_by(name=username.data).first()
        if not user:
            logger_forms.info("Name is not found")
            raise ValidationError('Пользователь не найден')


class AddingLanguage(FlaskForm):
    name_language = StringField('Название языка', validators=[DataRequired(), Length(min=2, max=40)])
    description_language = TextAreaField('Описание языка', validators=[DataRequired(), Length(min=10, max=1500)])
    submit = SubmitField('Добавить')

    def validate_name_language(self, name_language):
        if Language.query.filter_by(name_language=name_language.data).first():
            logger_forms.info("This language already exists")
            raise ValidationError('Такой язык уже есть')


class AddingPart(FlaskForm):
    name_language = StringField('Название части')
    name_part = StringField('Название части', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Добавить')


class AddingChapter(FlaskForm):
    name_part = StringField('Название части', validators=[DataRequired()])
    name_chapter = StringField('Название главы', validators=[DataRequired(), Length(min=3, max=50)])
    text_chapter = TextAreaField('Текст главы', validators=[Length(min=0, max=5000)])
    submit = SubmitField('Добавить')

    def validate_name_part(self, name_part):
        current_part = Part.query.filter_by(name_part=name_part.data).first()
        try:
            current_part.name_chapter
        except AttributeError as err:
            logger_forms.exception(err)
            raise ValidationError('Такой части не существует')
