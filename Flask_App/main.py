from flask import Blueprint, render_template, flash, url_for, redirect, current_app, jsonify
from flask_login import login_required, current_user

from flask_mail import Mail
#Chargement socketIO des modules requis
from flask import Flask, session, request         
from flask_socketio import SocketIO, emit, join_room, leave_room, \
      close_room, rooms, disconnect                                  

from __init__ import create_app, get_db_connection
from login_decorator import check_confirmed
from age_calc import age, age_period
from localization import localize_text, distance
from datetime import date
from token_gen import generate_confirmation_token, confirm_token, generate_email_token, confirm_email_token
from email_mngr import send_email

from passlib.hash import md5_crypt
from passlib.hash import bcrypt
from password_checker import password_check
from img_upload import upload_file_to_s3, create_presigned_url
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

GENRE = ["Non-binaire", "Men", "Women"]
ORIENTATION = ["Bisexuel", "Heterosexuel", "Homosexuel"]

# home page that return 'index'
main = Blueprint('main', __name__)
@main.route('/') 
def index():
    return render_template('index.html')

# profile page that return 'profile'
@main.route('/profile') 
@login_required
@check_confirmed
def profile():
    images_path = dict()
    print(current_user.name)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM profil WHERE user_id='{0}' LIMIT 1;".format(current_user.id))
    profil = cur.fetchone()
    print(profil)
    age_num = str(age(profil[5]))
    description = profil[6]
    score = str(profil[8])
    if score == "None":
        score = str(0)
    genre = GENRE[profil[2]]
    orientation = ORIENTATION[profil[3]]
    cur.execute("SELECT image_profil FROM profil WHERE user_id='{0}' LIMIT 1;".format(current_user.id))
    image_profil = cur.fetchone()
    if image_profil :
        image_profil_id = str(image_profil[0])
    else :
        image_profil_id = "0"
    cur.execute("SELECT id, path FROM images WHERE profil_id='{0}';".format(current_user.id))
    all_images = cur.fetchall()
    for key, imgpth in all_images:
        images_path[str(key)] = create_presigned_url(current_app.config["S3_BUCKET"], imgpth)
    total_img = len(images_path)

    cur.execute("SELECT interest_id::INTEGER FROM \"ProfilInterest\" WHERE user_id='{0}';".format(current_user.id))
    interest = cur.fetchall()
    print(interest)
    interest_list = []
    for id in interest:
        cur.execute("SELECT hashtag FROM \"Interest\" WHERE id='{0}' LIMIT 1;".format(id[0]))
        interest_list.append(cur.fetchone()[0].rstrip())
        print(interest_list)
    cur.execute("SELECT city FROM location WHERE id='{0}';".format(profil[4]))
    localisation = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template('profile.html', name=current_user.name, age=age_num, score=score, desc=description, genre=genre, orientation=orientation,  interest_list=interest_list, localisation=localisation, image_profil_id=image_profil_id, images_path=images_path, total_img=total_img)

# edit profile page that return 'edit-profile'
@main.route('/edit-profile') 
def editprofile():
    image_path = dict()
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT image_profil FROM profil WHERE user_id='{0}' LIMIT 1;".format(current_user.id))
    image_profil = cur.fetchone()
    image_profil_id = str(image_profil[0])

    cur.execute("SELECT id, path FROM images WHERE profil_id='{0}';".format(current_user.id))
    all_images = cur.fetchall()
    cur.execute("SELECT bio, genre_id, orientation_id FROM profil WHERE user_id='{0}' LIMIT 1;".format(current_user.id))

    i_am = cur.fetchone()
    i_am_bio = str(i_am[0])
    i_am_genre = GENRE[i_am[1]]
    i_am_orientation = ORIENTATION[i_am[2]]
    print(i_am)
    cur.execute("SELECT interest_id::INTEGER FROM \"ProfilInterest\" WHERE user_id='{0}';".format(current_user.id))
    interest = cur.fetchall()
    print(interest)
    interest_list = []
    for id in interest:
        cur.execute("SELECT hashtag FROM \"Interest\" WHERE id='{0}' LIMIT 1;".format(id[0]))
        interest_list.append(cur.fetchone()[0].rstrip())
        print(interest_list)
    print("blablabla")
    cur.execute("SELECT * FROM \"Interest\";")
    full_interest = cur.fetchall()
    cur.close()
    conn.close()
    for key, imgpth in all_images:
        image_path[str(key)] = create_presigned_url(current_app.config["S3_BUCKET"], imgpth)
    total_img = len(image_path)
    if total_img != 5:
        image_path['default'] = create_presigned_url(current_app.config["S3_BUCKET"],"test/no-photo.png")
    return render_template('edit-profile.html', image_profil=image_profil_id, images_urls=image_path, total_img=total_img, interest=interest_list, bio=i_am_bio, genre=i_am_genre, orientation=i_am_orientation, full_interest=full_interest)

