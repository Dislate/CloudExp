from CloudExp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

class users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60))
    email =  db.Column(db.String(100), unique=True, nullable=False)
    privilages = db.Column(db.String(15), nullable=False, default='is_user')

    def __init__(self, name, password, email, privilages):
        self.name = name
        self.password = password
        self.email = email
        self.privilages = privilages

class languages(db.Model):
    __tablename__ = 'languages'
    id_language = db.Column(db.Integer, primary_key=True)
    name_language = db.Column(db.String(40), unique=True)
    description_language = db.Column(db.String(300))
    part_list = db.relationship('parts', backref='languages', passive_deletes=True, lazy='dynamic')
    
    def __init__(self, name_language, description_language):
        self.name_language = name_language
        self.description_language = description_language

class parts(db.Model):
    __tablename__ = 'parts'
    id_part = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id_language', ondelete="CASCADE"))
    name_part = db.Column(db.String(50))
    chapter_list = db.relationship('chapters', backref='parts', passive_deletes=True, lazy='dynamic')

    def __init__(self, language_id, name_part):
        self.language_id = language_id
        self.name_part = name_part

class chapters(db.Model):
    __tablename__ = 'chapters'
    id_chapter = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id_part', ondelete="CASCADE"))
    name_chapter = db.Column(db.String(30))
    text_chapter = db.Column(db.String(2000))
    part = db.relationship('parts', backref='chapters')

    def __init__(self, part_id, name_chapter, text_chapter):
        self.part_id = part_id
        self.name_chapter = name_chapter
        self.text_chapter = text_chapter
    
# class task(db.Model):
#     _id_task = db.Column('id_task', db.Integer, primary_key=True)
#     chapter = db.Column(db.String(30))
#     text_task = db.Column(db.String(200))
#     solution = db.Column(db.String(300))
#     hint = db.Column(db.String(100))