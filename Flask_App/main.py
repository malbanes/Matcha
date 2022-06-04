from flask import Blueprint, render_template, flash, url_for, redirect, current_app, jsonify
from flask_login import login_required, current_user, logout_user

from flask_mail import Mail
#Chargement socketIO des modules requis
from flask import Flask, session, request         
from flask_socketio import SocketIO, emit, join_room, leave_room, \
      close_room, rooms, disconnect     
from threading import Lock                             

from __init__ import create_app, get_db_connection
from login_decorator import check_confirmed
from age_calc import age, age_period

from localization import localize_text, distance, localize_user
from datetime import date, datetime

from token_gen import generate_confirmation_token, confirm_token, generate_email_token, confirm_email_token
from email_mngr import send_email

from passlib.hash import md5_crypt
from passlib.hash import bcrypt
from password_checker import password_check
from img_upload import upload_file_to_s3, create_presigned_url
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

import re

GENRE = ["Non-binaire", "Men", "Women"]
ORIENTATION = ["Bisexuel", "Heterosexuel", "Homosexuel"]
rooms = []
NOTIF_TYPE = ["like", "view", "message"]
OFFSET = 20



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
    images_path = []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM profil WHERE user_id=%(id)s LIMIT 1", {'id': current_user.id})
    profil = cur.fetchone()
    age_num = str(age(profil[5]))
    description = profil[6]
    score = str(profil[8])
    is_online = profil[9]
    last_log = str(profil[10])
    if score == "None":
        score = str(0)
    genre = GENRE[profil[2]]
    orientation = ORIENTATION[profil[3]]
    cur.execute("SELECT image_profil FROM profil WHERE user_id=%(id)s LIMIT 1", {'id': current_user.id})
    image_profil = cur.fetchone()
    if image_profil:
        image_profil_id = str(image_profil[0])
    else :
        image_profil_id = "0"
    cur.execute("SELECT id, path FROM images WHERE profil_id=%(id)s", {'id': current_user.id})
    all_images = cur.fetchall()
    for key, imgpth in all_images:
        images_path.append([key,create_presigned_url(current_app.config["S3_BUCKET"], imgpth)])
    total_img = len(images_path)
    if images_path != []:
        fav_image = images_path[int(image_profil_id)][1]
    else:
        fav_image = "0"
    cur.execute("SELECT interest_id::INTEGER FROM \"ProfilInterest\" WHERE user_id=%(id)s", {'id': current_user.id})
    interest = cur.fetchall()
    interest_list = []
    for id in interest:
        cur.execute("SELECT hashtag FROM \"Interest\" WHERE id=%(id)s LIMIT 1", {'id': id[0]})
        interest_list.append(cur.fetchone()[0].rstrip())
        print(interest_list)
    cur.execute("SELECT city FROM location WHERE id=%(id)s", {'id': profil[4]})
    localisation = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template('profile.html', name=current_user.name, age=age_num, score=score, desc=description, genre=genre, orientation=orientation,  interest_list=interest_list, localisation=localisation, image_profil=fav_image, images_path=images_path, total_img=total_img, is_online=is_online, last_log=last_log)

# Other User profile page that return 'show-profile'
@main.route('/showprofile/<username>') 
@login_required
@check_confirmed
def showprofile(username):
    images_path = []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=%(username)s LIMIT 1", {'username': username})
    showuser_details = cur.fetchone()
    user_id = showuser_details[0]
    print(showuser_details[4])
    user_name = str(showuser_details[4]) + " " + str(showuser_details[5])
    user_username = str(showuser_details[1])
    cur.execute("SELECT * FROM profil WHERE user_id=%(id)s LIMIT 1", {'id': user_id})
    profil = cur.fetchone()
    age_num = str(age(profil[5]))
    description = profil[6]
    score = str(profil[8])
    is_online = profil[9]
    last_log = str(profil[10])
    if score == "None":
        score = str(0)
    genre = GENRE[profil[2]]
    orientation = ORIENTATION[profil[3]]

    cur.execute("SELECT blocked FROM accountcontrol WHERE from_user_id=%(sid)s AND to_user_id=%(rid)s LIMIT 1", {'sid': current_user.id, 'rid': user_id})
    is_user_block = cur.fetchone()
    if is_user_block is None:
        is_block = False
    else:
        is_block = is_user_block[0]
    cur.execute("SELECT COUNT(id) FROM likes WHERE sender_id=%(sid)s AND receiver_id=%(rid)s", {'sid': current_user.id, 'rid': user_id})
    like_send = cur.fetchone()[0]
    cur.execute("SELECT COUNT(id) FROM likes WHERE sender_id=%(sid)s AND receiver_id=%(rid)s", {'sid': user_id, 'rid': current_user.id})
    is_like = cur.fetchone()[0]
    if like_send == 1 and is_like == 1:
        like_message = "This is a match !"
    elif is_like == 1:
        like_message = "This person like you. Like back ?"
    else:
        like_message = ""

    #Add Visit or Update visit
    cur.execute("SELECT COUNT(id) FROM visites WHERE sender_id=%(sid)s AND receiver_id=%(rid)s", {'sid': current_user.id, 'rid': user_id})
    visit_send = cur.fetchone()[0]
    if visit_send == 0:
        cur.execute("INSERT INTO visites (sender_id, receiver_id) VALUES ('{0}', '{1}');".format(current_user.id , user_id))
        conn.commit()

    cur.execute("SELECT image_profil FROM profil WHERE user_id=%(id)s LIMIT 1", {'id': user_id})
    image_profil = cur.fetchone()
    if image_profil:
        image_profil_id = str(image_profil[0])
    cur.execute("SELECT id, path FROM images WHERE profil_id=%(id)s", {'id': user_id})
    all_images = cur.fetchall()
    for key, imgpth in all_images:
        images_path.append([key,create_presigned_url(current_app.config["S3_BUCKET"], imgpth)])
    total_img = len(images_path)
    if images_path != []:
        fav_image = images_path[int(image_profil_id)][1]
    else:
        fav_image = "0"
    cur.execute("SELECT interest_id::INTEGER FROM \"ProfilInterest\" WHERE user_id=%(id)s", {'id': user_id})
    interest = cur.fetchall()
    interest_list = []
    for id in interest:
        cur.execute("SELECT hashtag FROM \"Interest\" WHERE id=%(id)s LIMIT 1", {'id': id[0]})
        interest_list.append(cur.fetchone()[0].rstrip())
        print(interest_list)
    cur.execute("SELECT city FROM location WHERE id=%(id)s", {'id': profil[4]})
    localisation = cur.fetchone()[0]
    cur.close()
    conn.close()
    return render_template('show_profile.html', profil=profil,user_id=user_id, username=user_username ,name=user_name, age=age_num, score=score, desc=description, genre=genre, orientation=orientation,  interest_list=interest_list, localisation=localisation, image_profil=fav_image, images_path=images_path, total_img=total_img, is_online=is_online, last_log=last_log, is_block=is_block, like_send=like_send, like_message=like_message)


