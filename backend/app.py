# app.py
import os
import logging
from flask import Flask, request, jsonify, Blueprint, make_response
from flask_cors import CORS
from extensions import db, bcrypt, socketio, login_manager
from datetime import timedelta
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Single CORS configuration
    CORS(app, 
         resources={
             r"/*": {
                 "origins": ["http://localhost:3000"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True,
                 "expose_headers": ["Access-Control-Allow-Origin"],
                 "max_age": 3600
             }
         })

    # Configure application
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'users.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY='your-secret-key-here',
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        UPLOAD_FOLDER=os.path.join(basedir, 'uploads'),
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        JSON_SORT_KEYS=False
    )

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="http://localhost:3000")
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Remove any custom CORS handlers from here
    # We'll let Flask-CORS handle everything

    with app.app_context():
        # Import models
        from models import (
            User, SessionLog, UserProblem, Profile, 
            Message, Group, ChatRequest, GroupJoinRequest
        )
        
        # Create database tables
        db.create_all()
        
        # Create and register blueprints
        from auth.routes import register_routes as register_auth_routes
        from users.routes import register_routes as register_user_routes
        from chats.routes import register_routes as register_chat_routes
        from bot.routes import register_routes as register_bot_routes

        # Initialize blueprints
        auth_bp = Blueprint('auth', __name__)
        users_bp = Blueprint('users', __name__)
        chats_bp = Blueprint('chats', __name__)
        bot_bp = Blueprint('bot', __name__)

        # Register routes
        register_auth_routes(auth_bp, db, bcrypt, login_manager)
        register_user_routes(users_bp, db)
        register_chat_routes(chats_bp, db, socketio)
        register_bot_routes(bot_bp, db)

        # Register blueprints
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(users_bp, url_prefix='/users')
        app.register_blueprint(chats_bp, url_prefix='/chats')
        app.register_blueprint(bot_bp, url_prefix='/bot')

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    try:
        socketio.run(
            app,
            debug=True,
            port=8000,
            host='127.0.0.1',
            allow_unsafe_werkzeug=True
        )
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise