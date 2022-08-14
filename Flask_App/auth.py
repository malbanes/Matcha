from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
#from models import User
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import get_db_connection

from passlib.hash import md5_crypt
from passlib.hash import bcrypt

from models import User

from token_gen import generate_confirmation_token, confirm_token, generate_email_token, confirm_email_token
from email_mngr import send_email
from password_checker import password_check
import re
from datetime import datetime
from localization import localize_user
from scoring import scoring_calculation
from werkzeug.exceptions import RequestEntityTooLarge


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
        try:
            # start request parsing
            form1 = request.form
        except RequestEntityTooLarge as e:
            flash('Please check your login details')
            return redirect(url_for('auth.login'))
        conn = get_db_connection()
        cur = conn.cursor()
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        cur.execute("SELECT * FROM users WHERE username=%(username)s LIMIT 1", {'username': username})
        user = cur.fetchone()
        
        # check if the user actually exists + take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user:
            flash('Please check your login details and try again - or sign up')
            return redirect(url_for('auth.login')) 
        # if the user doesn't exist or password is wrong, reload the page
        elif not bcrypt.verify(password,user[2]):
            flash('Please check your login details and try again - or sign up')
            return redirect(url_for('auth.login')) 
        # if the above check passes, then we know the user has the right credentials
        login_user(User(user), remember=remember)
        cur.execute("UPDATE profil SET is_online = true WHERE user_id=%(id)s", {'id': current_user.id})
        cur.execute("SELECT score from profil WHERE user_id=%(id)s LIMIT 1", {'id': current_user.id})
        former_score = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) from images WHERE profil_id=%(id)s", {'id': current_user.id})
        image_num = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) from likes WHERE receiver_id=%(id)s", {'id': current_user.id})
        likes_num = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) from \"ProfilInterest\" WHERE user_id=%(id)s", {'id': current_user.id})
        tag_num = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) from accountcontrol WHERE to_user_id=%(id)s and blocked=true", {'id': current_user.id})
        block_num = int(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) from accountcontrol WHERE to_user_id=%(id)s and fake=true", {'id': current_user.id})
        report_num = int(cur.fetchone()[0])
        cur.execute("SELECT last_log from profil WHERE user_id=%(id)s", {'id': current_user.id})
        lact_co_date = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT receiver_id) from messages WHERE sender_id=%(id)s", {'id': current_user.id})
        match_num = int(cur.fetchone()[0])
        updated_score = scoring_calculation(former_score, image_num, likes_num, tag_num, block_num, report_num, lact_co_date, match_num)
        cur.execute("UPDATE profil SET score = %(score)s WHERE user_id=%(id)s", {'score': updated_score, 'id': current_user.id})
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('main.profile'))


# sign up page that return 'sign up'
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    # If request is GET, return the sign up page and forms
    if request.method=='GET': 
        return render_template('signup.html')
    # if request is POST, then check if the email doesn't already exist and then save data
    else: 
        try:
            # start request parsing
            form1 = request.form
        except RequestEntityTooLarge as e:
            flash('Please check your login details')
            return redirect(url_for('auth.signup'))
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        password = request.form.get('password')
        username_regex = r'.*\S.*'
        match = re.fullmatch(username_regex, username)
        if len(str(email)) > 200 or len(str(first_name)) > 200 or len(str(last_name)) > 200 or len(str(username)) > 200 or len(str(email)) < 1 or len(str(first_name)) < 1 or len(str(last_name)) < 1 or len(str(username)) < 1 or match is None:
            flash('There was an issue with your inputs, try again',)
            return redirect(url_for('auth.signup'))
        # if this returns a user, then the email already exists in database
        #user = User.query.filter_by(email=email).first()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT email FROM users WHERE email=%(email)s OR username = %(username)s", {'email': email, 'username': username})  
        user = cur.fetchall()
        # if a user is found, we want to redirect back to signup page so user can try again
        if user: 
            flash('Email or User Name address already exists')
            return redirect(url_for('auth.signup'))
        pass_complexity = password_check(password)
        if pass_complexity['password_ok'] == False:
            error_to_return = ""
            if pass_complexity['length_error_min'] == True:
                error_to_return = error_to_return + "\nPassword must contain at least 8 characters. "
            if pass_complexity['length_error_max'] == True:
                error_to_return = error_to_return + "\nPassword must contain less than 201 characters. "
            if pass_complexity['digit_error'] == True:
                error_to_return = error_to_return + "\nPassword must contain at least 1 digit. "
            if pass_complexity['uppercase_error'] == True:
                error_to_return = error_to_return + "\nPassword must contain at least 1 uppercase character. "
            if pass_complexity['lowercase_error'] == True:
                error_to_return = error_to_return + "\nPassword must contain at least 1 lowercase character. "
            if pass_complexity['symbol_error'] == True:
                error_to_return = error_to_return + "\nPassword must contain at least 1 special character. "
            flash('password not enough complex:\n' + error_to_return)
            return redirect(url_for('auth.signup'))
        else:
            # create a new user with the form data. Hash the password so the plaintext version isn't saved.
            cur.execute("INSERT INTO users (email, first_name, last_name, username, password, confirmed) VALUES (%(email)s, %(first_name)s, %(last_name)s, %(username)s, crypt(%(password)s, gen_salt('bf')), false);", {'email': email, 'first_name': first_name, 'last_name': last_name, 'username': username, 'password': password})
            conn.commit()
            # add the new user to the database
            new_user = cur.execute("SELECT * FROM users WHERE email=%(email)s LIMIT 1", {'email': email})
            new_user = cur.fetchone()
            localisation, latitude, longitude = localize_user()
            loc_id = cur.execute("INSERT INTO location (latitude,longitude,date_modif,city) VALUES (%(lat)s, %(long)s, %(date)s, %(city)s) returning id", {'lat': latitude, 'long': longitude, 'date': str(datetime.date(datetime.now())), 'city': localisation})
            conn.commit()
            loc_id = cur.fetchone()
            cur.execute("INSERT INTO profil (user_id, location_id, score) VALUES (%(user_id)s, %(location_id)s, 0)", {'user_id': new_user[0], 'location_id': loc_id[0]})
            conn.commit()
            cur.execute("UPDATE profil SET is_online = true WHERE user_id=%(id)s", {'id': new_user[0]})
            conn.commit()
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
    cur.execute("SELECT * FROM users WHERE email=%(email)s LIMIT 1", {'email': email})
    user = cur.fetchone()
    #print(user)
    if user[7] == True:
        flash('Account confirmed. Please login.', 'success')
    else:
        cur.execute("UPDATE users SET confirmed = true WHERE email=%(email)s", {'email': email})
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
        return redirect(url_for('main.index'))
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

