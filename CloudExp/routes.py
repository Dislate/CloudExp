import logging
from flask import redirect, url_for, render_template, request, flash, send_from_directory, Response
from flask_login import login_user, current_user, logout_user
from CloudExp import app, db, bcrypt
from CloudExp.models import User, Language, Part, Chapter, Task, Seo
from CloudExp.forms import RegistrationForm, LoginForm, AddingLanguageForm, AddingPartForm, AddingChapterForm
from CloudExp.helper import save_in_db
from CloudExp.decorators import login_required

logging.basicConfig(filename='forms_logs.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.context_processor
def inject_languages():
    """
    Get dictionary all language to show in base template
    :return: dict or status code
    """
    try:
        return dict(languages_list=Language.query.all())
    except Exception as err:
        logger.exception(err)
        return Response(503)


@app.route('/')
def home():
    """Rendering main page"""
    return render_template("index.html")


@app.route('/robots.txt')
def robots():
    """For search robots"""
    return send_from_directory(app.static_folder, request.path[1:])


@app.route('/agreement')
def agreement():
    """Rendering agreement page
    :return:template"""
    return render_template("agreement.html")


@app.route('/admin-panel', methods=['GET'])
@login_required
def admin_panel():
    """
    Function show admin-panel for work with content of our website
    :return:template or url
    """
    if current_user.privilages == 'is_admin' and Language.query.first():
        id_chapter_for_work = request.args.get('data_input_chapter')
        current_chapter = None
        if id_chapter_for_work:
            current_chapter = Chapter.query.filter_by(id_chapter=id_chapter_for_work).first()
        elif Chapter.query.first():
            current_chapter = Language.query.first().part_list.first().chapter_list.first()

        # if current chapter haven't seo data, then create one
        if current_chapter is not None and not current_chapter.seo:
            add_seo_for_chapter = Seo(current_chapter.id_chapter, '', '')
            save_in_db(add_seo_for_chapter, redirect_to_page=False)

        return render_template('admin-panel.html', langs=Language.query.all(),
                               current_chapter=current_chapter, name_page='Админ-панель')
    return redirect(url_for('adding_language'))


@app.route('/admin-panel/update-chapter-tasks', methods=["POST"])
@login_required
def update_chapter_tasks():
    '''
    Function processes form of task and update data in database
    :return:template or status code
    '''
    if request.method == 'POST':
        id_current_chapter = request.args.get('data_input_chapter', type=int)

        current_chapter = Chapter.query.first()
        if id_current_chapter:
            current_chapter = Chapter.query.filter_by(id_chapter=id_current_chapter).first()

        # updating data about task for current chapter
        text_chapter = request.form['text_chapter']
        current_chapter.text_chapter = text_chapter
        for index, task in enumerate(current_chapter.task_list):
            task.name_task = request.form[f'name_task_{index + 1}']
            task.text_task = request.form[f'text_task_{index + 1}']
            task.solution = request.form[f'solution_task_{index + 1}']
            task.hint = request.form[f'hint_task_{index + 1}']
        db.session.commit()
        return redirect(url_for('admin_panel', data_input_chapter=current_chapter.id_chapter))
    return Response(status=404)


@app.route('/admin-panel/update-seo', methods=['POST'])
@login_required
def update_seo():
    '''
    Function processes form of seo and update data in database
    :return:url or status code
    '''
    if request.method == 'POST':
        keywords = request.form['keywords_chapter']
        description = request.form['description_chapter']

        chapter = Chapter.query.first()
        if request.args.get('data_input_chapter'):
            chapter = Chapter.query.filter_by(id_chapter=request.args.get('data_input_chapter')).first()

        chapter.seo.keywords = keywords
        chapter.seo.description = description
        db.session.commit()
        return redirect(url_for('admin_panel', data_input_chapter=chapter.id_chapter))
    return Response(status=404)


@app.route('/admin-panel/adding-task', methods=['GET'])
@login_required
def adding_task():
    '''
    Function add new task for chapter
    :return:url
    '''
    id_chapter = request.args.get('current_chapter')
    new_task = Task(int(id_chapter), '', '', '', '')
    return save_in_db(new_task, 'admin_panel', data_input_chapter=id_chapter)


@app.route('/admin-panel/delete-task', methods=['GET'])
@login_required
def delete_task():
    '''
    Function delete task for chapter
    :return:url
    '''
    # reading args
    id_chapter = request.args.get('current_chapter')
    index_del_task = request.args.get('delete_task', type=int)
    # find task
    current_task = Chapter.query.filter_by(id_chapter=id_chapter).first().task_list[index_del_task - 1]
    return save_in_db(current_task, 'admin_panel', delete=True, data_input_chapter=id_chapter)


@app.route('/adding-language', methods=['GET', 'POST'])
def adding_language():
    '''
    Function add new language
    :return:template or status code
    '''
    if current_user.is_authenticated and current_user.privilages == 'is_admin':
        add_lang_form = AddingLanguageForm()

        if add_lang_form.validate_on_submit():
            new_language = Language(add_lang_form.name_language.data, add_lang_form.description_language.data)
            return save_in_db(new_language, 'admin_panel')
        return render_template('adding-language.html', form=add_lang_form)
    return Response(status=401)


@app.route('/adding-part', methods=['GET', 'POST'])
def adding_part():
    '''
    This function add new part
    :return:url or template or status code
    '''
    if current_user.is_authenticated and current_user.privilages == 'is_admin':

        add_part_form = AddingPartForm()

        if add_part_form.validate_on_submit():
            new_part = Part(Language.query.filter_by(
                name_language=add_part_form.name_language.data).first().id_language, add_part_form.name_part.data)
            return save_in_db(new_part, 'admin_panel')
        return render_template('adding-part.html', form=add_part_form, language=request.args.get('language'))
    return Response(status=401)


@app.route('/adding-chapter', methods=['GET', 'POST'])
def adding_chapter():
    '''
    Function add new chapter
    :return:url or template or status code
    '''
    if current_user.is_authenticated and current_user.privilages == 'is_admin':

        add_chapter_form = AddingChapterForm()
        if add_chapter_form.validate_on_submit():
            new_chapter = Chapter(Part.query.filter_by(
                name_part=add_chapter_form.name_part.data).first().id_part,
                                  add_chapter_form.name_chapter.data,
                                  add_chapter_form.text_chapter.data)
            return save_in_db(new_chapter, 'admin_panel')
        return render_template('adding-chapter.html',
                               form=add_chapter_form,
                               part=request.args.get('part'))
    return Response(status=401)


@app.route('/languages/<language>', methods=['POST', 'GET'])
def get_language(language):
    '''
    Function shows all part and chapter for current language
    :return:template or status code
    '''
    current_language = Language.query.filter_by(name_language=language).first()
    if current_language:
        return render_template('language.html',
                               current_language=current_language,
                               name_page=current_language.name_language)
    return Response(status=404)


@app.route('/<language>/<name_part>/<name_chapter>', methods=['GET'])
def get_chapter(language, name_part, name_chapter):
    '''
    Function displays current chapter
    :return:template or url
    '''
    current_language = Language.query.filter_by(name_language=language).first()
    current_part = current_language.part_list.filter_by(name_part=name_part).first()
    current_chapter = current_part.chapter_list.filter_by(name_chapter=name_chapter).first()
    name_page = f"{current_language.name_language} - {current_chapter.name_chapter}"

    task_list = None
    if Chapter.task_list:
        task_list = current_chapter.task_list

    if current_language and current_part:
        return render_template('chapter.html',
                               current_language=current_language,
                               current_part=current_part,
                               current_chapter=current_chapter,
                               name_page=name_page,
                               task_list=task_list)
    return redirect(url_for('home'))


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    '''
    Function allows you to authorize  a user
    :return:url or template
    '''
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
    '''
    Function allows you to register a user
    :return:url or template
    '''
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
    '''
    Function allows you to logout a user
    :return:url
    '''
    logout_user()
    return redirect(url_for('home'))
