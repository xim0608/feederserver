# flaskr/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('flaskr.config')
# app.config.from_pyfile('config.py')
# bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

import flaskr.views

# from .models import User

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "signin"


# @login_manager.user_loader
# def load_user(userid):
#     return User.query.filter(User.id == userid).first()