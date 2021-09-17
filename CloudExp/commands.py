import logging
import click
from flask.cli import AppGroup
from CloudExp import db, bcrypt
from CloudExp.models import User

# Init logger
logging.basicConfig(filename='forms_logs.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

start_cli = AppGroup('start', short_help='Need for first start')


@start_cli.command('create_db')
def create_db():
    db.create_all()
    db.session.commit()


@start_cli.command('create_superuser')
@click.argument('name')
@click.argument('password')
@click.argument('email')
def create_superuser(name, password, email):
    superuser = User(name, bcrypt.generate_password_hash(password), email, 'is_admin')
    db.session.add(superuser)
    try:
        db.session.commit()
    except Exception as err:
        logger.exception(err)
        print('A user with such data already exists')

