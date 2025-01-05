# backend/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
bcrypt = Bcrypt()
socketio = SocketIO()
login_manager = LoginManager()