@main.route('/uploadajax', methods = ['POST'])
def upldfile():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('There is no file')
            return ("KO")
        file1 = request.files['file']
        if file1.filename == "":
            return "Please select a file"
        if file1 :
            file1.filename = secure_filename(file1.filename)
            path = str(current_user.email) + str(current_user.id)
            output, file_path = upload_file_to_s3(file1, app.config["S3_BUCKET"], path)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO images (title, path, profil_id, date_added) VALUES ('{0}', '{1}', '{2}', '{3}');".format(file1.filename, file_path, current_user.id, date.today()))
            conn.commit()
            cur.close()
            conn.close()
            return ("OK")
        else:
            return ("KO")

@main.route('/setimageprofil', methods = ['POST'])
def setimgprofil():
    if request.method == 'POST':
        img_id = request.form['data']
        if img_id :
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute
            cur.execute("UPDATE profil SET image_profil='{0}' WHERE user_id={1};".format(img_id,current_user.id))
            conn.commit()
            cur.close()
            return ("success")
        else:
            return ("KO")

@main.route('/deleteimage', methods = ['POST'])
def delimg():
    if request.method == 'POST':
        img_id = request.form['data']
        if img_id :
            return (img_id)
        else:
            return ("KO")

@main.route('/updatebio', methods = ['POST'])
def updbio():
    if request.method == 'POST':
        if 'newBio' not in request.form:
            flash('There is no bio')
            return ("KO")
        bio = request.form['newBio']
        if bio :
            bio = bio.replace("'", "`")
            print(bio)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE profil SET bio='{0}' WHERE user_id={1};".format(bio,current_user.id))
            conn.commit()
            cur.close()
            return (bio)
        else:
            return ("KO")

@main.route('/updateprimary', methods = ['POST'])
def updprim():
    if request.method == 'POST':
        if 'newGender' not in request.form:
            flash('There is no gender')
            return ("KO")
        gender = request.form['newGender']
        orient = request.form['newOrient']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE profil SET genre_id='{0}', orientation_id={1} WHERE user_id={2};".format(gender, orient, current_user.id))
        conn.commit()
        cur.close()
        conn.close()
        if (gender) :
            return {
                'gender': GENRE[int(gender)],
                'orient': ORIENTATION[int(orient)]
            }
        if (orient) :
            return {
                'gender': GENRE[int(gender)],
                'orient': ORIENTATION[int(orient)]
            }
        else :
            return ("KO")

    
@main.route('/updatehashtag', methods = ['POST'])
def updhash():
    if request.method == 'POST':
        hash_id = request.form.getlist("check")
        print(hash_id)
        existing_list = []
        if (hash_id):
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM \"ProfilInterest\" WHERE user_id='{0}';".format(current_user.id))
            except: 
                print("no hash  for the user")
            for i in hash_id:
                cur.execute("INSERT INTO \"ProfilInterest\" (user_id, interest_id) VALUES ('{0}', '{1}');".format(current_user.id, i))
                conn.commit()
            for id in hash_id:
                cur.execute("SELECT hashtag FROM \"Interest\" WHERE id='{0}' LIMIT 1;".format(id))
                existing_list.append(cur.fetchone()[0].rstrip())
                print(existing_list)
            cur.close()
            conn.close()
            return jsonify(existing_list)
        else:
            return ("KO")