@main.route('/addlike', methods = ['POST'])
@login_required
@check_confirmed
def addlike():
    if request.method == 'POST':
        error = ""
        user_id = request.form['data']
        if user_id :
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT COUNT(*) FROM accountcontrol WHERE (from_user_id=%(id)s AND to_user_id=%(tid)s AND blocked = true) LIMIT 1", {'id': user_id, 'tid': current_user.id})
            is_block = cur.fetchone()[0]
            if is_block == 0:
                cur.execute("INSERT INTO likes (sender_id, receiver_id) VALUES ('{0}', '{1}');".format(current_user.id , user_id))
                conn.commit()
            else:
                error = "An error occur"
            cur.close()
            conn.close()


            return (error)
        else:
            return ("KO")

@main.route('/delnotif', methods = ['POST'])
@login_required
@check_confirmed
def delnotif():
    if request.method == 'POST':
        notif_id = int(request.form['notif'])
        if notif_id :
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("DELETE FROM notifications WHERE receiver_id='{0}' AND id='{1}';".format(current_user.id , notif_id))
            conn.commit()

            cur.close()
            conn.close()
            return (str(notif_id))
        else:
            return ("KO")



@main.route('/sendmessage', methods = ['POST'])
def sendmessage():
    if request.method == 'POST':
        receiver = request.form['receiver']
        msg = request.form['msg']
        #A FIX Check message format
        
        if msg and msg != '':

            conn = get_db_connection()
            cur = conn.cursor()
            #get receiver_id from username
            cur.execute("SELECT id FROM users WHERE username='{0}';".format(receiver))
            receiver_id = cur.fetchone()[0]
            print(receiver_id)
            
            msg_time = float(datetime.now().timestamp())

            # create a new message
            cur.execute("INSERT INTO messages (sender_id, receiver_id, msg, date_added) VALUES ('{0}', '{1}', '{2}', '{3}');".format(current_user.id , receiver_id, msg, msg_time))
            conn.commit()
            cur.execute("SELECT id, date_added FROM messages WHERE sender_id='{0}' AND receiver_id='{1}' AND msg='{2}' AND date_added='{3}' LIMIT 1;".format(current_user.id , receiver_id, msg, msg_time))
            msg_row = cur.fetchone()
            msg_id = msg_row[0]
            msg_date = msg_row[1]

            # add the new user to the database
            cur.close()
            conn.close()

            return {
                'msg': msg,
                'date': msg_date,
                'receiver_id': receiver_id,
                'msg_id' : msg_id
            }
        else:
            return ("KO")

            

@main.route('/dellike', methods = ['POST'])
@login_required
@check_confirmed
def dellike():
    if request.method == 'POST':
        user_id = request.form['data']
        if user_id :
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM likes WHERE sender_id='{0}' AND receiver_id='{1}';".format(current_user.id , user_id))
            conn.commit()

            cur.close()
            conn.close()
            return (user_id)
        else:
            return ("KO")

@main.route('/block', methods = ['POST'])
@login_required
@check_confirmed
def block():
    if request.method == 'POST':
        user_id = request.form['data']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT to_user_id FROM accountcontrol WHERE (to_user_id=%(id)s AND blocked = true) LIMIT 1", {'id': user_id})
        to_user_id = cur.fetchone()
        if to_user_id != None:
            to_user_id = to_user_id[0]
        if user_id and str(to_user_id) != str(user_id):
            cur.execute("SELECT COUNT(to_user_id) FROM accountcontrol WHERE (to_user_id=%(id)s AND from_user_id = %(from)s) LIMIT 1", {'id': user_id, 'from': current_user.id})
            if cur.fetchone()[0]==0:
                cur.execute("INSERT INTO accountcontrol (blocked, fake, from_user_id, to_user_id) VALUES (true, false, %(from)s, %(to)s)", {'from': current_user.id, 'to': user_id})
                conn.commit()
            else:
                cur.execute("UPDATE accountcontrol SET blocked='true' WHERE from_user_id=%(from)s AND to_user_id=%(to)s", {'from': current_user.id, 'to': user_id})
                conn.commit()
            cur.close()
            conn.close()
            flash('The user has been blocked')
            return (user_id)
        else:
            cur.close()
            conn.close()
            flash('The user is already blocked')
            return ("KO")

@main.route('/unblock', methods = ['POST'])
@login_required
@check_confirmed
def unblock():
    if request.method == 'POST':
        user_id = request.form['data']
        conn = get_db_connection()
        cur = conn.cursor()  
        try:
            cur.execute("UPDATE accountcontrol SET blocked=false WHERE (from_user_id=%(user)s AND to_user_id=%(id)s AND blocked = true)", {'user': current_user.id, 'id': user_id})
            conn.commit()
            cur.close()
            conn.close()
            flash('The user has been unblocked')
            return (user_id)
        except: 
            flash('Issue while unblocking user, try again later')
            cur.close()
            conn.close()
            return ("KO")

@main.route('/report', methods = ['POST'])
@login_required
@check_confirmed
def report():
    if request.method == 'POST':
        user_id = request.form['data']
        conn = get_db_connection()
        cur = conn.cursor()  
        cur.execute("SELECT COUNT(to_user_id) FROM accountcontrol WHERE (to_user_id=%(id)s AND fake = true) LIMIT 1", {'id': user_id})
        to_user_id = cur.fetchone()[0]
        if user_id and to_user_id==0:
            cur.execute("SELECT COUNT(to_user_id) FROM accountcontrol WHERE (to_user_id=%(id)s AND from_user_id = %(from)s) LIMIT 1", {'id': user_id, 'from': current_user.id})
            if cur.fetchone()[0]==0:
                cur.execute("INSERT INTO accountcontrol (blocked, fake, from_user_id, to_user_id) VALUES (false, true, %(from)s, %(to)s)", {'from': current_user.id, 'to': user_id})
                conn.commit()
            else:
                cur.execute("UPDATE accountcontrol SET fake='true' WHERE from_user_id=%(from)s AND to_user_id=%(to)s", {'from': current_user.id, 'to': user_id})
                conn.commit()
            cur.close()
            conn.close()
            flash('The user has been reported')
            return (user_id)
        else:
            cur.close()
            conn.close()
            flash('The user is already reported')
            return (user_id)

