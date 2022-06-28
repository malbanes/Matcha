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
from gender_id import set_gender_orientation

from localization import localize_text, distance, localize_user
from datetime import date, datetime

from token_gen import generate_confirmation_token, confirm_token, generate_email_token, confirm_email_token
from email_mngr import send_email
from scoring import matching_calculation

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
OFFSET_MATCH = 3


# home page that return 'index'
main = Blueprint('main', __name__)
@main.route('/') 
def index():
    return render_template('index.html')

# we initialize our flask app using the  __init__.py function 
app = create_app()
#Spécification de la bibliothèque à utiliser pour le traitement asynchrone
# `threading`, `eventlet`, `gevent`Peut être sélectionné parmi
async_mode = None

#Objet Flask, asynchrone_Créer un objet serveur SocketIO en spécifiant le mode
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

# profile page that return 'profile'
@main.route('/profile') 
@login_required
@check_confirmed
def profile():
    images_path = []
    fav_image = []
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
    # get fav image               
    cur.execute("SELECT image_profil_id, i.path FROM profil INNER JOIN images as i on i.id=image_profil_id AND i.profil_id =%(id)s LIMIT 1;", {'id': current_user.id})
    image_profil = cur.fetchone()
    fav_image_path = create_presigned_url(current_app.config["S3_BUCKET"], image_profil[1])
    fav_image.append(image_profil[0])
    fav_image.append(fav_image_path)
    cur.execute("SELECT id, path FROM images WHERE profil_id=%(id)s AND id NOT IN (%(fav)s) ORDER BY date_added LIMIT 4", {'id': current_user.id, 'fav':image_profil[0]})
    all_images = cur.fetchall()
    for key, imgpth in all_images:
        images_path.append([key,create_presigned_url(current_app.config["S3_BUCKET"], imgpth)])
    cur.execute("SELECT COUNT(*) FROM images WHERE profil_id=%(id)s;", { 'id': current_user.id})
    total_img = cur.fetchone()[0]
    #if total_img > 5:
    #    total_img = 5
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
    fav_image = []
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

    cur.execute("SELECT image_profil_id, i.path FROM profil INNER JOIN images as i on i.id=image_profil_id AND i.profil_id =%(id)s LIMIT 1;", {'id': user_id})
    image_profil = cur.fetchone()
    print(image_profil)
    fav_image_path = create_presigned_url(current_app.config["S3_BUCKET"], image_profil[1])
    fav_image.append(image_profil[0])
    fav_image.append(fav_image_path)
    cur.execute("SELECT id, path FROM images WHERE profil_id=%(id)s AND id NOT IN (%(fav)s) ORDER BY date_added", {'id': user_id, 'fav':image_profil[0]})
    all_images = cur.fetchall()
    for key, imgpth in all_images:
        images_path.append([key,create_presigned_url(current_app.config["S3_BUCKET"], imgpth)])
    cur.execute("SELECT COUNT(*) FROM images WHERE profil_id=(SELECT user_id FROM profil WHERE user_id=%(id)s);", { 'id': user_id})
    total_img = cur.fetchone()[0]
    #if total_img > 5:
    #    total_img = 5
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


@main.route('/matchpass', methods = ['POST'])
@login_required
@check_confirmed
def matchpass():
    if request.method == 'POST':
        error = ""
        user_id = request.form['data']
        if user_id :
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(id) FROM accountcontrol WHERE (from_user_id=%(id)s AND to_user_id=%(tid)s AND blocked = true) LIMIT 1", {'id': user_id, 'tid': current_user.id})
            is_block = cur.fetchone()[0]
            cur.execute("SELECT COUNT(id) FROM match WHERE user_id=%(sid)s AND match_id=%(rid)s;",{'sid': current_user.id , 'rid': user_id})
            is_exist = cur.fetchone()[0]
            if is_block == 0 and is_exist != 0:
                cur.execute("UPDATE match SET is_pass=true WHERE user_id=%(sid)s AND match_id=%(rid)s;",{'sid': current_user.id , 'rid': user_id})
                conn.commit()
            else:
                error = "KO"
            cur.close()
            conn.close()
            return (error)
        else:
            return ("KO")

@main.route('/matchnext', methods = ['POST'])
@login_required
@check_confirmed
def matchnext():
    final_users = []
    if request.method == 'POST':
        error = ""
        user_id = request.form['data']
        if user_id :
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT to_user_id from accountcontrol WHERE from_user_id=%(id)s and blocked=true;", {'id':current_user.id})
            blocked_users=cur.fetchall()
            blocked_list = ','.join([str(elem[0]) for elem in blocked_users])
            if blocked_list != '':
                blocked_list = str(current_user.id) + ','+ blocked_list
            else:
                blocked_list = str(current_user.id)
            cur.execute("SELECT match_id, match.score FROM match INNER JOIN profil p on match.match_id=p.user_id AND match.user_id='{0}' AND is_filter=false AND is_pass=false AND match_id NOT IN ({1}) ORDER BY position, match.score desc LIMIT '{2}' OFFSET '{3}';".format(current_user.id, blocked_list, 1, 2))
            profil_list = cur.fetchall()
            for user in profil_list:
                cur.execute("SELECT users.id, username, age, city, image_profil_id, bio FROM users INNER JOIN profil ON users.id = profil.user_id AND users.id=%(id)s LEFT JOIN location ON  profil.location_id = location.id LIMIT 1", {'id': user[0]})
                user_details = cur.fetchone()
                #calc age
                if user_details:
                    user_age = age(user_details[2])
                    if user_details[4] is not None:
                        images_path = []
                        cur.execute("SELECT path from images where id =%(image_id)s LIMIT 1", {'image_id': user_details[4]})
                        user_image = cur.fetchone()
                        user_image = create_presigned_url(current_app.config["S3_BUCKET"], str(user_image[0]))
                        cur.execute("SELECT path FROM images WHERE profil_id=%(id)s AND id NOT IN (%(fav)s) ORDER BY date_added", {'id': user_details[0], 'fav':user_details[4]})
                        all_images = cur.fetchall()
                        for imgpth in all_images:
                            images_path.append([create_presigned_url(current_app.config["S3_BUCKET"], imgpth[0])])
                    else: 
                        user_image = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
                    final_users.append([user_details[0], user_details[1], user_age, user_details[3], user_details[5], user_image, images_path, int(user[1])])
            cur.close()
            conn.close()
            return {
                'final_users': final_users
            }
        else:
            return ("KO")