# account profile page that return 'account'
@main.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM profil WHERE user_id='{0}' LIMIT 1;".format(current_user.id))
    profil = cur.fetchone()
    cur.execute("SELECT city FROM location WHERE id='{0}';".format(profil[4]))
    localisation = cur.fetchone()[0]
    username = current_user.username
    email = current_user.email
    firstname = current_user.firstname
    lastname = current_user.lastname
    cur.execute("SELECT path FROM images WHERE id='{0}' LIMIT 1;".format(profil[7]))
    image_profil = cur.fetchone()
    if image_profil :
        image_profil_path = create_presigned_url(current_app.config["S3_BUCKET"], image_profil[0])
    else :
        image_profil_path = 0
    if request.method=='GET':
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('main.index'))
        onglet = "account"
        section = "like"
        if request.args.get('onglet'):
            onglet = request.args.get('onglet')
            print(onglet)
        if request.args.get('section'):
            section = request.args.get('section')
        return render_template('account.html', username=username, email=email, firstname=firstname, lastname=lastname, localisation=localisation, image_profil=image_profil_path, onglet=onglet, section=section)
    else:
        if 'username' in request.form:
            if current_user.confirmed is False:
                flash('Please confirm your account!', 'warning')
                return redirect(url_for('main.index'))
            print("post")
            firstname1 = request.form.get('first_name')
            lastname1 = request.form.get('last_name')
            username1 = request.form.get('username')
            localisation1 = request.form.get('location')
            cur.execute("SELECT * FROM users WHERE username='{0}';".format(username1))
            username_check = cur.fetchall()
            print(username_check)
            if username1 != "" and username_check != []:
                flash('User Name address already exists')
            elif username1 != "":
                cur.execute("UPDATE users SET username = '{0}' WHERE id='{1}';".format(username1,current_user.id))
                conn.commit()
                username = username1
            if firstname1 != "":
                cur.execute("UPDATE users SET first_name = '{0}' WHERE id='{1}';".format(firstname1,current_user.id))
                conn.commit()
                firstname = firstname1           
            if lastname1 != "":
                cur.execute("UPDATE users SET last_name = '{0}' WHERE id='{1}';".format(lastname1,current_user.id))
                conn.commit()
                lastname = lastname1           
            if localisation1 != "":
                lat, lont, display_loc = localize_text(str(localisation1))
                today = date.today()
                print(lat)
                print(lont)
                print(display_loc)
                if  display_loc != "ERROR - WRONG LOCALISATION":
                    cur.execute("UPDATE location SET latitude = '{0}', longitude = '{1}', date_modif = '{2}', city = '{3}' WHERE id='{4}';".format(lat,lont,today,display_loc.strip(),profil[4]))
                    conn.commit()
                    localisation = display_loc
                else:
                    flash('New location not found')
        elif 'oldpassword' in request.form:
            print("password")
            if current_user.confirmed is False:
                flash('Please confirm your account!', 'warning')
                return redirect(url_for('main.index'))
            else:
                oldpassword = request.form.get('oldpassword')
                password1 = request.form.get('password1')
                password2 = request.form.get('password2')
                cur.execute("SELECT * FROM users WHERE id='{0}' LIMIT 1;".format(current_user.id))
                user = cur.fetchone()
                pass_complexity = password_check(password1)
                if password1 != password2:
                    flash('new passwords don\'t match, try again', 'warning')
                elif not bcrypt.verify(oldpassword,user[2]):
                    flash('Please check your login details and try again.','warning')
                elif pass_complexity['password_ok'] == False:
                    error_to_return = ""
                    if pass_complexity['length_error'] == True:
                        error_to_return = error_to_return + "\nPassword must contain at least 8 characters. "
                    if pass_complexity['digit_error'] == True:
                        error_to_return = error_to_return + "\nPassword must contain at least 1 digit. "
                    if pass_complexity['uppercase_error'] == True:
                        error_to_return = error_to_return + "\nPassword must contain at least 1 uppercase character. "
                    if pass_complexity['lowercase_error'] == True:
                        error_to_return = error_to_return + "\nPassword must contain at least 1 lowercase character. "
                    if pass_complexity['symbol_error'] == True:
                        error_to_return = error_to_return + "\nPassword must contain at least 1 special character. "
                    flash('password not enough complex:\n' + error_to_return, 'warning')
                else:
                    cur.execute("UPDATE users SET password = crypt('{0}', gen_salt('bf')) WHERE id='{1}';".format(password1, current_user.id))
                    conn.commit()
                    flash('password updated', 'success')
        elif 'email' in request.form:
            print("email")
            email1 = request.form.get('email')
            cur.execute("SELECT * FROM users WHERE email='{0}';".format(email1))
            email_check = cur.fetchall()
            print(email_check)
            email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if email1 != "" and email_check == [] and re.fullmatch(email_regex, email):
                cur.execute("UPDATE users SET email = '{0}', confirmed = false WHERE id='{1}';".format(email1,current_user.id))
                conn.commit()
                token = generate_confirmation_token(email1)
                confirm_url = url_for('auth.confirm_email', token=token, _external=True)
                html = render_template('activate.html', confirm_url=confirm_url)
                subject = "Please confirm your email"
                send_email(email1, subject, html)
                flash('A confirmation email has been sent via email.', 'success')
                email = email1
            else:
                flash('Email structure not valid or email address already exists')
        else: 
            print("No modal implemented")
        cur.close()
        conn.close()

        return render_template('account.html', username=username, email=email, firstname=firstname, lastname=lastname, localisation=localisation, image_profil=image_profil_path)

# match page that return 'match'
@main.route('/match') 
def match():
    return render_template('match.html')

# chat page that return 'match'
@main.route('/chat') 
def chat():
    return render_template('chat.html')