# edit profile page that return 'edit-profile'
@main.route('/edit-profile') 
@login_required
@check_confirmed
def editprofile():
    image_path = dict()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT image_profil FROM profil WHERE user_id=%(id)s LIMIT 1", {'id': current_user.id})
    image_profil = cur.fetchone()
    if image_profil != None:
        image_profil_id = str(image_profil[0])
    print(image_profil_id)
    cur.execute("SELECT id, path FROM images WHERE profil_id=%(id)s", {'id': current_user.id})
    all_images = cur.fetchall()
    print(all_images)
    if all_images != []:
        fav_image = all_images[int(image_profil_id)][0]
    else:
        fav_image = None
    cur.execute("SELECT bio, genre_id, orientation_id FROM profil WHERE user_id=%(id)s LIMIT 1", {'id': current_user.id})
    i_am = cur.fetchone()
    i_am_bio = str(i_am[0])
    i_am_genre = GENRE[i_am[1]]
    i_am_orientation = ORIENTATION[i_am[2]]
    print(i_am)
    cur.execute("SELECT interest_id::INTEGER FROM \"ProfilInterest\" WHERE user_id=%(id)s", {'id': current_user.id})
    interest = cur.fetchall()
    interest_list = []
    for id in interest:
        cur.execute("SELECT hashtag FROM \"Interest\" WHERE id=%(id)s LIMIT 1", {'id': id[0]})
        interest_list.append(cur.fetchone()[0].rstrip())
    cur.execute("SELECT * FROM \"Interest\";")
    full_interest = cur.fetchall()
    cur.close()
    conn.close()
    for key, imgpth in all_images:
        image_path[str(key)] = create_presigned_url(current_app.config["S3_BUCKET"], imgpth)
    total_img = len(image_path)
    if total_img != 5:
        image_path['default'] = create_presigned_url(current_app.config["S3_BUCKET"],"test/no-photo.png")
    return render_template('edit-profile.html', image_profil=str(fav_image), images_urls=image_path, total_img=total_img, interest=interest_list, bio=i_am_bio, genre=i_am_genre, orientation=i_am_orientation, full_interest=full_interest)

@main.route('/uploadajax', methods = ['POST'])
@login_required
@check_confirmed
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
            #check if total image < 5    
            cur.execute("SELECT COUNT(*) FROM images WHERE profil_id=(SELECT id FROM profil WHERE user_id=%(id)s);", { 'id': current_user.id})
            if cur.fetchone()[0] < 5:
                cur.execute("INSERT INTO images (title, path, profil_id, date_added) VALUES (%(title)s, %(path)s, %(profil_id)s, %(date_added)s)", {'title': file1.filename, 'path': file_path, 'profil_id': current_user.id, 'date_added': date.today()})
                conn.commit()
            cur.close()
            conn.close()
            return ("OK")
        else:
            return ("KO")

@main.route('/setimageprofil', methods = ['POST'])
@login_required
@check_confirmed
def setimgprofil():
    if request.method == 'POST':
        img_id = request.form['data']
        print(img_id)
        if img_id :
            order = []
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM images WHERE profil_id=%(id)s", {'id': current_user.id})
            all_images = cur.fetchall()
            print(all_images)
            for i in all_images:
                order.append(int(i[0]))
            print(order)
            position = order.index(int(img_id))
            print(position)
            cur.execute("UPDATE profil SET image_profil=%(fav)s WHERE user_id=%(id)s", {'fav': position, 'id': current_user.id})
            cur.execute("UPDATE profil SET image_profil_id=%(fav)s WHERE user_id=%(id)s", {'fav': img_id, 'id': current_user.id})
            conn.commit()
            cur.close()
            return ("success")
        else:
            return ("KO")

@main.route('/deleteimage', methods = ['POST'])
@login_required
@check_confirmed
def delimg():
    if request.method == 'POST':
        img_id = request.form['data']
        if img_id :
            return (img_id)
        else:
            return ("KO")

        

@main.route('/updatebio', methods = ['POST'])
@login_required
@check_confirmed
def updbio():
    if request.method == 'POST':
        if 'newBio' not in request.form:
            flash('There is no bio')
            return ("KO")
        bio = request.form['newBio']
        if bio :
            bio = bio.replace("'", "`")
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE profil SET bio=%(bio)s WHERE user_id=%(id)s", {'bio': bio, 'id': current_user.id})
            conn.commit()
            cur.close()
            return (bio)
        else:
            return ("KO")

