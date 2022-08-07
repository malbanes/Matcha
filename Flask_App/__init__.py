from flask import Flask
from flask_login import LoginManager
import os
import psycopg2
from models import User
from dotenv import load_dotenv, find_dotenv



#import for time filter
from datetime import datetime

#sammy-test
def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='flask_db',
                            user=os.getenv('DB_USERNAME'),
                            password=os.getenv('DB_PASSWORD'))
    return conn

def create_app():
    app = Flask(__name__)
    load_dotenv(find_dotenv())
    # creates the Flask instance, __name__ is the name of the current Python module
    app.config['SECRET_KEY'] = 'secret-key-goes-here'

    app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
    # mail settings
    app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    # gmail authentication
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    # S3 upload
    app.config['S3_BUCKET'] = os.getenv('S3_BUCKET')
    app.config['S3_KEY'] = os.getenv('S3_KEY')
    app.config['S3_SECRET'] = os.getenv('S3_SECRET')
    app.config['S3_LOCATION'] = 'http://{}.s3.amazonaws.com/'.format(app.config['S3_BUCKET'])

    # The login manager contains the code that lets your application and Flask-Login work together
    login_manager = LoginManager() 
    # Create a Login Manager instance
    login_manager.login_view = 'auth.login' 
    # define the redirection path when login required and we attempt to access without being logged in
    login_manager.init_app(app) 
    # configure it for login

    #By Malbanes : time filter for message gesture
    @app.template_filter('strftime')
    def _jinja2_filter_datetime(date, fmt=None):
        mydate = datetime.fromtimestamp(date)
        native = mydate.replace(tzinfo=None)
        format='%H:%M:%S'
        return native.strftime(format) 
    
    @login_manager.user_loader
    def load_user(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id=%(id)s", {'id': user_id})        
        user = cur.fetchall()
        cur.close()
        conn.close()
        #reload user object from the user ID stored in the session since the user_id is just the primary key of our user table, use it in the query for the user
        return (User(user[0]))
    
    
    # blueprint for auth routes in our app, it allows you to organize your flask app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    
    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app