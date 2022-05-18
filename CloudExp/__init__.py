from datetime import timedelta
from sqlalchemy import MetaData
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_login import LoginManager

from CloudExp.config import Config

# Custom naming convention for alembic-sqlalchemy
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# Init app and set сonfiguration
app = Flask(__name__)
app.config.from_object(Config)
app.permanent_session_lifetime = timedelta(days=1)

# Init db and declaration custom metadata
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)

# Init migrate сonfiguration
migrate = Migrate(app, db)
manager = Manager(app)

# Init authorization сonfiguration
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

manager.add_command('db', MigrateCommand, render_as_batch=True)

# importing after declaration app
from CloudExp import routes