@main.route('/updateprimary', methods = ['POST'])
@login_required
@check_confirmed
def updprim():
    if request.method == 'POST':
        if 'newGender' not in request.form:
            flash('There is no gender')
            return ("KO")
        gender = request.form['newGender']
        orient = request.form['newOrient']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE profil SET genre_id=%(genre)s, orientation_id=%(orientation)s WHERE user_id=%(id)s", {'genre': gender, 'orientation': orient, 'id': current_user.id})
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
@login_required
@check_confirmed
def updhash():
    if request.method == 'POST':
        hash_id = request.form.getlist("check")
        existing_list = []
        if (hash_id):
            conn = get_db_connection()
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM \"ProfilInterest\" WHERE user_id=%(id)s", {'id': current_user.id})
            except: 
                print("no hash  for the user")
            for i in hash_id:
                cur.execute("INSERT INTO \"ProfilInterest\" (user_id, interest_id) VALUES (%(id)s, %(int)s)", {'id': current_user.id, 'int': i})
                conn.commit()
            for id in hash_id:
                cur.execute("SELECT hashtag FROM \"Interest\" WHERE id=%(id)s LIMIT 1", {'id': id})
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
@check_confirmed
def account():
    onglet = None
    section = 'like'
    blocked_list = []
    likes_list = []
    views_list = []
    conn = get_db_connection()
    cur = conn.cursor()

    # Current user profil gesture
    cur.execute("SELECT * FROM profil WHERE user_id=%(id)s LIMIT 1", {'id': current_user.id})
    profil = cur.fetchone()
    cur.execute("SELECT city FROM location WHERE id=%(id)s", {'id': profil[4]})
    localisation = cur.fetchone()[0]
    username = current_user.username
    email = current_user.email
    firstname = current_user.firstname
    lastname = current_user.lastname
    birthdate = profil[5]
    cur.execute("SELECT bio FROM profil WHERE user_id=%(id)s LIMIT 1", {'id': current_user.id})
    bio = cur.fetchone()[0]
    is_bio = 0
    if bio != '':
        is_bio = 1
    cur.execute("SELECT image_profil FROM profil WHERE user_id=%(id)s", {'id': current_user.id})
    image_profil = cur.fetchone()[0]
    cur.execute("SELECT id, path FROM images WHERE profil_id=%(id)s", {'id': current_user.id})
    all_images = cur.fetchall()
    if all_images != []:
        fav_image = all_images[int(image_profil)][1]
    else:
        fav_image = None
    if fav_image :
        image_profil_path = create_presigned_url(current_app.config["S3_BUCKET"], fav_image)
    else :
        image_profil_path = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
    
    # Select blocked user_id
    cur.execute("SELECT to_user_id from accountcontrol WHERE from_user_id=%(id)s and blocked=true;", {'id':current_user.id})
    blocked_users=cur.fetchall()
    for i in blocked_users:
        cur.execute("SELECT id, username from users where users.id=%(id)s LIMIT 1;", {'id': i})
        blocked_profil = cur.fetchone()
        blocked_list.append([blocked_profil[0], blocked_profil[1]])
  
    #set blocked_list for views and likes + exclude current_user
    blocked_string = str(current_user.id)+','.join([str(elem[0]) for elem in blocked_users])
    # Select Like user_id
    cur.execute("SELECT sender_id FROM likes WHERE receiver_id='{0}' AND sender_id NOT IN ({1});".format(current_user.id, blocked_string))
    like_users=cur.fetchall()
    for i in like_users:
        cur.execute("SELECT users.id, username, age, city FROM users INNER JOIN profil ON users.id = profil.user_id AND users.id=%(id)s LEFT JOIN location ON  profil.location_id = location.id LIMIT 1;", {'id': i})
        like_profil = cur.fetchone()
        #calc age
        user_age = age(like_profil[2])
        #did i like this person ? 
        cur.execute("SELECT COUNT(id) FROM likes WHERE sender_id=%(sid)s AND receiver_id=%(rid)s", {'sid': current_user.id, 'rid': like_profil[0]})
        is_like = cur.fetchone()[0]
        likes_list.append([like_profil[0], like_profil[1], user_age, like_profil[3], is_like])
    # Select visites user_id

    #cur.execute("INSERT INTO notifications (sender_id, receiver_id, notif_type, content, date_added) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}');".format(current_user.id, receiver_id, notif_type, content, notif_date))
    cur.execute("SELECT sender_id FROM visites WHERE receiver_id='{0}' AND sender_id NOT IN ({1});".format(current_user.id, blocked_string))
    visite_users=cur.fetchall()
    for i in visite_users:
        cur.execute("SELECT users.id, username, age, city FROM users INNER JOIN profil ON users.id = profil.user_id AND users.id=%(id)s LEFT JOIN location ON  profil.location_id = location.id LIMIT 1;", {'id': i})
        visite_profil = cur.fetchone()
        #calc age
        user_age = age(like_profil[2])
        #did i like this person ? 
        cur.execute("SELECT COUNT(id) FROM likes WHERE sender_id=%(sid)s AND receiver_id=%(rid)s", {'sid': current_user.id, 'rid': like_profil[0]})
        is_like = cur.fetchone()[0]
        views_list.append([visite_profil[0], visite_profil[1], user_age, visite_profil[3], is_like])
    
    if request.method=='GET':
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('main.index'))
        if request.args.get('onglet') != None :
            onglet = request.args.get('onglet')
        if request.args.get('section') != None :
            section = request.args.get('section')
        return render_template('account.html', username=username, email=email, firstname=firstname, lastname=lastname, localisation=localisation, image_profil=image_profil_path, onglet=onglet, section=section, blocked_list=blocked_list,likes_list=likes_list, views_list=views_list, is_bio=is_bio, birthdate=birthdate)
    else:
        if 'deletemyaccount' in request.form:
            officialdelete = request.form.get('deletemyaccount')
            if str(officialdelete) == "Delete my account now":
                cur.execute("DELETE FROM \"ProfilInterest\" USING users WHERE user_id =%(id)s", {'id': current_user.id})
                cur.execute("DELETE FROM images USING users WHERE profil_id =%(id)s", {'id': current_user.id})
                cur.execute("DELETE FROM profil USING users WHERE user_id =%(id)s", {'id': current_user.id})
                cur.execute("DELETE FROM users WHERE id =%(id)s", {'id': current_user.id})
                logout_user()
                conn.commit()
                cur.close()
                conn.close()
                flash('Your account is now deleted', 'warning')
                return redirect(url_for('main.index'))
            else:
                flash('There was an error  while deleting your account, try again!', 'warning')
                return redirect(url_for('main.account'))

        if 'username' in request.form:
            if current_user.confirmed is False:
                flash('Please confirm your account!', 'warning')
                return redirect(url_for('main.index'))
            firstname1 = request.form.get('first_name')
            lastname1 = request.form.get('last_name')
            username1 = request.form.get('username')
            birthdate1 = request.form.get('birthdate')
            localisation1 = request.form.get('location')
            cur.execute("SELECT * FROM users WHERE username=%(username)s", {'username': username1})
            username_check = cur.fetchall()
            if username1 != "" and username_check != []:
                flash('User Name address already exists')
            elif username1 != "":
                cur.execute("UPDATE users SET username = %(username)s WHERE id=%(id)s", {'username': username1, 'id': current_user.id})
                conn.commit()
                username = username1
            if firstname1 != "":
                cur.execute("UPDATE users SET first_name = %(firstname)s WHERE id=%(id)s", {'firstname': firstname1, 'id': current_user.id})
                conn.commit()
                firstname = firstname1           
            if lastname1 != "":
                cur.execute("UPDATE users SET last_name = %(lastname)s WHERE id=%(id)s", {'lastname': lastname1, 'id': current_user.id})
                conn.commit()
                lastname = lastname1  
            if birthdate1 != "":
                cur.execute("UPDATE profil SET age = %(birthdate)s WHERE user_id=%(id)s", {'birthdate': birthdate1, 'id': current_user.id})
                birthdate = birthdate1    
            if localisation1 != "":
                lat, lont, display_loc = localize_text(str(localisation1))
                today = date.today()
                if  display_loc != "ERROR - WRONG LOCALISATION":
                    cur.execute("UPDATE location SET latitude = %(lat)s, longitude = %(long)s, date_modif = %(date)s, city = %(city)s WHERE id=%(id)s", {'lat': lat, 'long': lont, 'date': today, 'city': display_loc.strip(),'id': profil[4]})
                    conn.commit()
                    localisation = display_loc
                else:
                    flash('New location not found')
        elif 'oldpassword' in request.form:
            if current_user.confirmed is False:
                flash('Please confirm your account!', 'warning')
                return redirect(url_for('main.index'))
            else:
                oldpassword = request.form.get('oldpassword')
                password1 = request.form.get('password1')
                password2 = request.form.get('password2')
                cur.execute("SELECT * FROM users WHERE id=%(id)s LIMIT 1", {'id': current_user.id})
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
                    cur.execute("UPDATE users SET password = crypt(%(pwd)s, gen_salt('bf')) WHERE id=%(id)s", {'pwd':password1, 'id': current_user.id})
                    conn.commit()
                    flash('password updated', 'success')
        elif 'email' in request.form:
            email1 = request.form.get('email')
            cur.execute("SELECT * FROM users WHERE email=%(email)s", {'email': email1})
            email_check = cur.fetchall()
            email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if email1 != "" and email_check == [] and re.fullmatch(email_regex, email):
                #cur.execute("UPDATE users SET email = '{0}', confirmed = false WHERE id='{1}';".format(email1,current_user.id))
                cur.execute("UPDATE users SET email = %(email)s,  confirmed = false WHERE id=%(id)s", {'email':email1, 'id': current_user.id})
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

        return render_template('account.html', username=username, email=email, firstname=firstname, lastname=lastname, localisation=localisation, image_profil=image_profil_path, section=section, onglet=onglet, blocked_list=blocked_list,likes_list=likes_list, views_list=views_list, is_bio=is_bio, birthdate=birthdate)


# match page that return 'match'
@main.route('/match')
@login_required
@check_confirmed
def match():
    return render_template('match.html')