@main.route('/addlike', methods = ['POST'])
@login_required
@check_confirmed
def addlike():
    if request.method == 'POST':
        error = "KO"
        user_id = request.form['data']
        if user_id :
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(id) FROM accountcontrol WHERE (from_user_id=%(id)s AND to_user_id=%(tid)s AND blocked = true) LIMIT 1", {'id': user_id, 'tid': current_user.id})
            is_block = cur.fetchone()[0]
            cur.execute("SELECT COUNT(id) FROM likes WHERE sender_id=%(sid)s AND receiver_id=%(rid)s;",{'sid': current_user.id , 'rid': user_id})
            is_exist = cur.fetchone()[0]
            if is_block == 0 and is_exist == 0:
                cur.execute("INSERT INTO likes (sender_id, receiver_id) VALUES ('{0}', '{1}');".format(current_user.id , user_id))
                conn.commit()
                error = "sucess"
            cur.close()
            conn.close()
            return (error)
        else:
            return (error)

@main.route('/addvisite', methods = ['POST'])
@login_required
@check_confirmed
def addvisite():
    if request.method == 'POST':
        error = ""
        user_id = request.form['data']
        if user_id :
            conn = get_db_connection()
            cur = conn.cursor()
            #Add Visit or Update visit
            cur.execute("SELECT COUNT(id) FROM visites WHERE sender_id=%(sid)s AND receiver_id=%(rid)s", {'sid': current_user.id, 'rid': user_id})
            visit_send = cur.fetchone()[0]
            if visit_send == 0:
                cur.execute("INSERT INTO visites (sender_id, receiver_id) VALUES ('{0}', '{1}');".format(current_user.id , user_id))
                conn.commit()
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
            cur.execute("INSERT INTO messages (sender_id, receiver_id, msg, date_added) VALUES (%(sid)s, %(rid)s, %(msg)s, %(tim)s);", {'sid':current_user.id , 'rid': receiver_id, 'msg': msg, 'tim': msg_time})
            conn.commit()
            cur.execute("SELECT id, date_added FROM messages WHERE sender_id=%(sid)s AND receiver_id=%(rid)s AND msg=%(msg)s AND date_added=%(tim)s LIMIT 1;", {'sid':current_user.id , 'rid': receiver_id, 'msg': msg, 'tim': msg_time})
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
        error = ""
        user_id = request.form['data']
        if user_id :
            error = user_id
            conn = get_db_connection()
            cur = conn.cursor()
            # If Like was a Match: generate notification type like-1 ?
            cur.execute("SELECT COUNT(id) FROM likes WHERE sender_id='{0}' AND receiver_id='{1}';".format(user_id, current_user.id))
            if cur.fetchone()[0] > 0:
                # Was a match
                cur.execute("SELECT COUNT(id) FROM notifications WHERE sender_id=%(sid)s AND receiver_id=%(rid)s AND notif_type=3 AND is_read=false;", {'sid':current_user.id , 'rid': user_id})
                is_notif = cur.fetchone()[0]
                if is_notif == 0 :
                    notif_date = float(datetime.now().timestamp())
                    cur.execute("INSERT INTO notifications (notif_type, sender_id, receiver_id, date_added) VALUES (3, %(sid)s, %(rid)s, %(dat)s)",{'sid':current_user.id , 'rid': user_id, 'dat': notif_date})
                    error = "Match"
                else :
                    error = "Old"
            else :
                cur.execute("DELETE FROM notifications WHERE sender_id='{0}' AND receiver_id='{1}' AND notif_type=0".format(current_user.id , user_id))
                conn.commit()
            cur.execute("DELETE FROM likes WHERE sender_id='{0}' AND receiver_id='{1}';".format(current_user.id , user_id))
            conn.commit()
            cur.close()
            conn.close()
            return (error)
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
    fav_image = []
    full_interest = []
    conn = get_db_connection()
    cur = conn.cursor()
    # get fav image               
    cur.execute("SELECT image_profil_id, i.path FROM profil INNER JOIN images as i on i.id=image_profil_id AND i.profil_id =%(id)s LIMIT 1;", {'id': current_user.id})
    image_profil = cur.fetchone()
    print(image_profil)
    fav_image_path = create_presigned_url(current_app.config["S3_BUCKET"], image_profil[1])
    fav_image.append(image_profil[0])
    fav_image.append(fav_image_path)
    print("fav img: "+str(fav_image[0])+","+fav_image[1])

    cur.execute("SELECT id, path FROM images WHERE profil_id=%(id)s AND id NOT IN (%(fav)s) ORDER BY date_added LIMIT 4", {'id': current_user.id, 'fav':image_profil[0]})
    all_images = cur.fetchall()
    print("toutes les images: ")
    print(all_images)

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
        interest_list.append([cur.fetchone()[0].rstrip(), id[0]])
    cur.execute("SELECT interest_id, COUNT(interest_id) FROM \"ProfilInterest\" GROUP BY interest_id LIMIT 50;")
    popular_interests = cur.fetchall()
    for popular_interest  in popular_interests:
        cur.execute("SELECT * FROM \"Interest\" WHERE id =%(id)s LIMIT 1", {'id': popular_interest[0]})
        full_interest.append(cur.fetchone())
    cur.execute("SELECT COUNT(*) FROM images WHERE profil_id=%(id)s;", { 'id': current_user.id})
    total_img = cur.fetchone()[0]
    cur.close()
    conn.close()
    for key, imgpth in all_images:
        image_path[str(key)] = create_presigned_url(current_app.config["S3_BUCKET"], imgpth)
    if total_img < 5:
        image_path['default'] = create_presigned_url(current_app.config["S3_BUCKET"],"test/no-photo.png")
    return render_template('edit-profile.html', image_profil=fav_image, images_urls=image_path, total_img=total_img, interest=interest_list, bio=i_am_bio, genre=i_am_genre, orientation=i_am_orientation, full_interest=full_interest)

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
            cur.execute("SELECT COUNT(*) FROM images WHERE profil_id=%(id)s;", { 'id': current_user.id})
            result = cur.fetchone()[0]
            if result < 5:
                cur.execute("INSERT INTO images (title, path, profil_id, date_added) VALUES (%(title)s, %(path)s, %(id)s, %(date_added)s)", {'title': file1.filename, 'path': file_path, 'id': current_user.id, 'date_added': date.today()})
                conn.commit()
            if result == 0:
                cur.execute("SELECT FROM images id WHERE profil_id=%(id)s LIMIT 1", {'id': current_user.id})
                fav_id = cur.fetchone()[0]
                cur.execute("UPDATE profil SET image_profil_id=%(fav)s WHERE user_id=%(id)s", {'fav': fav_id, 'id': current_user.id})
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
            conn = get_db_connection()
            cur = conn.cursor()
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
            # IF img_id == image_profil_id :
            # remplacer par une autre image disponnible.
            # Id pas d'image dispo' mettre image_profil_id à null
            # delete l'image
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
        cur.execute("DELETE FROM search WHERE user_id = %(id)s", {'id': current_user.id})
        conn.commit()
        cur.execute("DELETE FROM match WHERE user_id = %(id)s", {'id': current_user.id})
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
        newhash = request.form['newhash']
        existing_list = []
        
        #TO DO: Chech if newhash exist and secure variable
        #TO DO: check if newtag existe insensible a la casse ToLowercase(newhash) existe en bdd (TolowerCase(hashtag))
        #TO DO: Si exist ou caractère interdi, return "KO"
        if (newhash):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO \"Interest\" (hashtag) VALUES (%(hash)s) ", {'hash': newhash})
            conn.commit()
            cur.execute("SELECT id, hashtag FROM \"Interest\" WHERE hashtag=%(hash)s LIMIT 1", {'hash': newhash})
            existing_elem = cur.fetchone()
            existing_list.append([existing_elem[0], existing_elem[1].rstrip()])
            cur.execute("INSERT INTO \"ProfilInterest\" (user_id, interest_id) VALUES (%(uid)s, %(int)s)", {'uid': current_user.id, 'int': existing_elem[0]})
            conn.commit()
            cur.close()
            conn.close()
            return jsonify(existing_list)
        elif (hash_id):
            conn = get_db_connection()
            cur = conn.cursor()
            for i in hash_id:
                cur.execute("SELECT COUNT(id) FROM \"ProfilInterest\" WHERE user_id=%(uid)s AND interest_id=%(int)s", {'uid': current_user.id, 'int': i })
                is_exist = cur.fetchone()[0]
                if is_exist == 0:
                    cur.execute("INSERT INTO \"ProfilInterest\" (user_id, interest_id) VALUES (%(uid)s, %(int)s)", {'uid': current_user.id, 'int': i})
                    conn.commit()
                    cur.execute("SELECT id, hashtag FROM \"Interest\" WHERE id=%(id)s LIMIT 1", {'id': i})
                    existing_elem = cur.fetchone()
                    existing_list.append([existing_elem[0], existing_elem[1].rstrip()])
                    print(existing_list)
            cur.close()
            conn.close()
            return jsonify(existing_list)
        else:
            return ("KO")

