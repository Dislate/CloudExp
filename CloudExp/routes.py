from flask import redirect, url_for, render_template, request, session, flash, send_from_directory
from CloudExp import app, db, bcrypt
from CloudExp.models import users, languages, parts, chapters, tasks, seo 
from CloudExp.forms import RegistrationForm, LoginForm, AddingLanguage, AddingPart, AddingChapter
from flask_login import login_user, current_user, logout_user


@app.context_processor
def inject_languages():
    return dict(languages_list=languages.query.all())

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/agreement')
def agreement():
    return render_template("agreement.html")

@app.route('/admin-panel', methods=['GET', 'POST'])
def admin_panel():
    if request.method == 'POST':
        
        try: 
            keywords = request.form['keywords_chapter']
            description = request.form['description_chapter']
        except:
            pass
        else:
            if request.args.get('data_input_chapter'):
                chapter = chapters.query.filter_by(id_chapter=request.args.get('data_input_chapter')).first()
            else:
                chapter = chapters.query.first()
            
            chapter.seo.keywords = keywords
            chapter.seo.description = description
            db.session.commit()
            return redirect(url_for('admin_panel', data_input_chapter=chapter.id_chapter))

        text_chapter = request.form['text_chapter']
        request_chapter = request.args.get('data_input_chapter')
        if request_chapter:
            current_chapter = chapters.query.filter_by(id_chapter=request_chapter).first()
        else:
            current_chapter = chapters.query.first()
        current_chapter.text_chapter = text_chapter
        for index, task in enumerate(current_chapter.task_list):
            task.name_task = request.form['name_task_' + str(index+1)]
            task.text_task = request.form['text_task_' + str(index+1)]
            task.solution = request.form['solution_task_' + str(index+1)]
            task.hint = request.form['hint_task_' + str(index+1)]
        db.session.commit()
        return redirect(url_for('admin_panel', data_input_chapter=request_chapter))

    if request.args.get('delete_task'):
        indexDeleteTask = request.args.get('delete_task', type=int)
        idChapter=request.args.get('current_chapter')
        currentTask = chapters.query.filter_by(id_chapter=idChapter).first().task_list[indexDeleteTask - 1]
        db.session.delete(currentTask)
        db.session.commit()
        return redirect(url_for('admin_panel', data_input_chapter=idChapter))

    if request.args.get('adding_task'):
        chapterForTask = request.args.get('adding_task')
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
                
                if not obj_chapter.seo:
                    add_seo_chapter = seo(obj_chapter.id_chapter, '', '')
                    db.session.add(add_seo_chapter)
                    db.session.commit()
                
                return render_template('admin-panel.html', langs=languages.query.all(), obj_chapter=obj_chapter, name_page='Админ-панель')
            else:
                return render_template('admin-panel.html', langs=languages.query.all(), obj_chapter='', name_page='Админ-панель')
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('signin'))

@app.route('/adding-language', methods=['GET', 'POST'])
def adding_language():
    if current_user.is_authenticated and current_user.privilages == 'is_admin':

        adding_language = AddingLanguage()

        if adding_language.validate_on_submit():
            new_language = languages(adding_language.name_language.data, adding_language.description_language.data)
            db.session.add(new_language)
            db.session.commit()
            return redirect(url_for('admin_panel'))

        return render_template('adding-language.html', form=adding_language)
    else:
        return 'Access dinied'

@app.route('/adding-part', methods=['GET', 'POST'])
def adding_part():
    if current_user.is_authenticated and current_user.privilages == 'is_admin':

        adding_part = AddingPart()

        if adding_part.validate_on_submit():
            new_part = parts(languages.query.filter_by(name_language=adding_part.name_language.data).first().id_language, adding_part.name_part.data)
            db.session.add(new_part)
            db.session.commit()
            return redirect(url_for('admin_panel'))
        
        return render_template('adding-part.html', form=adding_part, language=request.args.get('language'))
    else:
        return 'Access denied'

@app.route('/adding-chapter', methods=['GET', 'POST'])
def adding_chapter():
    if current_user.is_authenticated and current_user.privilages == 'is_admin':

        adding_chapter = AddingChapter()
        if adding_chapter.validate_on_submit():
            new_chapter = chapters(parts.query.filter_by(name_part=adding_chapter.name_part.data).first().id_part, adding_chapter.name_chapter.data, adding_chapter.text_chapter.data)
            db.session.add(new_chapter)
            db.session.commit()
            return redirect(url_for('admin_panel'))
        
        return render_template('adding-chapter.html', form=adding_chapter, part=request.args.get('part'))
    else:
        return 'Access denied'


@app.route('/languages/<language>', methods=['POST', 'GET'])
def getLanguage(language):
    current_language = languages.query.filter_by(name_language=language).first()
    if current_language:
        return render_template('language.html', current_language=current_language, name_page=current_language.name_language)
    else:
        return redirect(url_for('home'))

@app.route('/<language>/<number_part>/<number_chapter>', methods=['GET'])
def getPart(language, number_part, number_chapter):
    current_language = languages.query.filter_by(name_language=language).first()
    number_part = current_language.part_list[int(number_part) - 1]
    number_chapter = number_part.chapter_list[int(number_chapter) - 1]

    def get_task(chapter):
        task_list = number_chapter.task_list
        try:
            task_list[0]
        except:
            return ''
        else:
            return task_list

    if current_language and number_part:
        return render_template('part.html', current_language=current_language, number_part=number_part, chapter=number_chapter, name_page=current_language.name_language + ' - ' + number_chapter.name_chapter, task_list=get_task(number_chapter))
    else:
        return redirect(url_for('home'))

@app.route('/signin', methods=['POST','GET'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = users.query.filter_by(name=form.username.data).first()
        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("home"))
        flash('Пароль не верный')
    return render_template('signin.html', form=form, name_page='Вход')


@app.route('/signup', methods=["POST", "GET"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = users(form.username.data, bcrypt.generate_password_hash(form.password.data), form.email.data, 'is_user')
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("signup.html", form=form, name_page='Регистрация')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))