# chat page that return 'match'
@main.route('/chat') 
@login_required
@check_confirmed
def chat():

    usersList = [] 
    matchList = []
    roomsList = []
    messagesList = []
    notifList = []
    onlineList = []

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT receiver_id FROM likes WHERE sender_id={0};".format(current_user.id))
    like_list = cur.fetchall()
    for i in like_list:
        cur.execute("SELECT COUNT(id) FROM likes WHERE sender_id='{0}' AND receiver_id='{1}';".format(i[0], current_user.id))
        if cur.fetchone()[0] > 0:
            matchList.append(i[0])
    for i in matchList:
        cur.execute("SELECT username FROM users WHERE id='{0}';".format(i))
        usersList.append(cur.fetchone()[0])
        cur.execute("SELECT is_online FROM profil WHERE user_id='{0}';".format(i))
        onlineList.append(cur.fetchone()[0])
        cur.execute("SELECT * FROM messages WHERE (sender_id='{0}' AND receiver_id='{1}') OR (sender_id='{1}' AND receiver_id='{0}') ORDER BY date_added ASC;".format(current_user.id, i))
        messages = cur.fetchall()
        messagesList.append(messages)
        cur.execute("SELECT COUNT(id) FROM notifications WHERE receiver_id=%(id)s AND notif_type=2 AND is_read=false AND sender_id=%(sid)s;", {'id': current_user.id, 'sid': i})
        notifList.append(cur.fetchone()[0])

    cur.close()
    conn.close()
    for u in usersList:
        if current_user.username < u :
            roomsList.append(current_user.username+u)
        else :
            roomsList.append(u+current_user.username)

    return render_template('chat.html', sync_mode=socketio.async_mode, usersList=usersList, usersListSize=len(usersList), roomsList=roomsList, messagesList=messagesList, current_user=current_user.id, onlineList=onlineList, notifList=notifList)

# notification page that return 'notification'
@main.route('/notification') 
@login_required
@check_confirmed
def notification():

    notifList = [] 
    elem = []
    message = ""
    #username / message (selon type) / type / date / notif_id

    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM notifications where receiver_id=%(id)s ORDER BY date_added DESC ;", {'id': current_user.id})
    notifications = cur.fetchall()
    for notif in notifications:
        notif_id = notif[0]
        notif_type = notif[3]
        content = notif[4]
        date = datetime.fromtimestamp(notif[6]).strftime('%d/%m-%H:%M:%S')
        is_read = notif[5]
        cur.execute("SELECT username FROM users where id=%(id)s LIMIT 1;", {'id': notif[1]})
        username = cur.fetchone()[0]
        #like
        if notif_type == 0:
            if content == 1:
                message = "like you"
            else:
                message = "doesn't like you anymore"
        #view
        if notif_type == 1:
            message = "looked at your profil"
        #messages
        if notif_type == 2:
            message = "send you a message"

        elem = [notif_id, notif_type, date, username, message, is_read]
        notifList.append(elem)
    cur.close()
    conn.close()

    return render_template('notification.html', notifications=notifList)


@main.route('/trisearch', methods = ['POST'])
@login_required
@check_confirmed
def trisearch():
    sort = []
    if request.method == 'POST':
        print(request.form.get('ageCheck'))
        print(request.form.get('ageCheckOrder'))
        print(request.form.get('distCheck'))
        print(request.form.get('distCheckOrder'))
        print(request.form.get('scoreCheck'))
        print(request.form.get('scoreCheckOrder'))
        print(request.form.get('hashtagCheck'))
        print(request.form.get('hashtagCheckOrder'))
        if request.form.get('ageCheck') == "on":
            if request.form.get('ageCheckOrder') == "on":
                sort.append(["age", "+"])
            else:
                sort.append(["age", "-"])
        if request.form.get('distCheck') == "on":
            if request.form.get('distCheckOrder') == "on":
                sort.append(["dist", "+"])
            else:
                sort.append(["dist", "-"])
        if request.form.get('scoreCheck') == "on":
            if request.form.get('scoreCheckOrder') == "on":
                sort.append(["score", "+"])
            else:
                sort.append(["score", "-"])
        if request.form.get('hashtagCheck') == "on":
            if request.form.get('hashtagCheckOrder') == "on":
                sort.append(["hashtag", "+"])
            else:
                sort.append(["hashtag", "-"])
    print(sort)
    blacklisted_list = []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, username FROM users LIMIT 50;")
    profil_list = cur.fetchall()
    cur.execute("SELECT to_user_id FROM accountcontrol WHERE (from_user_id=%(id)s AND blocked = true)", {'id': current_user.id})
    blacklisted_elems = cur.fetchall()
    for i in blacklisted_elems:
        cur.execute("SELECT id, first_name, username FROM users where id=%(id)s LIMIT 1;", {'id': i[0]})
        blacklisted_list.append(cur.fetchone())
    print(profil_list)
    print(blacklisted_list)
    print(len(profil_list))
    profil_list = [x for x in profil_list if x not in blacklisted_list]
    profil_list = [x for x in profil_list if x not in blacklisted_list]
    print(len(profil_list))
    final_users = []
    cur.execute("SELECT * FROM \"Interest\";")
    full_interest = cur.fetchall()
    for user in profil_list:
        if user[0] != current_user.id:
            cur.execute("SELECT image_profil, age, location_id, score FROM profil WHERE user_id=%(id)s LIMIT 1", {'id': user[0]})
            user_details = cur.fetchone()
            #print(user[0])
            #print(user_details)
            if user_details != None:
                image_profil = user_details[0]
                #print(image_profil)
                cur.execute("SELECT id, path FROM images WHERE profil_id=%(id)s", {'id': user[0]})
                all_images = cur.fetchall()
                try:
                    fav_image = all_images[int(image_profil)][1]

                except:
                    all_images.append([0, 'test/no-photo.png']) 
                    all_images.append([1, 'test/no-photo.png'])
                    all_images.append([2, 'test/no-photo.png'])
                    all_images.append([3, 'test/no-photo.png'])
                    all_images.append([4, 'test/no-photo.png'])
                    fav_image = all_images[int(image_profil)][1]
                #print("all_images")
                #print(all_images)
                #print(fav_image)
                if fav_image:
                    image_profil_path = create_presigned_url(current_app.config["S3_BUCKET"], fav_image)
                else :
                    image_profil_path = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
                user_age = str(age(user_details[1]))
                cur.execute("SELECT city FROM location WHERE id=%(id)s LIMIT 1", {'id': user_details[2]})
                user_location = cur.fetchone()[0]
                final_users.append([user[1], user_age, user_location, image_profil_path, user[2], user_details[3]])
                #print(len(final_users))
    #print(profil_list)
    cur.close()
    conn.close()
    for elem in sort:
        if elem[0] == "age" and elem[1] == "+":
            final_users = sorted(final_users, key=lambda tup: tup[1], reverse=False)
        elif elem[0] == "age" and elem[1] == "-":
            final_users = sorted(final_users, key=lambda tup: tup[1], reverse=True)
        if elem[0] == "dist" and elem[1] == "+":
            final_users = sorted(final_users, key=lambda tup: tup[2], reverse=False)
        elif elem[0] == "dist" and elem[1] == "-":
            final_users == final_users.sort(key=lambda tup: tup[2], reverse=True)
        if elem[0] == "score" and elem[1] == "+":
            final_users = sorted(final_users, key=lambda tup: tup[3], reverse=False)
        elif elem[0] == "score" and elem[1] == "-":
            final_users = sorted(final_users, key=lambda tup: tup[3], reverse=True)
        #if elem[0] = "hashtag" and elem[1] ="+":
        #    final_users = sorted(final_users, key=lambda tup: tup[1], reverse=False)
        #elif elem[0] = "hashtag" and elem[1] ="-":
        #    final_users = sorted(final_users, key=lambda tup: tup[1], reverse=True)
    print(final_users)

    return {
        'all_users': final_users,
        'full_interest': full_interest
    }
    #return render_template('research.html', all_users = final_users, user_num=len(final_users), full_interest=full_interest)

    
