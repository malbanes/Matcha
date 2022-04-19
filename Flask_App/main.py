from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user

from flask_mail import Mail
#Chargement socketIO des modules requis
from flask import Flask, session, request         
from flask_socketio import SocketIO, emit, join_room, leave_room, \
      close_room, rooms, disconnect                                  



from __init__ import create_app, get_db_connection
from login_decorator import check_confirmed
from age_calc import age
from localization import localize_text
from datetime import date

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
    print(current_user.name)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM profil WHERE user_id='{0}' LIMIT 1;".format(current_user.id))
    profil = cur.fetchone()
    print(profil)
    age_num = str(age(profil[5]))
    description = profil[6]
    score = ""
    image_profil = ""
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
    return render_template('profile.html', name=current_user.name, age=age_num, desc=description, interest_list=interest_list, localisation=localisation)

# edit profile page that return 'edit-profile'
@main.route('/edit-profile') 
def editprofile():
    return render_template('edit-profile.html')

# account profile page that return 'account'
@main.route('/account', methods=['GET', 'POST'])
@login_required
@check_confirmed
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
    if request.method=='GET':
        return render_template('account.html', username=username, email=email, firstname=firstname, lastname=lastname, localisation=localisation)
    else:
        if 'username' in request.form:
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
                    cur.execute("UPDATE location SET latitude = '{0}', longitude = '{1}', date_modif = '{2}', city = '{3}' WHERE id='{4}';".format(lat,lont,today,display_loc,profil[4]))
                    conn.commit()
                    localisation = display_loc
                else:
                    flash('New location not found')
        elif 'oldpassword' in request.form:
            print("password")
        elif 'email' in request.form:
            print("email")
        else: 
            print("No modal implemented")
        cur.close()
        conn.close()
        return render_template('account.html', username=username, email=email, firstname=firstname, lastname=lastname, localisation=localisation)

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
@main.route('/search') 
def search():
    return render_template('research.html')
    

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