@main.route('/delhashtag', methods = ['POST'])
@login_required
@check_confirmed
def delhash():
    if request.method == 'POST':
        hashtag = request.form['data']
        if (hashtag):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM \"ProfilInterest\" WHERE user_id=%(id)s AND interest_id=%(int)s", {'id': current_user.id, 'int':hashtag})
            conn.commit()
            cur.close()
            conn.close()
            return (hashtag)
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
    cur.execute("SELECT image_profil_id FROM profil WHERE user_id=%(id)s", {'id': current_user.id})
    image_profil = cur.fetchone()[0]
    cur.execute("SELECT path FROM images WHERE id=%(id)s", {'id': image_profil})
    fav_image = cur.fetchone()[0]
    if fav_image :
        image_profil_path = create_presigned_url(current_app.config["S3_BUCKET"], fav_image)
    else :
        image_profil_path = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
    
    # Select blocked user_id
    cur.execute("SELECT to_user_id from accountcontrol WHERE from_user_id=%(id)s and blocked=true;", {'id':current_user.id})
    blocked_users=cur.fetchall()
    for i in blocked_users:
        cur.execute("SELECT users.id, username, i.path from users INNER JOIN profil as p ON users.id=p.user_id AND users.id=%(id)s LEFT JOIN images as i on i.id=p.image_profil_id LIMIT 1;", {'id': i})
        blocked_profil = cur.fetchone()
        if blocked_profil[2] is not None:
            user_image = create_presigned_url(current_app.config["S3_BUCKET"], str(blocked_profil[2]))
        else: 
            user_image = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
        #calc age
        blocked_list.append([blocked_profil[0], blocked_profil[1], user_image])
  
    #set blocked_list for views and likes + exclude current_user
    blocked_string = str(current_user.id)+','.join([str(elem[0]) for elem in blocked_users])
    # Select Like user_id
    cur.execute("SELECT sender_id FROM likes WHERE receiver_id='{0}' AND sender_id NOT IN ({1});".format(current_user.id, blocked_string))
    like_users=cur.fetchall()
    for i in like_users:
        cur.execute("SELECT users.id, username, age, city, i.path FROM users INNER JOIN profil ON users.id = profil.user_id AND users.id=%(id)s LEFT JOIN location ON  profil.location_id = location.id LEFT JOIN images as i on i.id=profil.image_profil_id LIMIT 1;", {'id': i})
        like_profil = cur.fetchone()
        if like_profil[4] is not None:
            user_image = create_presigned_url(current_app.config["S3_BUCKET"], str(like_profil[4]))
        else: 
            user_image = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
        #calc age
        user_age = age(like_profil[2])
        #did i like this person ? 
        cur.execute("SELECT COUNT(id) FROM likes WHERE sender_id=%(sid)s AND receiver_id=%(rid)s", {'sid': current_user.id, 'rid': like_profil[0]})
        is_like = cur.fetchone()[0]
        likes_list.append([like_profil[0], like_profil[1], user_age, like_profil[3], is_like, user_image])
    # Select visites user_id

    user_image = ""
    #cur.execute("INSERT INTO notifications (sender_id, receiver_id, notif_type, content, date_added) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}');".format(current_user.id, receiver_id, notif_type, content, notif_date))
    cur.execute("SELECT sender_id FROM visites WHERE receiver_id='{0}' AND sender_id NOT IN ({1});".format(current_user.id, blocked_string))
    visite_users=cur.fetchall()
    for i in visite_users:
        cur.execute("SELECT users.id, username, age, city, i.path FROM users INNER JOIN profil ON users.id = profil.user_id AND users.id=%(id)s LEFT JOIN location ON profil.location_id = location.id LEFT JOIN images as i on i.id=profil.image_profil_id LIMIT 1;", {'id': i})
        visite_profil = cur.fetchone()
        if visite_profil[4] is not None:
            user_image = create_presigned_url(current_app.config["S3_BUCKET"], str(visite_profil[4]))
        else: 
            user_image = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
        #calc age
        user_age = age(visite_profil[2])
        #did i like this person ? 
        cur.execute("SELECT COUNT(id) FROM likes WHERE sender_id=%(sid)s AND receiver_id=%(rid)s", {'sid': current_user.id, 'rid': visite_profil[0]})
        is_like = cur.fetchone()[0]
        views_list.append([visite_profil[0], visite_profil[1], user_age, visite_profil[3], is_like, user_image])
    
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
@main.route('/match', methods=['GET'])
@main.route('/match/page/<int:page>', methods=['GET'])
@login_required
@check_confirmed
def match(page=1):
    final_users = []

    conn = get_db_connection()
    cur = conn.cursor()
    #Page doit être > 0 car offset ne prend pas de négatif
    page = 1
    offset = (page - 1) * OFFSET_MATCH
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
    if request.method=='GET':
        user_age = 18
        # Get number of pages
        cur.execute("SELECT COUNT(id) FROM match WHERE user_id='{0}' AND is_pass=false AND is_filter=false AND match_id NOT IN ({1}) ;".format(current_user.id, blocked_list))
        total_users = cur.fetchone()[0]
        if total_users == 0:   
            cur.execute("SELECT orientation_id, location_id, age, score FROM profil WHERE user_id = %(id)s LIMIT 1", {'id':current_user.id})
            user_details = cur.fetchone()
            cur.execute("SELECT latitude, longitude, city FROM location WHERE id = %(id)s LIMIT 1", {'id':user_details[1]})
            user_loc = cur.fetchone()
            cur.execute("SELECT count(id) FROM \"ProfilInterest\" WHERE user_id = %(id)s LIMIT 1", {'id':current_user.id})
            interest_num = cur.fetchone()[0]
            matching_calculation(user_details[0], user_loc[1], user_loc[0], user_loc[2], interest_num, age(user_details[2]), user_details[3])
        
        cur.execute("SELECT match_id, match.score FROM match INNER JOIN profil p on match.match_id=p.user_id AND match.user_id='{0}' AND is_filter=false AND is_pass=false AND match_id NOT IN ({1}) ORDER BY position, match.score desc LIMIT '{2}' OFFSET '{3}';".format(current_user.id, blocked_list, OFFSET_MATCH, offset))
        profil_list = cur.fetchall()

        max_page = int((total_users/OFFSET_MATCH)+1)
        if ((total_users % OFFSET_MATCH) > 0) :
            max_page+1

        for user in profil_list:
            cur.execute("SELECT users.id, username, age, city, image_profil_id, bio FROM users INNER JOIN profil ON users.id = profil.user_id AND users.id=%(id)s LEFT JOIN location ON  profil.location_id = location.id LIMIT 1", {'id': user[0]})
            user_details = cur.fetchone()
            #calc age
            if user_details:
                user_age = age(user_details[2])
                if user_details[4] is not None:
                    images_path = []
                    cur.execute("SELECT path from images where id =%(image_id)s LIMIT 1", {'image_id': user_details[4]})
                    user_image = cur.fetchone()
                    user_image = create_presigned_url(current_app.config["S3_BUCKET"], str(user_image[0]))
                    cur.execute("SELECT path FROM images WHERE profil_id=%(id)s AND id NOT IN (%(fav)s) ORDER BY date_added", {'id': user_details[0], 'fav':user_details[4]})
                    all_images = cur.fetchall()
                    for imgpth in all_images:
                        images_path.append([create_presigned_url(current_app.config["S3_BUCKET"], imgpth[0])])
                else: 
                    user_image = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
                final_users.append([user_details[0], user_details[1], user_age, user_details[3], user_details[5], user_image, images_path, int(user[1])])
        cur.close()
        conn.close()
        return render_template('match.html', max_page=max_page, current_page=page, all_users = final_users, user_num=total_users, full_interest=full_interest)

