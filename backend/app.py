import os
from flask import Flask
from extensions import db, bcrypt, socketio, login_manager
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, 
         resources={
             r"/auth/*": {
                 "origins": "http://localhost:3000",
                 "methods": ["GET", "POST", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"]
             }
         },
         supports_credentials=True
    )


    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'users.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
        SECRET_KEY=os.urandom(24)
    )

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    with app.app_context():
        # Import models
        from models import User, SessionLog, UserProblem, Profile
        
        # Import and register blueprints
        from auth import create_auth_routes
        from users import create_user_routes
        from chats import create_chat_routes

        # Initialize blueprints
        create_auth_routes(app, db, bcrypt, login_manager)
        create_user_routes(app, db)
        create_chat_routes(app, db, socketio)

        # Create tables
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8000)
