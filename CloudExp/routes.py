from flask import redirect, url_for, render_template, request, flash, send_from_directory, Response
from CloudExp import app, db, bcrypt
from CloudExp.models import User, Language, Part, Chapter, Task, Seo
from CloudExp.forms import RegistrationForm, LoginForm, AddingLanguage, AddingPart, AddingChapter
from flask_login import login_user, current_user, logout_user

from CloudExp.helper import get_task


@app.context_processor
def inject_languages():
    return dict(languages_list=Language.query.all())


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/agreement')
def agreement():
    return render_template("agreement.html")


@app.route('/admin-panel', methods=['POST'])
def admin_panel_post():
    if request.method == 'POST':
        try:
            keywords = request.form['keywords_chapter']
            description = request.form['description_chapter']
        except:
            pass
        else:
            if request.args.get('data_input_chapter'):
                chapter = Chapter.query.filter_by(id_chapter=request.args.get('data_input_chapter')).first()
            else:
                chapter = Chapter.query.first()

            chapter.seo.keywords = keywords
            chapter.seo.description = description
            db.session.commit()
            return redirect(url_for('admin_panel_post', data_input_chapter=chapter.id_chapter))

        text_chapter = request.form['text_chapter']
        request_chapter = request.args.get('data_input_chapter')
        if request_chapter:
            current_chapter = Chapter.query.filter_by(id_chapter=request_chapter).first()
        else:
            current_chapter = Chapter.query.first()
        current_chapter.text_chapter = text_chapter
        for index, task in enumerate(current_chapter.task_list):
            task.name_task = request.form['name_task_' + str(index + 1)]
            task.text_task = request.form['text_task_' + str(index + 1)]
            task.solution = request.form['solution_task_' + str(index + 1)]
            task.hint = request.form['hint_task_' + str(index + 1)]
        db.session.commit()
        return redirect(url_for('admin_panel_post', data_input_chapter=request_chapter))
    return Response(status=404)


@app.route('/admin-panel', methods=['GET'])
def admin_panel():

    if request.args.get('delete_task'):

        index_delete_task = request.args.get('delete_task', type=int)
        idChapter = request.args.get('current_chapter')
        currentTask = Chapter.query.filter_by(id_chapter=idChapter).first().task_list[index_delete_task - 1]

        db.session.delete(currentTask)
        db.session.commit()
        return redirect(url_for('admin_panel', data_input_chapter=idChapter))

    if request.args.get('adding_task'):

        chapterForTask = request.args.get('adding_task')
        newTask = Task(int(chapterForTask), '', '', '', '')

        db.session.add(newTask)
        db.session.commit()
        return redirect(url_for('admin_panel', data_input_chapter=chapterForTask))

    if current_user.is_authenticated:
        if current_user.privilages == 'is_admin':
            if Language.query.first() and Part.query.first() and Chapter.query.first():
                data = request.args.get('data_input_chapter')
                if data:
                    obj_chapter = Chapter.query.filter_by(id_chapter=data).first()
                else:
                    obj_chapter = Language.query.first().part_list.first().chapter_list.first()
                
                if not obj_chapter.seo:
                    add_seo_chapter = Seo(obj_chapter.id_chapter, '', '')
                    db.session.add(add_seo_chapter)
                    db.session.commit()
                
                return render_template('admin-panel.html', langs=Language.query.all(),
                                       obj_chapter=obj_chapter, name_page='Админ-панель')
            else:
                return render_template('admin-panel.html', langs=Language.query.all(),
                                       obj_chapter='', name_page='Админ-панель')
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('signin'))


@app.route('/adding-language', methods=['GET', 'POST'])
def adding_language():
    if current_user.is_authenticated and current_user.privilages == 'is_admin':
        adding_language = AddingLanguage()

        if adding_language.validate_on_submit():

            new_language = Language(adding_language.name_language.data, adding_language.description_language.data)

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

            new_part = Part(Language.query.filter_by(
                name_language=adding_part.name_language.data).first().id_language, adding_part.name_part.data)

            db.session.add(new_part)
            db.session.commit()

            return redirect(url_for('admin_panel'))
        
        return render_template('adding-part.html', form=adding_part, language=request.args.get('language'))
    else:
        return Response(status=401)


@app.route('/adding-chapter', methods=['GET', 'POST'])
def adding_chapter():
    if current_user.is_authenticated and current_user.privilages == 'is_admin':

        adding_chapter = AddingChapter()
        if adding_chapter.validate_on_submit():
            new_chapter = Chapter(Part.query.filter_by(
                name_part=adding_chapter.name_part.data).first().id_part,
                                   adding_chapter.name_chapter.data,
                                   adding_chapter.text_chapter.data)
            db.session.add(new_chapter)
            db.session.commit()
            return redirect(url_for('admin_panel'))
        
        return render_template('adding-chapter.html',
                               form=adding_chapter,
                               part=request.args.get('part'))
    else:
        return Response(status=401)


@app.route('/languages/<language>', methods=['POST', 'GET'])
def getLanguage(language):
    current_language = Language.query.filter_by(name_language=language).first()
    if current_language:
        return render_template('language.html',
                               current_language=current_language,
                               name_page=current_language.name_language)
    else:
        return redirect(url_for('home'))


@app.route('/<language>/<number_part>/<number_chapter>', methods=['GET'])
def getPart(language, number_part, number_chapter):
    current_language = Language.query.filter_by(name_language=language).first()
    number_part = current_language.part_list[int(number_part) - 1]
    number_chapter = number_part.chapter_list[int(number_chapter) - 1]

    name_page = f"{current_language.name_language} - {number_chapter.name_chapter}"

    if current_language and number_part:
        return render_template('part.html',
                               current_language=current_language,
                               number_part=number_part,
                               chapter=number_chapter,
                               name_page=name_page,
                               task_list=get_task(number_chapter))
    else:
        return redirect(url_for('home'))


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
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

        user = User(form.username.data,
                     bcrypt.generate_password_hash(form.password.data),
                     form.email.data,
                     'is_user')

        db.session.add(user)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("signup.html", form=form, name_page='Регистрация')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))