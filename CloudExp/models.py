from CloudExp import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

class users(db.Model, UserMixin):
    # TODO: исправить именования класса

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

    def __repr__(self):
        return f"users('{self.id}', '{self.name}', '{self.email}', '{self.privilages}')"


class languages(db.Model):

    __tablename__ = 'languages'

    id_language = db.Column(db.Integer, primary_key=True)
    name_language = db.Column(db.String(40), unique=True)
    description_language = db.Column(db.String(1500))
    part_list = db.relationship('parts', backref='languages', passive_deletes=True, lazy='dynamic')
    
    def __init__(self, name_language, description_language):
        self.name_language = name_language
        self.description_language = description_language

    def __repr__(self):
        return f"languages('{self.id_language}', '{self.name_language}', '{self.description_language}')"


class parts(db.Model):
    __tablename__ = 'parts'
    id_part = db.Column(db.Integer, primary_key=True)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id_language', ondelete="CASCADE"))
    name_part = db.Column(db.String(50), nullable=False)
    chapter_list = db.relationship('chapters', backref='parts', passive_deletes=True, lazy='dynamic')

    def __init__(self, language_id, name_part):
        self.language_id = language_id
        self.name_part = name_part

    def __repr__(self):
        return f"parts('{self.id_part}', '{self.language_id}', '{self.name_part}')"


class chapters(db.Model):
    __tablename__ = 'chapters'
    id_chapter = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('parts.id_part', ondelete="CASCADE"))
    name_chapter = db.Column(db.String(50), nullable=False)
    text_chapter = db.Column(db.String(5000))
    task_list = db.relationship('tasks', backref='chapter', passive_deletes=True, lazy='dynamic')
    seo = db.relationship('seo', backref='chapter', uselist=False, passive_deletes=True)
    
    def __init__(self, part_id, name_chapter, text_chapter):
        self.part_id = part_id
        self.name_chapter = name_chapter
        self.text_chapter = text_chapter
    
    def __repr__(self):
        return f"chapters('{self.id_chapter}', '{self.part_id}', '{self.name_chapter}', '{self.text_chapter}')"


class tasks(db.Model):
    id_task = db.Column('id_task', db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id_chapter', ondelete='CASCADE'))
    name_task = db.Column(db.String(100))
    text_task = db.Column(db.String(1000))
    solution = db.Column(db.String(1000))
    hint = db.Column(db.String(500))

    def __init__(self, chapter_id, name_task, text_task, solution, hint):
        self.chapter_id = chapter_id
        self.name_task = name_task
        self.text_task = text_task
        self.solution = solution
        self.hint = hint

    def __repr__(self):
        return f"tasks('{self.chapter_id}', '{self.name_task}', '{self.text_task}', '{self.solution}', '{self.hint}')"


class seo(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id_chapter', ondelete='CASCADE'))
    keywords = db.Column(db.String(50))
    description = db.Column(db.String(2000))

    def __init__(self, chapter_id, keywords, description):
        self.chapter_id = chapter_id
        self.keywords = keywords
        self.description = description

    def __repr__(self): 
        return f"seo('{self.chapter_id}', '{self.keywords}', '{self.description}')"