# chat page that return 'match'
@main.route('/chat') 
@login_required
@check_confirmed
def chat():
    print(current_user)
    print(current_user.id)
    print(current_user.is_authenticated)
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

    return render_template('chat.html', sync_mode=socketio.async_mode, usersList=usersList, usersListSize=len(usersList), roomsList=roomsList, messagesList=messagesList, current_user=current_user, onlineList=onlineList, notifList=notifList)

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
        if notif_type == 3:
            message = "doesn't like you anymore"
        if notif_type == 0:
            if content == 1:
                message = "like you"
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
    final_users = []

    if request.method == 'POST':
        print(request.form.get('ageCheck'))
        print(request.form.get('ageCheckOrder'))
        print(request.form.get('distCheck'))
        print(request.form.get('distCheckOrder'))
        print(request.form.get('scoreCheck'))
        print(request.form.get('scoreCheckOrder'))
        print(request.form.get('hashtagCheck'))
        print(request.form.get('hashtagCheckOrder'))
        if request.form.get('hashtagCheck') == "on":
            if request.form.get('hashtagCheckOrder') == "on":
                sort.append(["hashtag", "+"])
            else:
                sort.append(["hashtag", "-"])
        if request.form.get('distCheck') == "on":
            if request.form.get('distCheckOrder') == "on":
                sort.append(["dist", "+"])
            else:
                sort.append(["dist", "-"])
        if request.form.get('ageCheck') == "on":
            if request.form.get('ageCheckOrder') == "on":
                sort.append(["age", "+"])
            else:
                sort.append(["age", "-"])
        if request.form.get('scoreCheck') == "on":
            if request.form.get('scoreCheckOrder') == "on":
                sort.append(["score", "+"])
            else:
                sort.append(["score", "-"])
    conn = get_db_connection()
    cur = conn.cursor()

    # Get Location of current user to calculate distance
    cur.execute("SELECT latitude, longitude from location WHERE id=(SELECT location_id FROM profil WHERE user_id=%(id)s);", {'id': current_user.id})
    current_user_loc = cur.fetchone()
    data = {'id': current_user.id}
    data['lat'] = current_user_loc[0]
    data['long'] = current_user_loc[1]

    search_list_str = ""
    cur.execute("SELECT list_id FROM search WHERE user_id=%(id)s", {'id': current_user.id})
    search_list = cur.fetchall()
    search_list_str = ','.join([str(elem[0]) for elem in search_list])

    # Prepare select tri with previous search Result
    select_stmt = "SELECT users.id FROM users INNER JOIN profil as p ON users.id= p.user_id "
    if search_list_str != "":
        select_stmt = select_stmt + "AND p.user_id IN ("+ search_list_str +") "
    else:
        select_gender= set_gender_orientation()
        select_stmt = select_stmt + select_gender
    select_stmt = select_stmt + "LEFT JOIN location as l ON p.location_id=l.id "
    select_stmt = select_stmt + 'LEFT JOIN \"ProfilInterest\"  pi ON users.id = pi.user_id AND pi.interest_id IN (SELECT interest_id FROM \"ProfilInterest\"  WHERE user_id=%(id)s) '
    select_stmt = select_stmt + "GROUP BY users.id, p.age, p.score, l.latitude, l.longitude "
    select_stmt = select_stmt + "ORDER BY "

    elem_lengh = len(sort)
    if elem_lengh == 0:
        return {
            'all_users': [],
            'error' : 1
        }

    print("My array lenght is: ", str(elem_lengh))
    for elem in sort:
        if elem[0] == "age" and elem[1] == "+":
            select_stmt = select_stmt + "p.age DESC"
        elif elem[0] == "age" and elem[1] == "-":
            select_stmt = select_stmt + "p.age"
        if elem[0] == "dist" and elem[1] == "+":
            select_stmt = select_stmt + "ABS( (l.latitude) - (%(lat)s) ) + ABS( (l.longitude) - (%(long)s) )"
        elif elem[0] == "dist" and elem[1] == "-":
            select_stmt = select_stmt + "ABS( (l.latitude) - (%(lat)s) ) + ABS( (l.longitude) - (%(long)s) ) DESC"
        if elem[0] == "score" and elem[1] == "+":
            select_stmt = select_stmt + "p.score"
        elif elem[0] == "score" and elem[1] == "-":
            select_stmt = select_stmt + "p.score DESC"
        if elem[0] == "hashtag" and elem[1] =="+":
            select_stmt = select_stmt + "count(pi.interest_id)"
        elif elem[0] == "hashtag" and elem[1] =="-":
            select_stmt = select_stmt + "count(pi.interest_id) DESC"
        if elem_lengh > 1:
            select_stmt = select_stmt + ", "
        elem_lengh = elem_lengh -1

    cur.execute(select_stmt, data)
    all_profil_list = cur.fetchall()
    position = 1
    for user in all_profil_list:
        cur.execute("UPDATE search set position=%(pos)s WHERE user_id=%(id)s AND list_id=%(lid)s", {'pos': position, 'id': current_user.id, 'lid':user})
        conn.commit()
        position = position +1
    cur.close()
    conn.close()
    return {
        'all_users': [],
        'error' : 0
    }
    #return render_template('search.html', all_users = final_users, user_num=len(final_users), full_interest=full_interest)


