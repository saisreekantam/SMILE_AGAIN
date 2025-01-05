import os
from flask import Flask
from extensions import db, bcrypt, socketio, login_manager
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Configure CORS for the application
    CORS(app, 
         resources={
             r"/auth/*": {
                 "origins": "http://localhost:3000",
                 "methods": ["GET", "POST", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True
             },
             r"/smilebot/*": {  # Add CORS for smilebot routes
                 "origins": "http://localhost:3000",
                 "methods": ["GET", "POST", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True
             }
         }
    )

    # Configure application
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(basedir, 'users.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.urandom(24),
        # Add configurations for file uploads (needed for facial analysis)
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
        UPLOAD_FOLDER=os.path.join(basedir, 'uploads')
    )

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
        from smilebot import create_smilebot_routes  # Import smilebot routes

        # Initialize blueprints
        create_auth_routes(app, db, bcrypt, login_manager)
        create_user_routes(app, db)
        create_chat_routes(app, db, socketio)
        create_smilebot_routes(app, db)  # Initialize smilebot routes

        # Create tables if they don't exist
        db.create_all()

        # Register error handlers
        @app.errorhandler(413)
        def too_large(e):
            return {"error": "File is too large"}, 413

        @app.errorhandler(500)
        def internal_error(e):
            db.session.rollback()
            return {"error": "Internal server error"}, 500

        @app.errorhandler(404)
        def not_found(e):
            return {"error": "Resource not found"}, 404

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Run the application with debugging enabled on port 8000
    socketio.run(app, debug=True, port=8000, cors_allowed_origins="http://localhost:3000")