# reset password class that return 'resetpassword'
@auth.route('/reset_page', methods=['GET', 'POST'])
def reset_page():
    if request.method=='GET': 
        return render_template('reset_page.html')
    else:
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        email = request.form.get('email')
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not (re.fullmatch(email_regex, email)) or len(str(email)) > 200:
            flash('Email structure not valid!')
            return redirect(url_for('auth.reset_page'))
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE email=%(email)s LIMIT 1", {'email': email})
            user = cur.fetchone()
            if user:
                token = generate_email_token(user[6])
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                html = render_template('reset_password_request.html', reset_url=reset_url)
                subject = "A password reset request has been initiated"
                send_email(user[6], subject, html)
            cur.close()
            conn.close()
            flash('Check your email for the instructions to reset your password')
            return redirect(url_for('auth.login'))
        return render_template('reset_page.html')

# reset password validation page that return 'confirm/<token>'
@auth.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    email = confirm_email_token(token)
    if email == False:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if  request.method=='POST': 
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email=%(email)s LIMIT 1", {'email': confirm_email_token(token)})
        user = cur.fetchone()
        password = request.form.get('password')
        pass_complexity = password_check(password)
        if pass_complexity['password_ok'] == False:
            error_to_return = ""
            if pass_complexity['length_error_min'] == True:
                error_to_return = error_to_return + "\nPassword must contain at least 8 characters. "
            if pass_complexity['length_error_max'] == True:
                error_to_return = error_to_return + "\nPassword must contain less than 201 characters. "
            if pass_complexity['digit_error'] == True:
                error_to_return = error_to_return + "\nPassword must contain at least 1 digit. "
            if pass_complexity['uppercase_error'] == True:
                error_to_return = error_to_return + "\nPassword must contain at least 1 uppercase character. "
            if pass_complexity['lowercase_error'] == True:
                error_to_return = error_to_return + "\nPassword must contain at least 1 lowercase character. "
            if pass_complexity['symbol_error'] == True:
                error_to_return = error_to_return + "\nPassword must contain at least 1 special character. "
            flash('Password not enough complex:\n' + error_to_return + ' Reset your password again')
            return render_template('reset_password.html', token=token)
        else:
            if user and user[7] == True:
                cur.execute("UPDATE users SET password = crypt(%(password)s, gen_salt('bf')) WHERE email=%(email)s", {'password': password,'email': email})
                conn.commit()
                flash('Your password has been reset. Thanks!', 'success')
            else:
                flash('There was an issue in the reset procedure, try again.', 'danger')
        cur.close()
        conn.close()
        logout_user()
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', token=token)

# define logout path
@auth.route('/logout') 
@login_required
def logout():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE profil SET is_online = false, last_log = %(date)s WHERE user_id=%(id)s", {'date': str(datetime.date(datetime.now())),'id': current_user.id})
    conn.commit()
    cur.close()
    conn.close()
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