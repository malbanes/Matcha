
Install Dependency:

- install python3.9
- sudo easy_install pip 
- sudo pip install pipenv
- pipenv --python /usr/local/bin/python3
- pipenv shell
- python3 -m pip install werkzeug==2.0.0

- pip install Flask
- pip install flask_login
- pip install flask-jsonpify
- pip install bcrypt

##front dependency

- install nodejs
- npm init vue@latest (champ a remplir)

Activate VirtualEnv:
- export DB_USERNAME="sammy"
- export DB_PASSWORD="test"  
- add email password in __init.py file -> app.config['MAIL_PASSWORD']
- pipenv shell
- Python3 init_db.py
- python3 main.py
- Access the IP address on your browser - Ctrl C to exit
The modifications will be automatically reloaded.
The 'Debug' mode is activated

- exit to quit the virtual env

##DB Postgre
- interact with postgre: sudo psql -U agu postgres  
- CREATE DATABASE testdb;
- \c flask_db
- SELECT title, path FROM images;
- \q

-------- outils ---------
##DBata grid
