import logging
from flask import redirect, url_for, render_template, request, flash, send_from_directory, Response
from flask_login import login_user, current_user, logout_user
from CloudExp import app, db, bcrypt
from CloudExp.models import User, Language, Part, Chapter, Task, Seo
from CloudExp.forms import RegistrationForm, LoginForm, AddingLanguage, AddingPart, AddingChapter
from CloudExp.helper import save_in_db
from CloudExp.decorators import login_required

logging.basicConfig(filename='forms_logs.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.context_processor
def inject_languages():
    try:
        return dict(languages_list=Language.query.all())
    except Exception as err:
        logger.exception(err)
        return Response(status=500)


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
@login_required
def admin_panel_post():
    if request.method == 'POST':
        # TODO сделать форму для seo
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

        # TODO сделать формы для главы и задач
        text_chapter = request.form['text_chapter']
        request_chapter = request.args.get('data_input_chapter')
        if request_chapter:
            current_chapter = Chapter.query.filter_by(id_chapter=request_chapter).first()
        else:
            current_chapter = Chapter.query.first()
        current_chapter.text_chapter = text_chapter
        # rewriting task fields
        for index, task in enumerate(current_chapter.task_list):
            task.name_task = request.form['name_task_' + str(index + 1)]
            task.text_task = request.form['text_task_' + str(index + 1)]
            task.solution = request.form['solution_task_' + str(index + 1)]
            task.hint = request.form['hint_task_' + str(index + 1)]
        db.session.commit()
        return redirect(url_for('admin_panel_post', data_input_chapter=request_chapter))
    return Response(status=404)


@app.route('/admin-panel', methods=['GET'])
@login_required
def admin_panel():
    if current_user.privilages == 'is_admin':
        if Chapter.query.first():
            current_chapter = Language.query.first().part_list.first().chapter_list.first()
            data = request.args.get('data_input_chapter')
            if data:
                current_chapter = Chapter.query.filter_by(id_chapter=data).first()

            if not current_chapter.seo:
                add_seo_for_chapter = Seo(current_chapter.id_chapter, None, None)
                save_in_db(add_seo_for_chapter, redirect_to_page=False)

            return render_template('admin-panel.html', langs=Language.query.all(),
                                   current_chapter=current_chapter, name_page='Админ-панель')
        else:
            return render_template('admin-panel.html', langs=Language.query.all(),
                                   current_chapter=None, name_page='Админ-панель')
    else:
        return Response(status=403)


@app.route('/admin-panel/delete-task', methods=['GET'])
@login_required
def delete_task():
    # reading args
    id_chapter = request.args.get('current_chapter')
    index_del_task = request.args.get('delete_task', type=int)
    # find task
    current_task = Chapter.query.filter_by(id_chapter=id_chapter).first().task_list[index_del_task - 1]
    return save_in_db(current_task, 'admin_panel', delete=True, data_input_chapter=id_chapter)


@app.route('/admin-panel/adding-task', methods=['GET'])
@login_required
def adding_task():
    id_chapter = request.args.get('current_chapter')
    new_task = Task(int(id_chapter), '', '', '', '')
    return save_in_db(new_task, 'admin_panel', data_input_chapter=id_chapter)


@app.route('/adding-language', methods=['GET', 'POST'])
def adding_language():
    if current_user.is_authenticated and current_user.privilages == 'is_admin':
        add_lang_form = AddingLanguage()

        if add_lang_form.validate_on_submit():
            new_language = Language(add_lang_form.name_language.data, add_lang_form.description_language.data)
            return save_in_db(new_language, 'admin-panel')
        return render_template('adding-language.html', form=add_lang_form)
    else:
        return Response(status=401)


@app.route('/adding-part', methods=['GET', 'POST'])
def adding_part():
    if current_user.is_authenticated and current_user.privilages == 'is_admin':

        add_part_form = AddingPart()

        if add_part_form.validate_on_submit():
            new_part = Part(Language.query.filter_by(
                name_language=add_part_form.name_language.data).first().id_language, add_part_form.name_part.data)
            return save_in_db(new_part, 'admin-panel')
        return render_template('adding-part.html', form=add_part_form, language=request.args.get('language'))
    else:
        return Response(status=401)


@app.route('/adding-chapter', methods=['GET', 'POST'])
def adding_chapter():
    if current_user.is_authenticated and current_user.privilages == 'is_admin':

        add_chapter_form = AddingChapter()
        if add_chapter_form.validate_on_submit():
            new_chapter = Chapter(Part.query.filter_by(
                name_part=add_chapter_form.name_part.data).first().id_part,
                                  add_chapter_form.name_chapter.data,
                                  add_chapter_form.text_chapter.data)
            return save_in_db(new_chapter, 'admin_panel')
        return render_template('adding-chapter.html',
                               form=add_chapter_form,
                               part=request.args.get('part'))
    else:
        return Response(status=401)


@app.route('/languages/<language>', methods=['POST', 'GET'])
def get_language(language):
    current_language = Language.query.filter_by(name_language=language).first()
    if current_language:
        return render_template('language.html',
                               current_language=current_language,
                               name_page=current_language.name_language)
    else:
        return redirect(url_for('home'))


@app.route('/<language>/<number_part>/<number_chapter>', methods=['GET'])
def get_part(language, number_part, number_chapter):
    current_language = Language.query.filter_by(name_language=language).first()
    number_part = current_language.part_list[int(number_part) - 1]
    number_chapter = number_part.chapter_list[int(number_chapter) - 1]
    name_page = f"{current_language.name_language} - {number_chapter.name_chapter}"

    task_list = None
    if Chapter.task_list[0]:
        task_list = Chapter.task_list

    if current_language and number_part:
        return render_template('part.html',
                               current_language=current_language,
                               number_part=number_part,
                               chapter=number_chapter,
                               name_page=name_page,
                               task_list=task_list)
    else:
        return redirect(url_for('home'))


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        next_url = request.form.get('next')
        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            if next_url:
                return redirect(next_url)
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
                    bcrypt.generate_password_hash(form.password.data), form.email.data, 'is_user')
        return save_in_db(user, 'home')
    return render_template("signup.html", form=form, name_page='Регистрация')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
