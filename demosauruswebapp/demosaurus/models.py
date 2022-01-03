"""User login for Flask - Demosaurus.

source: https://learnpyjs.blogspot.com/2021/02/how-to-setup-user-login-in-flask.html?m=1
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db_users = SQLAlchemy()


class UserModel(UserMixin, db_users.Model):
    __tablename__ = 'users'

    id = db_users.Column(db_users.Integer, primary_key=True)
    email = db_users.Column(db_users.String(80), unique=True)
    username = db_users.Column(db_users.String(100))
    password_hash = db_users.Column(db_users.String())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
