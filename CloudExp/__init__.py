
from os.path import dirname
from datetime import timedelta
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager

from CloudExp import routes

from CloudExp.config import Config


projectDir = dirname(__file__)

app = Flask(__name__)
app.config.from_object(Config)
app.permanent_session_lifetime = timedelta(days=1)

db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

manager.add_command('db', MigrateCommand, render_as_batch=True)