# New Search thet return 'search'
@main.route('/research', methods=['GET', 'POST'])
@main.route('/research/page/<int:page>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def research(page=1):
    final_users = []
    conn = get_db_connection()
    cur = conn.cursor()
    #Page doit être > 0 car offset ne prend pas de négatif
    if int(page) < 1:
        page = 1
    offset = (page - 1) * OFFSET
    # Select blocked user_id
    cur.execute("SELECT to_user_id from accountcontrol WHERE from_user_id=%(id)s and blocked=true;", {'id':current_user.id})
    blocked_users=cur.fetchall()
    blocked_list = ','.join([str(elem[0]) for elem in blocked_users])
    if blocked_list != '':
        blocked_list = str(current_user.id) + ','+ blocked_list
    else:
        blocked_list = str(current_user.id)
    # Select list of all interests
    cur.execute("SELECT * FROM \"Interest\";")
    full_interest = cur.fetchall()
    #Select right Gender
    cur.execute("SELECT genre_id, orientation_id FROM profil WHERE user_id=%(id)s LIMIT 1;", {'id': current_user.id})
    user_details = cur.fetchone()
    print(user_details)
    # Si l'user est un homme
    if user_details[0] == 1:
        # Si l'user est Hetero
        if user_details[1] == 1:
            #select femme et (hetero ou bi) ou non-binaire  A
            select_gender = "AND (p.genre_id=2 AND (p.orientation_id=1 or p.orientation_id=0) OR p.genre_id=0)"
        #si user est un homme gay
        elif user_details[1] == 2:
            #select homme et (gay ou bi) ou non binaire  B
            select_gender = "AND (p.genre_id=1 AND (p.orientation_id=0 or p.orientation_id=2) OR p.genre_id=0)"
        #si user est un homme bi
        elif user_details[1] == 0:
            #select homme et (gay ou bi) ou femme et (hetero ou bi) ou non binaire  B + A
            select_gender = "AND (p.genre_id=1 AND (p.orientation_id=0 or p.orientation_id=2) OR p.genre_id=2 AND (p.orientation_id=1 or p.orientation_id=0) OR p.genre_id=0)"
    elif user_details[0] == 2:
        #si user est une femme et hetero
        if user_details[1] == 1:
            #select homme et (hetero ou bi) ou non-binaire C
            select_gender = "AND (p.genre_id=1 AND (p.orientation_id=1 or p.orientation_id=0) OR p.genre_id=0)"
        #si user est une femme et gay
        elif user_details[1] == 2:
            #select femme et (gay ou bi) ou non-binaire D
            select_gender = "AND (p.genre_id=2 AND (p.orientation_id=0 or p.orientation_id=2) OR p.genre_id=0)"
        #si user est une femme et bi
        elif user_details[1] == 0:
            #select homme et (hetero ou bi) ou femme et (gay ou bi) ou non-binaire C + D
            select_gender = "AND (p.genre_id=1 AND (p.orientation_id=0 or p.orientation_id=2) OR p.genre_id=2 AND (p.orientation_id=1 or p.orientation_id=0) OR p.genre_id=0)"
    #si user est non-binaire et hetero
    elif user_details[1] == 1:
        #select homme et femme hetero
        select_gender = "AND p.orientation_id=1"
    #si user est non-binaire gay
    elif user_details[1] == 2:
        #select homme et femme gay
        select_gender = "AND p.orientation_id=2"
    #si user est non-binaire et bi
    elif user_details[1] == 0:
        #select all
        select_gender=""

    # On GET Return All Users except block and current
    if request.method=='GET':
        user_age = 18
        # Get number of pages
        cur.execute("SELECT COUNT(id) FROM search WHERE user_id='{0}' AND list_id NOT IN ({1}) ;".format(current_user.id, blocked_list))
        total_users = cur.fetchone()[0]
        if total_users > 0:                       
            cur.execute("SELECT list_id FROM search WHERE user_id='{0}' AND list_id NOT IN ({1}) ORDER BY id desc LIMIT '{2}' OFFSET '{3}';".format(current_user.id, blocked_list, OFFSET, offset))
            profil_list = cur.fetchall()
        else:
            cur.execute("SELECT COUNT(users.id) FROM users INNER JOIN profil p on users.id=p.user_id AND users.id NOT IN ({0}) {1};".format(blocked_list, select_gender))
            total_users = cur.fetchone()[0]
            print("Ma super selection on GENDER")
            # Select all user from page=page except blocked ones
            cur.execute("SELECT users.id FROM users INNER JOIN profil p on users.id=p.user_id AND users.id NOT IN ({0}) {1} ORDER BY p.genre_id desc, p.last_log desc LIMIT '{2}' OFFSET '{3}';".format(blocked_list, select_gender, OFFSET, offset))
            profil_list = cur.fetchall()
        max_page = int((total_users/OFFSET)+1)
        if ((total_users % OFFSET) > 0) :
            max_page+1
        for user in profil_list:
            cur.execute("SELECT users.id, username, age, city FROM users INNER JOIN profil ON users.id = profil.user_id AND users.id=%(id)s LEFT JOIN location ON  profil.location_id = location.id LIMIT 1", {'id': user})
            user_details = cur.fetchone()
            #calc age
            if user_details:
                user_age = age(user_details[2])
                final_users.append([user_details[0], user_details[1], user_age, user_details[3]])
        cur.close()
        conn.close()
        return render_template('research.html', max_page=max_page, current_page=page, all_users = final_users, user_num=total_users, full_interest=full_interest)
    # On POST return Users that match Search Inputs
    if request.method=='POST':
        if 'ageMinSearch' in request.form:
            ageMinSearch = request.form.get('ageMinSearch')
            ageMaxSearch = request.form.get('ageMaxSearch')
            citySearch = request.form.get('citySearch')
            locRangeSearch = request.form.get('locRangeSearch')
            scoreMinSearch = request.form.get('scoreMinSearch')
            scoreMaxSearch = request.form.get('scoreMaxSearch')
            hashtags_id = request.form.getlist('searchcheck') 
            hashtag_user_list = []
            #to meter#
            #locRangeSearch = int(locRangeSearch)
            print("locRange:"+locRangeSearch)
            # Prepare Select Qwery
            select_stmt = " FROM profil WHERE user_id NOT IN ("+blocked_list+")"
            data = {}
            #Age qwery
            if ageMinSearch != '' and ageMaxSearch != '':
                #before#
                ageMinComp = age_period(ageMinSearch)
                #after#
                ageMaxComp = age_period(ageMaxSearch)
                select_stmt = select_stmt+" AND age between %(amax)s and %(amin)s"
                data['amax'] = ageMaxComp
                data['amin'] = ageMinComp
            #Score qwery
            if scoreMinSearch != '' and scoreMaxSearch != '':
                scoreMinSearch = int(scoreMinSearch)
                scoreMaxSearch = int(scoreMaxSearch)
                select_stmt = select_stmt+" AND score between %(smin)s and %(smax)s"
                data['smin'] = scoreMinSearch
                data['smax'] = scoreMaxSearch
            #Location qwery
                #locRangeSearch
            #if citySearch != '':
                #cur.execute("SELECT city from ")

            #Hashtags qwery
            if hashtags_id and hashtags_id[0] != '':
                cur.execute("SELECT user_id FROM \"ProfilInterest\" WHERE interest_id=%(int1)s", {'int1': hashtags_id[0]})
                hashtags_users_list = cur.fetchall()
                for user in hashtags_users_list:
                    exclude=0
                    for hashtag_id in hashtags_id:
                        cur.execute("SELECT COUNT(user_id) FROM \"ProfilInterest\" WHERE interest_id=%(int)s AND user_id=%(uid)s", {'int': hashtag_id, 'uid': user})
                        is_tag = cur.fetchone()[0]
                        if ( is_tag == 0):
                            exclude = exclude+1
                    if exclude == 0:
                        hashtag_user_list.append(user)
                hashtag_user_list_str = ','.join([str(elem[0]) for elem in hashtag_user_list])
                select_stmt = select_stmt+" AND user_id IN ("+hashtag_user_list_str+")"
            # Get number of pages
            get_page_qwery = "SELECT COUNT(id)" + select_stmt
            cur.execute(get_page_qwery, data)
            user_num = cur.fetchone()[0]
            max_page = int((user_num/OFFSET)+1)
            if ((user_num % OFFSET) > 0) :
                max_page+1
            #Final qwery
            select_stmt = "SELECT user_id" + select_stmt
            select_all = select_stmt + "ORDER BY last_log desc;"
            cur.execute(select_stmt, data)
            all_profil_list = cur.fetchall()

            #SET current search List
            #cur.execute("SELECT COUNT(id) FROM search WHERE user_id=%(id)s", {'id': current_user.id})
            #if cur.fetchone()[0]==0:                     
            #    cur.execute("INSERT INTO search (user_id, list) VALUES ('{0}', '{1}')".format(current_user.id, search_list)) 
            #    conn.commit()
            #else:
            #    cur.execute("UPDATE search SET list=%(l)s WHERE user_id=%(id)s", {'l': search_list, 'id': current_user.id})
            #    conn.commit()
            cur.execute("DELETE FROM search WHERE user_id = %(id)s", {'id': current_user.id})
            for user in all_profil_list:
                cur.execute("INSERT INTO search (user_id, list_id) VALUES (%(id)s, %(lid)s)", {'id': current_user.id, 'lid': user})
                conn.commit()
            # Get Final UserList
            select_stmt = select_stmt + " ORDER BY last_log desc LIMIT 20 OFFSET %(offs)s;"
            data['offs'] = offset
            cur.execute(select_stmt, data)
            profil_list = cur.fetchall()
            for user in profil_list:
                cur.execute("SELECT users.id, username, age, city FROM users INNER JOIN profil ON users.id = profil.user_id AND users.id=%(id)s LEFT JOIN location ON  profil.location_id = location.id LIMIT 1", {'id': user})
                user_details = cur.fetchone()
                #calc age
                user_age = age(user_details[2])
                final_users.append([user_details[0], user_details[1], user_age, user_details[3]])
    cur.close()
    conn.close()
    return render_template('research.html', max_page=max_page, current_page=page, all_users = final_users, user_num=user_num, full_interest=full_interest)



# search page that return 'search'
@main.route('/search', methods=['GET', 'POST'])
@login_required
@check_confirmed
def search():
    blacklisted_list = []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, first_name, username FROM users LIMIT 30;")
    profil_list = cur.fetchall()
    cur.execute("SELECT to_user_id FROM accountcontrol WHERE (from_user_id=%(id)s AND blocked = true)", {'id': current_user.id})
    blacklisted_elems = cur.fetchall()
    for i in blacklisted_elems:
        cur.execute("SELECT id, first_name, username FROM users where id=%(id)s LIMIT 1", {'id': i[0]})
        blacklisted_list.append(cur.fetchone())
    print(profil_list)
    print(blacklisted_list)
    print(len(profil_list))
    profil_list = [x for x in profil_list if x not in blacklisted_list]
    print(len(profil_list))
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
                cur.execute("SELECT user_id FROM profil WHERE age between %(max)s and %(min)s AND score between %(smin)s and %(smax)s", {'max': ageMaxComp, 'min': ageMinComp, 'smin': int(scoreMinSearch), 'smax': int(scoreMaxSearch)})
                profil_list_id = cur.fetchall()
                print(profil_list)
                for i in profil_list_id:
                    cur.execute("SELECT id, first_name, username FROM users where id=%(id)s LIMIT 1", {'id': i[0]})
                    if i[0] != current_user.id:
                        profil_list.append(cur.fetchone())
            else:
                cur.execute("SELECT user_id, location_id FROM profil WHERE age between  %(max)s and %(min)s AND score between %(smin)s and %(smax)s", {'max': ageMaxComp, 'min': ageMinComp, 'smin': int(scoreMinSearch), 'smax': int(scoreMaxSearch)})
                profil_list_id = cur.fetchall()
                cur.execute("SELECT location_id FROM profil WHERE user_id = %(id)s LIMIT 1", {'id': current_user.id})
                loc_me = cur.fetchone()
                cur.execute("SELECT latitude, longitude FROM location WHERE id = %(id)s LIMIT 1", {'id': loc_me[0]})
                coordinates_me = cur.fetchone()
                for i in profil_list_id:
                    if i[0] != current_user.id:
                        cur.execute("SELECT latitude, longitude FROM location WHERE id =%(id)s LIMIT 1", {'id': i[1]})
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
                    cur.execute("SELECT id, first_name, username FROM users where id=%(id)s LIMIT 1", {'id': i[0]})
                    profil_list.append(cur.fetchone())
            cur.close()
            conn.close()
    #print(profil_list)
    profil_list = [x for x in profil_list if x not in blacklisted_list]
    print(len(profil_list))
    final_users = []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM \"Interest\";")
    full_interest = cur.fetchall()
    for user in profil_list:
        if user[0] != current_user.id:
            cur.execute("SELECT image_profil, age, location_id FROM profil WHERE user_id=%(id)s LIMIT 1", {'id': user[0]})
            user_details = cur.fetchone()
            #print(user[0])
            #print(user_details)
            if user_details != None:
                image_profil = user_details[0]
                #print(image_profil)
                cur.execute("SELECT id, path FROM images WHERE profil_id=%(id)s", {'id': user[0]})
                all_images = cur.fetchall()
                try:
                    fav_image = all_images[int(image_profil)][1]

                except:
                    all_images.append([0, 'test/no-photo.png']) 
                    all_images.append([1, 'test/no-photo.png'])
                    all_images.append([2, 'test/no-photo.png'])
                    all_images.append([3, 'test/no-photo.png'])
                    all_images.append([4, 'test/no-photo.png'])
                    fav_image = all_images[int(image_profil)][1]
                #print("all_images")
                #print(all_images)
                #print(fav_image)
                if fav_image:
                    image_profil_path = create_presigned_url(current_app.config["S3_BUCKET"], fav_image)
                else :
                    image_profil_path = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
                user_age = str(age(user_details[1]))
                cur.execute("SELECT city FROM location WHERE id=%(id)s LIMIT 1", {'id': user_details[2]})
                user_location = cur.fetchone()[0]
                final_users.append([user[1], user_age, user_location, image_profil_path, user[2]])
                #print(len(final_users))
    #print(profil_list)
    cur.close()
    conn.close()
    return render_template('research.html', all_users = final_users, user_num=len(final_users), full_interest=full_interest)
    