@main.route('/filtresearch', methods = ['POST'])
@login_required
@check_confirmed
def filtresearch():
    filtre = []
    existing_list = []
    final_users = []
    age_qwery = ""
    loc_qwery = ""
    score_qwery = ""
    hash_qwery = ""
    hash_id = ""
    final_profil_list_id = []
    if request.method == 'POST':
        if request.form.get('ageFiltreCheck') == "on":
            if request.form.get('ageMin') !='' and request.form.get('ageMax') != '':
                filtre.append(["age", request.form.get('ageMin'), request.form.get('ageMax')])
        if request.form.get('locFiltreCheck') == "on":
            if request.form.get('city') != '':
                filtre.append(["city", request.form.get('city')])
        if request.form.get('scoreFiltreCheck') == "on":
            if request.form.get('scoreMin') != '' and request.form.get('scoreMax') != '':
                filtre.append(["score", request.form.get('scoreMin'), request.form.get('scoreMax')])
        if request.form.get('hashtagFiltreCheck') == "on":
            hash_id = request.form.getlist("check")

    conn = get_db_connection()
    cur = conn.cursor()
    #Check if hashtag exist in bdd
    if (hash_id != ""):
        for elem in hash_id:
            cur.execute("SELECT id FROM \"Interest\" WHERE id=%(id)s LIMIT 1", {'id': elem})
            existing_list.append(cur.fetchone()[0])
        filtre.append(["hashtag", existing_list])
    nbr_hashtag = len(existing_list)
    # Check if at least 1 filter is selected
    if (len(filtre) == 0):
        return {
            'all_users': [],
            'error' : 1
        }
    # Construct request by checked filtre
    data = {'id': current_user.id}
    for elem in filtre:
        # Prepare age qwery
        if elem[0] == "age":
            ageMinComp = age_period(elem[1])
            ageMaxComp = age_period(elem[2])
            data['amax'] = ageMaxComp
            data['amin'] = ageMinComp
            age_qwery = "AND p.age BETWEEN %(amax)s and %(amin)s "
        # Prepare location qwery
        elif elem[0] == "city":
             locRange = request.form.get('locRange')
             print(locRange)
             get_long, get_lat, city_name = localize_text(elem[1])
             cur.execute("SELECT user_id, location_id FROM profil")
             profil_list_id = cur.fetchall()
             for i in profil_list_id:
                 if i[0] != current_user.id:
                     cur.execute("SELECT latitude, longitude FROM location WHERE id =%(id)s LIMIT 1", {'id': i[1]})
                     coordinates_others = cur.fetchone()
                     off_distance = distance(get_lat, get_long, coordinates_others[0], coordinates_others[1])
                     if off_distance <= float(locRange):
                         final_profil_list_id.append(i)
                     else:
                         print("remove user")
             #Ensuite, tu la formate pour rentrer dans une requete sql :
             print(final_profil_list_id)
             final_profil_list_id_str = ','.join([str(elem[0]) for elem in final_profil_list_id])
             if final_profil_list_id_str:
                 #On rajoute l'élément à la requete en préparation:
                 loc_qwery = "AND user_id IN ("+final_profil_list_id_str+") "
                 print(loc_qwery)
        # Prepare score qwery
        elif elem[0] == "score":
            scoreMinSearch = int(elem[1])
            scoreMaxSearch = int(elem[2])
            if scoreMinSearch == scoreMaxSearch:
                score_qwery = "AND p.score = %(smin)s"
                data['smin'] = scoreMinSearch
            else:
                data['smin'] = scoreMinSearch
                data['smax'] = scoreMaxSearch
                score_qwery = "AND p.score BETWEEN %(smin)s and %(smax)s "
        # Prepare hashtag qwery
        elif elem[0] == "hashtag" and elem[1]:
            interest_str = ','.join([str(interest_id) for interest_id in elem[1]])
            hashtag_match = []
            cur.execute("SELECT user_id, COUNT(interest_id) FROM \"ProfilInterest\"  WHERE user_id !=%(id)s AND interest_id IN ("+ interest_str +") GROUP BY user_id ORDER BY COUNT(interest_id) desc;", {'id': current_user.id})
            potential_hash_match = cur.fetchall()
            for potential in potential_hash_match:
                if potential[1] >= nbr_hashtag:
                    hashtag_match.append(potential[0])
                else:
                    # Si on à terminer de checker les user ok, on sort de la boucle - CF Order by
                    break
            if len(hashtag_match) == 0:
                # Return render - Aucuns match retourne 0 users
                print("ERROR: No user to match interest")
                return {
                    'all_users': [],
                    'error' : 0
                }
            else :
                hashtag_match_str = ','.join([str(user_id) for user_id in hashtag_match])
                hash_qwery = "AND p.user_id IN ("+ hashtag_match_str +") "
    
    search_list_str = ""
    cur.execute("SELECT list_id FROM search WHERE user_id=%(id)s", {'id': current_user.id})
    search_list = cur.fetchall()
    search_list_str = ','.join([str(elem[0]) for elem in search_list])

    # Prepare select filtre with previous search Result
    select_stmt = "SELECT users.id FROM users INNER JOIN profil as p ON users.id= p.user_id "
    if search_list_str != "":
        select_stmt = select_stmt + "AND p.user_id IN ("+ search_list_str +") " 
    else:
        select_gender= set_gender_orientation()
        select_stmt = select_stmt + select_gender
    if hash_qwery != "":
            select_stmt = select_stmt + hash_qwery
    if score_qwery != "":
        select_stmt = select_stmt + score_qwery
    if age_qwery != "":        
        select_stmt = select_stmt + age_qwery
    if loc_qwery != "":
         select_stmt = select_stmt + loc_qwery


    select_stmt = select_stmt + "ORDER BY p.last_log DESC"

    cur.execute(select_stmt, data)
    filtre_profil_list = cur.fetchall()
    filtre_list_str = ','.join([str(elem[0]) for elem in filtre_profil_list])
    total_user = len(filtre_profil_list)

    upd_search_qwery = "UPDATE search SET is_filter=True WHERE user_id=%(id)s AND list_id NOT IN ("+ filtre_list_str +") " 
    upd_data = {'id': current_user.id}
    cur.execute(upd_search_qwery, upd_data)
    conn.commit()
    upd_search_qwery = "UPDATE search SET is_filter=False WHERE user_id=%(id)s AND list_id IN ("+ filtre_list_str +") " 
    cur.execute(upd_search_qwery, upd_data)
    conn.commit()

    select_stmt = select_stmt + " LIMIT 20;"

    cur.execute(select_stmt, data)
    all_profil_list = cur.fetchall()
    for user in all_profil_list:
        cur.execute("SELECT users.id, username, age, city, image_profil_id FROM users INNER JOIN profil ON users.id = profil.user_id AND users.id=%(id)s LEFT JOIN location ON  profil.location_id = location.id LIMIT 1", {'id': user})
        user_details = cur.fetchone()
        #calc age
        user_age = age(user_details[2])
        if user_details[4] is not None:
            cur.execute("SELECT path from images where id =%(image_id)s LIMIT 1", {'image_id': user_details[4]})
            user_image = cur.fetchone()
            user_image = create_presigned_url(current_app.config["S3_BUCKET"], str(user_image[0]))
        else: 
            user_image = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
        final_users.append([user_details[0], user_details[1], user_age, user_details[3], user_image])

    cur.close()
    conn.close()
    return {
        'all_users': [],
        'error' : 0
    }
    #return render_template('search.html', all_users = final_users, user_num=len(final_users), full_interest=full_interest)