# notification page that return 'match'
@main.route('/notification') 
def notification():
    return render_template('notification.html')

# search page that return 'match'
@main.route('/search', methods=['GET', 'POST'])
def search():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name FROM users;")
    profil_list = cur.fetchall()
    if request.method=='POST':
        if 'ageMinSearch' in request.form:
            print("blablabebfbeizfi")
            profil_list = []
            final_profil_list_id = []
            ageMinSearch = request.form.get('ageMinSearch')
            ageMaxSearch = request.form.get('ageMaxSearch')
            citySearch = request.form.get('citySearch')
            locRangeSearch = request.form.get('locRangeSearch')
            scoreMinSearch = request.form.get('scoreMinSearch')
            scoreMaxSearch = request.form.get('scoreMaxSearch')
            #before#
            ageMinComp = age_period(ageMinSearch)
            #after#
            ageMaxComp = age_period(ageMaxSearch)
            #to meter#
            locRangeSearch = int(locRangeSearch)
            print(locRangeSearch)
            if citySearch == '':
                cur.execute("SELECT user_id FROM profil WHERE age between '{1}' and '{0}' AND score between {2} and {3};".format(ageMinComp, ageMaxComp, int(scoreMinSearch), int(scoreMaxSearch)))
                profil_list_id = cur.fetchall()
                print(profil_list)
                for i in profil_list_id:
                    cur.execute("SELECT id, first_name FROM users where id={0} LIMIT 1;".format(i[0]))
                    if i[0] != current_user.id:
                        profil_list.append(cur.fetchone())
            else:
                cur.execute("SELECT user_id, location_id FROM profil WHERE age between '{1}' and '{0}' AND score between {2} and {3};".format(ageMinComp, ageMaxComp, int(scoreMinSearch), int(scoreMaxSearch)))
                profil_list_id = cur.fetchall()
                cur.execute("SELECT location_id FROM profil WHERE user_id = {0} LIMIT 1;".format(current_user.id))
                loc_me = cur.fetchone()
                cur.execute("SELECT latitude, longitude FROM location WHERE id = {0} LIMIT 1;".format(loc_me[0]))
                coordinates_me = cur.fetchone()
                for i in profil_list_id:
                    if i[0] != current_user.id:
                        cur.execute("SELECT latitude, longitude FROM location WHERE id = {0} LIMIT 1;".format(i[1]))
                        coordinates_others = cur.fetchone()
                        off_distance = distance(coordinates_me[0], coordinates_me[1], coordinates_others[0], coordinates_others[1])
                        print(off_distance)
                        if off_distance <= float(locRangeSearch):
                            print("keep user")
                            final_profil_list_id.append(i)
                        else:
                            print("remove user")
                print("hiiiiii")
                for i in final_profil_list_id:
                    cur.execute("SELECT id, first_name FROM users where id={0} LIMIT 1;".format(i[0]))
                    profil_list.append(cur.fetchone())
            cur.close()
            conn.close()
    print(profil_list)
    final_users = []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM \"Interest\";")
    full_interest = cur.fetchall()
    for user in profil_list:
        if user[0] != current_user.id:
            cur.execute("SELECT image_profil, age, location_id FROM profil WHERE user_id='{0}' LIMIT 1;".format(user[0]))
            user_details = cur.fetchone()
            print(user_details)
            if user_details != None:
                user_age = str(age(user_details[1]))
                cur.execute("SELECT city FROM location WHERE id='{0}' LIMIT 1;".format(user_details[2]))
                user_location = cur.fetchone()[0]
                final_users.append([user[1], user_age, user_location])
                print(final_users)
                print(len(final_users))
    print(profil_list)
    cur.close()
    conn.close()
    return render_template('research.html', all_users = final_users, user_num=len(final_users), full_interest=full_interest)
    

# we initialize our flask app using the  __init__.py function 
app = create_app()
#Spécification de la bibliothèque à utiliser pour le traitement asynchrone
# `threading`, `eventlet`, `gevent`Peut être sélectionné parmi
async_mode = None

#Objet Flask, asynchrone_Créer un objet serveur SocketIO en spécifiant le mode
socketio = SocketIO(app, async_mode=async_mode)

#Variable globale pour stocker les threads
thread = None

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    emit('my response', {'data': 'Envoyez le premier message !', 'count': 0})

@socketio.on('my event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',                                               
         {'data': message['data'], 'count': session['receive_count']})
                                                                      
@socketio.on('my broadcast event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)

# setup Mail
mail = Mail(app)     
if __name__ == '__main__':
    ##db.create_all(app=create_app())
    app.run(debug=True)
    socketio.run(app)