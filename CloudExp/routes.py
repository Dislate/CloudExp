from flask import redirect, url_for, render_template, request, session, flash
from CloudExp import app, db, bcrypt
from CloudExp.models import users, languages, parts, chapters, tasks
from CloudExp.forms import RegistrationForm, LoginForm
from flask_login import login_user, current_user, logout_user


@app.context_processor
def inject_languages():
    return dict(languages_list=languages.query.all())

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/admin-panel', methods=['GET', 'POST', 'PUT'])
def admin_panel():
    if request.method == 'POST':
        
        try:
            requestLang = request.form['name_language']
        except:
            pass
        else:
            newLang = languages(requestLang, 'lorem')
            db.session.add(newLang)
            db.session.commit()
            return redirect(url_for('admin_panel'))

        try:
            requestPart = request.form['name_part']
        except:
            pass
        else:
            newPart = parts(request.args.get('data-id-lang'), request.form['name_part'])
            db.session.add(newPart)
            db.session.commit()
            return redirect(url_for('admin_panel'))

        try:
            requestChapter = request.form['name_chapter']
        except:
            pass
        else:
            newChapter = chapters(request.args.get('data-id-part'), request.form['name_chapter'], 'Enter text here, bro')
            db.session.add(newChapter)
            db.session.commit()
            return redirect(url_for('admin_panel'))

        try:
            text_chapter = request.form['text_chapter']
        except:
            pass
        else:
            request_chapter = request.args.get('data_input_chapter')
            if request_chapter:
                chapters.query.filter_by(id_chapter=request_chapter).update({"text_chapter": text_chapter})
            else:
                chapters.query.first().text_chapter = text_chapter
            db.session.commit()
            return redirect(url_for('admin_panel', data_input_chapter=request_chapter))
    
    if request.args.get('data-task-chapter'):
        chapterForTask = request.args.get('data-task-chapter')
        newTask = tasks(int(chapterForTask), '', '', '', '')
        db.session.add(newTask)
        db.session.commit()
        return redirect(url_for('admin_panel', data_input_chapter=chapterForTask))

    if current_user.is_authenticated:
        if current_user.privilages == 'is_admin':
            if languages.query.first() and parts.query.first() and chapters.query.first():
                data = request.args.get('data_input_chapter')
                if data:
                    obj_chapter = chapters.query.filter_by(id_chapter=data).first()
                else:
                    obj_chapter = languages.query.first().part_list.first().chapter_list.first()
                return render_template('admin-panel.html', langs=languages.query.all(), obj_chapter=obj_chapter, name_page='Админ-панель')
            else:
                return render_template('admin-panel.html', langs=languages.query.all(), obj_chapter='', name_page='Админ-панель')
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('signin'))


@app.route('/languages/<language>', methods=['POST', 'GET'])
def getLanguage(language):
    obj_language = languages.query.filter_by(name_language=language).first()
    if obj_language:
        return render_template('language.html', lang=obj_language, name_page=obj_language.name_language)
    else:
        return redirect(url_for('home'))

@app.route('/<language>/<name_part>/<number_chapter>', methods=['POST', 'GET'])
def getPart(language, name_part, number_chapter):
    obj_lang = languages.query.filter_by(name_language=language).first()
    obj_part = obj_lang.part_list.filter_by(name_part=name_part).first()
    number_chapter = obj_part.chapter_list[int(number_chapter) - 1]
    if request.method == 'POST':
        text_chapter = request.form['update_chapter']
        chapters.query.filter_by(id_chapter=1).update({'text_chapter': text_chapter})
        db.session.commit()

    if obj_lang and name_part:
        return render_template('part.html', lang=obj_lang, part=obj_part, chapter=number_chapter, name_page=obj_lang.name_language + ' - ' + number_chapter.name_chapter)
    else:
        return redirect(url_for('home'))

@app.route('/signin', methods=['POST','GET'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = users.query.filter_by(name=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Данные не верны")
            return redirect(url_for("signin"))

    return render_template('signin.html', form=form, name_page='Вход')


@app.route('/signup', methods=["POST", "GET"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        if users.query.filter_by(name=form.username.data).first() and users.query.filter_by(email=form.email.data).first():
            return redirect(url_for("signup"))
        else:
            user = users(form.username.data, bcrypt.generate_password_hash(form.password.data), form.email.data, 'is_user')
            db.session.add(user)
            db.session.commit()
        return redirect(url_for("home"))
    return render_template("signup.html", form=form, name_page='Регистрация')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))