@main.route('/filtreresetsearch', methods = ['POST'])
@login_required
@check_confirmed
def filtreresetsearch():
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM search WHERE user_id=%(id)s AND is_filter=true", {'id':current_user.id})
        filtered_user = cur.fetchall()
        for user in filtered_user:
            cur.execute("UPDATE search SET is_filter=false WHERE id=%(id)s", {'id':user})
            conn.commit()
        cur.close()
        conn.close()
        return("OK")
    return("KO")

@main.route('/triresetsearch', methods = ['POST'])
@login_required
@check_confirmed
def triresetsearch():
    if request.method == 'POST':
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM search WHERE user_id=%(id)s", {'id':current_user.id})
        search_user = cur.fetchall()
        for user in search_user:
            cur.execute("UPDATE search SET position=0 WHERE id=%(id)s", {'id':user})
            conn.commit()
        cur.close()
        conn.close()
        return("OK")
    return("KO")

# New Search thet return 'search'
@main.route('/search', methods=['GET', 'POST'])
@main.route('/search/page/<int:page>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def search(page=1):
    final_users = []
    is_search = False
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
    select_gender= set_gender_orientation()

    # On GET Return All Users except block and current
    if request.method=='GET':
        user_age = 18
        # Get number of pages
        cur.execute("SELECT COUNT(id) FROM search WHERE user_id='{0}' AND is_filter=false AND list_id NOT IN ({1}) ;".format(current_user.id, blocked_list))
        total_users = cur.fetchone()[0]
        if total_users > 0:       
            cur.execute("SELECT list_id FROM search INNER JOIN profil p on search.list_id=p.user_id AND search.user_id='{0}' AND is_filter=false AND list_id NOT IN ({1}) ORDER BY position, p.last_log desc LIMIT '{2}' OFFSET '{3}';".format(current_user.id, blocked_list, OFFSET, offset))
            profil_list = cur.fetchall()
            is_search = True
        else:
            is_search = False
            cur.execute("SELECT COUNT(users.id) FROM users INNER JOIN profil p on users.id=p.user_id AND users.id NOT IN ({0}) {1};".format(blocked_list, select_gender))
            total_users = cur.fetchone()[0]
            # Select all user from page=page except blocked ones
            cur.execute("SELECT users.id FROM users INNER JOIN profil p on users.id=p.user_id AND users.id NOT IN ({0}) {1} ORDER BY score DESC LIMIT '{2}';".format(blocked_list, select_gender, OFFSET))
            profil_list = cur.fetchall()
        max_page = int((total_users/OFFSET)+1)
        if ((total_users % OFFSET) > 0) :
            max_page+1
        for user in profil_list:
            cur.execute("SELECT users.id, username, age, city, image_profil_id FROM users INNER JOIN profil ON users.id = profil.user_id AND users.id=%(id)s LEFT JOIN location ON  profil.location_id = location.id LIMIT 1", {'id': user})
            user_details = cur.fetchone()
            #calc age
            if user_details:
                user_age = age(user_details[2])
                if user_details[4] is not None:
                    cur.execute("SELECT path from images where id =%(image_id)s LIMIT 1", {'image_id': user_details[4]})
                    user_image = cur.fetchone()
                    user_image = create_presigned_url(current_app.config["S3_BUCKET"], str(user_image[0]))
                else: 
                    user_image = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
                final_users.append([user_details[0], user_details[1], user_age, user_details[3], user_image])
        cur.close()
        conn.close()
        return render_template('search.html', is_search=is_search, max_page=max_page, current_page=page, all_users = final_users, user_num=total_users, full_interest=full_interest)
    # On POST return Users that match Search Inputs
    if request.method=='POST':
        is_search = True
        if 'ageMinSearch' in request.form:
            ageMinSearch = request.form.get('ageMinSearch')
            ageMaxSearch = request.form.get('ageMaxSearch')
            citySearch = request.form.get('citySearch')
            locRangeSearch = request.form.get('locRangeSearch')
            scoreMinSearch = request.form.get('scoreMinSearch')
            scoreMaxSearch = request.form.get('scoreMaxSearch')
            hashtags_id = request.form.getlist('searchcheck') 
            hashtag_user_list = []
            final_profil_list_id = []
            #to meter#
            #locRangeSearch = int(locRangeSearch)
            print("locRange:"+locRangeSearch)
            # Prepare Select Qwery
            select_stmt = " FROM profil WHERE user_id NOT IN ("+blocked_list+") " + select_gender
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
                if scoreMinSearch == scoreMaxSearch:
                    select_stmt = select_stmt+" AND score = %(smin)s"
                    data['smin'] = scoreMinSearch
                else:
                    select_stmt = select_stmt+" AND score between %(smin)s and %(smax)s"
                    data['smin'] = scoreMinSearch
                    data['smax'] = scoreMaxSearch
            #Location qwery
                #locRangeSearch
            #if citySearch != '':
                #cur.execute("SELECT city from ")
            if citySearch != '':
                get_long, get_lat, city_name = localize_text(citySearch)
                cur.execute("SELECT user_id, location_id FROM profil")
                profil_list_id = cur.fetchall()
                for i in profil_list_id:
                    if i[0] != current_user.id:
                        cur.execute("SELECT latitude, longitude FROM location WHERE id =%(id)s LIMIT 1", {'id': i[1]})
                        coordinates_others = cur.fetchone()
                        off_distance = distance(get_lat, get_long, coordinates_others[0], coordinates_others[1])
                        print(off_distance)
                        if off_distance <= float(locRangeSearch):
                            print("keep user")
                            final_profil_list_id.append(i)
                        else:
                            print("remove user")
                        print(float(locRange))
                        print(off_distance)
                #Ensuite, tu la formate pour rentrer dans une requete sql :
                final_profil_list_id_str = ','.join([str(elem[0]) for elem in final_profil_list_id])
                if final_profil_list_id_str:
                    #On rajoute l'élément à la requete en préparation:
                    select_stmt = select_stmt+" AND user_id IN ("+final_profil_list_id_str+")"
                print(final_profil_list_id_str)
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
                if hashtag_user_list_str:
                    select_stmt = select_stmt+" AND user_id IN ("+hashtag_user_list_str+")"
                else:
                    print("No user found")
                    return render_template('search.html', max_page=1, is_search=is_search, current_page=1, all_users = [], user_num=0, full_interest=full_interest)
            
            # Get number of pages
            get_page_qwery = "SELECT COUNT(id)" + select_stmt
            cur.execute(get_page_qwery, data)
            print(get_page_qwery)
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
                cur.execute("SELECT users.id, username, age, city, image_profil_id FROM users INNER JOIN profil ON users.id = profil.user_id AND users.id=%(id)s LEFT JOIN location ON  profil.location_id = location.id LIMIT 1", {'id': user})
                user_details = cur.fetchone()
                #calc age
                user_age = age(user_details[2])
                if user_details[4] is not None:
                    cur.execute("SELECT path from images where id =%(image_id)s LIMIT 1", {'image_id': user_details[4]})
                    user_image = cur.fetchone()
                    user_image = create_presigned_url(current_app.config["S3_BUCKET"], str(user_image[0]))
                else: 
                    user_image = create_presigned_url(current_app.config["S3_BUCKET"], "test/no-photo.png")
                final_users.append([user_details[0], user_details[1], user_age, user_details[3], user_image])
    cur.close()
    conn.close()
    return render_template('search.html', max_page=max_page, is_search=is_search, current_page=page, all_users = final_users, user_num=user_num, full_interest=full_interest)

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
            cur.execute("SELECT COUNT(id) FROM notifications WHERE receiver_id=%(id)s AND notif_type=%(tid)s AND is_read=false AND sender_id = %(from)s LIMIT 1", {'id': receiver_id, 'tid': notif_type, 'from': current_user.id})
            if cur.fetchone()[0]==0:
                cur.execute("INSERT INTO notifications (sender_id, receiver_id, notif_type, content, date_added) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}');".format(current_user.id, receiver_id, notif_type, content, notif_date))
                conn.commit()
                return_str = NOTIF_TYPE[int(request.form['notif_type'])]
            else:
                cur.execute("UPDATE notifications SET date_added=%(d)s WHERE sender_id=%(from)s AND receiver_id=%(to)s", {'from': current_user.id, 'to': receiver_id, 'd': notif_date})
                conn.commit()
                return_str = "Old"

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
        if notif_type or notif_type==0 :
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
                cur.execute("UPDATE notifications SET is_read=true WHERE receiver_id=%(id)s AND notif_type=%(ntype)s;", {'id': current_user.id, 'ntype': notif_type})
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
        cur.execute("SELECT COUNT(*) FROM notifications WHERE receiver_id='{0}' AND is_read=false AND (notif_type=0 OR notif_type=3);".format(current_user.id))
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

#Variable globale pour stocker les threads


# Notifications Dynamic Gesture 

@socketio.on('join_request')
def on_join_request():
    print("ON JOIN REQUEST")
    print("ON JOIN REQUEST")
    print("ON JOIN REQUEST")
    if current_user.is_authenticated:
        user_id = current_user.id
        join_room(user_id)
        print("User join the chanel"+str(user_id))
        

@socketio.on('new_notif')
def new_notif(data):
    content = int(data['content'])
    value = content
    type_id = int(data['notif_type'])
    if type_id == 3 :
        type_id = 0
    receiver = data['receiver']
    notif_type = NOTIF_TYPE[type_id]
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
