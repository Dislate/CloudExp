from CloudExp import db
from flask import url_for, redirect, render_template


def save_in_db(obj, template=None, delete=False, redirect_to_page=True, **kwargs):
    if delete:
        db.session.delete(obj)
    else:
        db.session.add(obj)
    db.session.commit()
    if redirect_to_page:
        return redirect(url_for(template, **kwargs))
