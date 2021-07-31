import logging
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from CloudExp.models import users, languages, parts


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Присоединиться')

    def validate_username(self, username):
        user = users.query.filter_by(name=username.data).first()
        if user:
            raise ValidationError('Это имя занято')

    def validate_email(self, email):
        email = users.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Эта почта уже используется')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Вход')

    def validate_username(self, username):
        user = users.query.filter_by(name=username.data).first()
        if not user:
            raise ValidationError('Пользователь не найден')


class AddingLanguage(FlaskForm):
    name_language = StringField('Название языка', validators=[DataRequired(), Length(min=2, max=40)])
    description_language = TextAreaField('Описание языка', validators=[DataRequired(), Length(min=10, max=1500)])
    submit = SubmitField('Добавить')

    def validate_name_language(self, name_language):
        if languages.query.filter_by(name_language=name_language.data).first():
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
        current_part = parts.query.filter_by(name_part=name_part.data).first()
        try:
            current_part.name_chapter
        except Exception as err:
            logger.exception(err)
            raise ValidationError('Такой части не существует')
