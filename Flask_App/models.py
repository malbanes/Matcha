from flask_login import UserMixin

class User(UserMixin, object):
    """Wraps User object for Flask-Login"""
    def __init__(self, user):
        self._user = user
        self.id = user[0]
        self.name = user[4] + ' ' + user[5]
        self.email = user[6]
        self.username = user[1]