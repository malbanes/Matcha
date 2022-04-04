from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user

from flask_mail import Mail

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

# we initialize our flask app using the  __init__.py function 
app = create_app()
# setup Mail
mail = Mail(app)     
if __name__ == '__main__':
    ##db.create_all(app=create_app())
    app.run(debug=True)