@main.route('/addnotification', methods = ['POST'])
def addnotif():
    if request.method == 'POST':
        receiver_id = request.form['receiver']
        notif_type = int(request.form['notif_type'])
        content = request.form['content']
        notif_date = float(datetime.now().timestamp())
        return_str="KO"
        if receiver_id :
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(id) FROM notifications WHERE (receiver_id=%(id)s AND notif_type=1 AND sender_id = %(from)s) LIMIT 1", {'id': receiver_id, 'from': current_user.id})
            if cur.fetchone()[0]==0:
                cur.execute("INSERT INTO notifications (sender_id, receiver_id, notif_type, content, date_added) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}');".format(current_user.id, receiver_id, notif_type, content, notif_date))
                conn.commit()
                return_str = NOTIF_TYPE[int(request.form['notif_type'])]
            else:
                cur.execute("UPDATE notifications SET date_added=%(d)s WHERE sender_id=%(from)s AND receiver_id=%(to)s", {'from': current_user.id, 'to': receiver_id, 'd': notif_date})
                conn.commit()
                return_str("Old")
            cur.close()
            conn.close()
            return (return_str)
        else:
            return (return_str)

@main.route('/readnotification', methods = ['POST'])
def readnotif():
    if request.method == 'POST':
        newvalue = None
        notif_type = int(request.form['notif_type'])

        if notif_type :
            conn = get_db_connection()
            cur = conn.cursor()
            if notif_type == 2:
                sender_id = request.form['sender_id']
                if sender_id :
                    cur.execute("UPDATE notifications SET is_read=true WHERE receiver_id=%(id)s AND notif_type=%(ntype)s AND sender_id=(SELECT id FROM users WHERE username=%(sid)s);", {'id': current_user.id, 'ntype': notif_type, 'sid': sender_id})
                    conn.commit()
                    cur.execute("SELECT COUNT(*) FROM notifications WHERE receiver_id=%(id)s AND is_read=false AND notif_type=%(t)s;", {'id': current_user.id, 't': notif_type})
                    newvalue = cur.fetchone()[0]
                else:
                    return("KO")
            else:
                cur.execute("UPDATE notifications SET is_read = true WHERE receiver_id=%(id)s AND notif_type=%(ntype)s;", {'id': current_user.id, 'ntype': notif_type})
                conn.commit()
                cur.execute("SELECT COUNT(*) FROM notifications WHERE receiver_id=%(id)s AND is_read=false AND notif_type=%(t)s;", {'id': current_user.id, 't': notif_type})
                newvalue = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM notifications WHERE receiver_id=%(id)s AND is_read=false", {'id': current_user.id})
            total_notif = cur.fetchone()[0]
            cur.close()
            conn.close()
            return {
                'notif_type': NOTIF_TYPE[int(request.form['notif_type'])],
                'value': newvalue,
                'total': total_notif,
            }
        else:
            return ("KO")

