# login_decorator.py
from functools import wraps

from flask import url_for, flash, redirect
from flask_login import current_user

from __init__ import get_db_connection

def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('auth.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function


def check_full_profile(func):
    @wraps(func)
    def decorated_function2(*args, **kwargs):
        ##age ##bio ## image
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT age, bio, image_profil_id FROM profil WHERE user_id=%(id)s LIMIT 1", {'id': current_user.id})
        user_details = cur.fetchone()
        print("HELLLOO")
        print(user_details)
        if  user_details[0] == None or user_details[1] == None or user_details[1] == 'None' or user_details[2] == 0:
            flash('Please fill your age, bio and add a profil image!', 'warning')
            cur.close()
            conn.close()
            return redirect(url_for('main.editprofile'))
        cur.close()
        conn.close()
        return func(*args, **kwargs)

    return decorated_function2