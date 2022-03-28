from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import psycopg2
#sammy-test
def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='flask_db',
                            user=os.environ['DB_USERNAME'],
                            password=os.environ['DB_PASSWORD'])
    return conn

def create_app():
    app = Flask(__name__) 
    # creates the Flask instance, __name__ is the name of the current Python module
    app.config['SECRET_KEY'] = 'secret-key-goes-here' 
    # it is used #by Flask and extensions to keep data safe
    ###app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' 
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:&hBDpRr5ztxas9Xx@localhost/users' 
    # it is the path where the SQLite database file will be saved
    #app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    # deactivate Flask-SQLAlchemy track modifications
    ##db.init_app(app) 
    # Initialiaze sqlite database
    #mysql = MySQL(app)
    
    # The login manager contains the code that lets your application and Flask-Login work together
    login_manager = LoginManager() 
    # Create a Login Manager instance
    login_manager.login_view = 'auth.login' 
    # define the redirection path when login required and we attempt to access without being logged in
    login_manager.init_app(app) 
    # configure it for login
    
    @login_manager.user_loader
    def load_user(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE id=(%s);', (user_id))
        user = cur.fetchall()
        print(user)
        cur.close()
        conn.close() 
        #reload user object from the user ID stored in the session since the user_id is just the primary key of our user table, use it in the query for the user
        return user
    
    
    # blueprint for auth routes in our app, it allows you to organize your flask app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    
    # blueprint for non-auth parts of app
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app