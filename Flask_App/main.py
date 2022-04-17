from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user

from flask_mail import Mail
#Chargement socketIO des modules requis
from flask import Flask, session, request         
from flask_socketio import SocketIO, emit, join_room, leave_room, \
      close_room, rooms, disconnect                                  



from __init__ import create_app, get_db_connection
from login_decorator import check_confirmed

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
    print(current_user)
    return render_template('profile.html', name=current_user.name)

# edit profile page that return 'edit-profile'
@main.route('/edit-profile') 
def editprofile():
    return render_template('edit-profile.html')

# account profile page that return 'account'
@main.route('/account') 
def account():
    return render_template('account.html')

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
    #app.run(debug=True)
    socketio.run(app)