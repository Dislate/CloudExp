from CloudExp import db
from flask import url_for, redirect


def save_in_db(obj, template=None, delete=False, redirect_to_page=True, **kwargs):
    '''
    Function get SQLAlchemy ORM object and save in db or delete from db.
    :param obj: SQLAlchemy object
    :param template: name template for render and redirect
    :param delete: if True function delete row from db, not save
    :param redirect_to_page: If False just save or delete ORM object
    :param kwargs: get context for template
    :return: url
    '''
    if delete:
        db.session.delete(obj)
    else:
        db.session.add(obj)
    db.session.commit()
    if redirect_to_page:
        return redirect(url_for(template, **kwargs))
