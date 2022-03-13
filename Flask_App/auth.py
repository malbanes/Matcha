from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import db

# create a Blueprint object that we name 'auth'
auth = Blueprint('auth', __name__) 

# define login page path
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # if the request is GET, return the login page
    if request.method=='GET': 
        return render_template('login.html')
    # if the request is POST, then check if the user exist and with the right password
    else:
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(email=email).first()
        # check if the user actually exists + take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user:
            flash('Please sign up before!')
            return redirect(url_for('auth.signup'))
        # if the user doesn't exist or password is wrong, reload the page
        elif not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login')) 
        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        return redirect(url_for('main.profile'))


# sign up page that return 'sign up'
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # If request is GET, return the sign up page and forms
    if request.method=='GET': 
        return render_template('signup.html')
    # if request is POST, then check if the email doesn't already exist and then save data
    else: 
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(email=email).first()
        # if a user is found, we want to redirect back to signup page so user can try again
        if user: 
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))
        
        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

# define logout path
@auth.route('/logout') 
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))