from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
#from models import User
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import get_db_connection

from passlib.hash import md5_crypt
from passlib.hash import bcrypt

from models import User

from token_gen import generate_confirmation_token, confirm_token
from email_mngr import send_email

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
        cur.execute("INSERT INTO users (email, first_name, last_name, username, password, confirmed) VALUES ('{0}', '{1}', '{2}', '{3}', crypt('{4}', gen_salt('bf')), false);".format(email, first_name, last_name,username,password))
        conn.commit()
        # add the new user to the database
        new_user = cur.execute("SELECT * FROM users WHERE email='{0}' LIMIT 1;".format(email))
        new_user = cur.fetchone()
        cur.close()
        conn.close()
        
        token = generate_confirmation_token(email)
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        html = render_template('activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(email, subject, html)
        login_user(User(new_user))
        flash('A confirmation email has been sent via email.', 'success')
        
        return redirect(url_for('auth.unconfirmed'))

# confirm email page that return 'confirm/<token>'
@auth.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email='{0}' LIMIT 1;".format(email))
    user = cur.fetchone()
    print(user)
    if user[7] == True:
        flash('Account already confirmed. Please login.', 'success')
    else:
        cur.execute("UPDATE users SET confirmed = true WHERE email='{0}';".format(email))
        conn.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    cur.close()
    conn.close()
    return redirect(url_for('main.index'))

# unconfirmed email page that return 'unconfirmed'
@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('main.index')
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html')

# resend email page that return 'resend'

@auth.route('/resend')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    html = render_template('activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('auth.unconfirmed'))


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