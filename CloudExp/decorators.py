from functools import wraps
from flask import redirect, request, url_for
from flask_login import current_user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_anonymous:
            return redirect(url_for('signin', next=request.url))
        return f(*args, **kwargs)

    return decorated_function