@main.route('/getnavnotification', methods = ['POST'])
def getnavnotif():

    if request.method == 'POST':

        if not current_user.is_authenticated:
            return("KO")
        conn = get_db_connection()
        cur = conn.cursor()

        #Notification setup Gesture
        cur.execute("SELECT COUNT(*) FROM notifications WHERE receiver_id='{0}' AND is_read=false AND notif_type=0;".format(current_user.id))
        nbr_like = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM notifications WHERE receiver_id='{0}' AND is_read=false AND notif_type=1;".format(current_user.id))
        nbr_view = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM notifications WHERE receiver_id='{0}' AND is_read=false AND notif_type=2;".format(current_user.id))
        nbr_msg = cur.fetchone()[0]

        total_notif = nbr_like + nbr_view + nbr_msg

        cur.close()
        conn.close()

        return {
            'likes': nbr_like,
            'views': nbr_view,
            'msgs': nbr_msg,
            'total': total_notif
        }

    else:
        return ("KO")

# we initialize our flask app using the  __init__.py function 
app = create_app()
#Spécification de la bibliothèque à utiliser pour le traitement asynchrone
# `threading`, `eventlet`, `gevent`Peut être sélectionné parmi
async_mode = None

#Objet Flask, asynchrone_Créer un objet serveur SocketIO en spécifiant le mode
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

#Variable globale pour stocker les threads


# Notifications Dynamic Gesture 
@socketio.on('join_request')
def on_join_request():
    if current_user.is_authenticated:
        user_id = current_user.id
        join_room(user_id)
        print("User join the chanel"+str(user_id))
        


@socketio.on('new_notif')
def new_notif(data):
    content = int(data['content'])
    value = content
    receiver = data['receiver']
    notif_type = NOTIF_TYPE[int(data['notif_type'])]
    # Si notif_type = message, add 1 to message
    emit("notifications",
        {"content": value, "notif_type":notif_type, "sender":current_user.username}, room=int(receiver))


@socketio.on('disconnect_request')
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)


# Chat Dynamic Gesture 
@socketio.on("send_message")
def message(data):
    username = data['username']
    if current_user.username < username :
        room = current_user.username+username
    else :
        room = username+current_user.username
    print(room)
    emit("broadcast_message", {"message": data['message'],"date":data['date'], "username":current_user.username, "room":room}, room=room)

@socketio.on('join')
def on_join(data):
    username = data['username']
    if current_user.username < username :
        channel = current_user.username+username
    else :
        channel = username+current_user.username
    join_room(channel)
    print("User join the chanel"+channel)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    if current_user.username < username :
        channel = current_user.username+username
    else :
        channel = username+current_user.username
    leave_room(channel)

# setup Mail
mail = Mail(app)   

if __name__ == '__main__':
    ##db.create_all(app=create_app())
    ##app.run(debug=True)
    socketio.run(app, debug=True)
