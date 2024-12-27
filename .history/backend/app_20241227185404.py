from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from flask_socketio import SocketIO
from auth import create_auth_routes
from users import create_user_routes
from chats import create_chat_routes

app = Flask(__name__)
CORS(app,origins="http://localhost:3000")
app.config.from_object('config')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Register auth routes
create_auth_routes(app, db, bcrypt, login_manager)
create_user_routes(app, db)
create_chat_routes(app, db, socketio)
create_workshop_routes(app, db)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    app.run(debug=True,port=8000)






