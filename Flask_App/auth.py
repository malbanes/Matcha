from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
#from models import User
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import get_db_connection

from passlib.hash import md5_crypt
from passlib.hash import bcrypt

from models import User

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
        conn = get_db_connection()
        cur = conn.cursor()
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        cur.execute("SELECT * FROM users WHERE email='{0}' LIMIT 1;".format(email))
        user = cur.fetchone()
        
        # check if the user actually exists + take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user:
            flash('Please sign up before!')
            return redirect(url_for('auth.signup'))
        # if the user doesn't exist or password is wrong, reload the page
        elif not bcrypt.verify(password,user[2]):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login')) 
        # if the above check passes, then we know the user has the right credentials
        login_user(User(user), remember=remember)
        print("hello")
        print(current_user.name)
        print(dir(current_user))
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
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        password = request.form.get('password')
        # if this returns a user, then the email already exists in database
        #user = User.query.filter_by(email=email).first()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT email FROM users WHERE email='{0}' OR username = '{1}';".format(email, username))
        user = cur.fetchall()
        # if a user is found, we want to redirect back to signup page so user can try again
        if user: 
            flash('Email or User Name address already exists')
            return redirect(url_for('auth.signup'))
        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        cur.execute("INSERT INTO users (email, first_name, last_name, username, password) VALUES ('{0}','{1}','{2}','{3}',crypt('{4}', gen_salt('bf')));".format(email, first_name, last_name,username,password))
        conn.commit()
        # add the new user to the database
        cur.close()
        conn.close() 
        return redirect(url_for('auth.login'))

# define logout path
@auth.route('/logout') 
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

    #    if request.method == 'POST':
    #    name = request.form['name']
    #    age = request.form['age']
    #    cursor = mysql.connection.cursor()
    #    cursor.execute(''' INSERT INTO info_table VALUES(%s,%s)''',(name,age))
    #    mysql.connection.commit()
    #    cursor.close()
    #    return f"Done!!"