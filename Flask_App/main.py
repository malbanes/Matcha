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


@main.route('/uploadajax', methods = ['POST'])
def upldfile():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('There is no file')
            return ("KO")
        file1 = request.files['file']
        if file1 :
            path = os.path.join('./static/public', file1.filename)
            file1.save(path)
            print(path)
            return ("OK")
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

        if (gender) :
            return {
            'gender': gender,
            'orient': orient
        }
        if (orient) :
            return {
            'gender': gender,
            'orient': orient
        }
        else:
            return ("KO")

@main.route('/newhashtag', methods = ['POST'])
def addhash():
    if request.method == 'POST':
        if 'hashtag' not in request.form:
            flash('There is no tag')
            return ("KO")
        else:
            tag = request.form['hashtag']
            return (tag)

@main.route('/updatehashtag', methods = ['POST'])
def updhash():
    if request.method == 'POST':
        cknames = request.form.getlist("check")
        if (cknames):
            for ckname in cknames:
                print (ckname)
            if (ckname) :
                return (ckname)
        else:
            return ("KO")

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