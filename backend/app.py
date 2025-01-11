# app.py
import os
import logging
from typing import Optional
from flask import Flask, request, jsonify, Blueprint, make_response, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager
from mood import create_mood_routes
from models import init_auth,User
from extensions import db, bcrypt, socketio, login_manager
from datetime import timedelta
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app():
    app = Flask(__name__)
    
    CORS(app, resources={r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "expose_headers": ["Access-Control-Allow-Origin"],
        "max_age": 3600
    }})

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

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="http://localhost:3000")
   
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        if not user_id:
            return None
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({
            'error': 'Authentication required',
            'message': 'Please log in to access this resource',
            'login_required': True
        }), 401
    with app.app_context():
        from models import User, SessionLog, UserProblem, Profile, Message, Group, ChatRequest, GroupJoinRequest, Blog
        db.create_all()
        
        from auth.routes import register_routes as register_auth_routes
        from users.routes import register_routes as register_user_routes
        from chats.routes import register_routes as register_chat_routes
        from bot.routes import register_routes as register_bot_routes
        from blogs.routes import blogs_bp
        from workshops.routes import workshops_bp
        from friends.routes import register_profile_routes
        from community import create_community_routes
        from activity.routes import register_routes
        from meditation.routes import register_meditation_routes
        from models import MeditationSession, MeditationPreset, MeditationStreak
        from smile_journey.routes import register_journey_routes
        from games.routes import register_routes
        register_routes(app, db)
        register_journey_routes(app, db)
        meditation_bp = Blueprint('meditation', __name__)
        register_meditation_routes(meditation_bp, db)
        app.register_blueprint(meditation_bp, url_prefix='/meditation')
        activities_bp = Blueprint('activities', __name__, url_prefix='/activities')
        auth_bp = Blueprint('auth', __name__)
        users_bp = Blueprint('users', __name__)
        chats_bp = Blueprint('chats', __name__)
        bot_bp = Blueprint('bot', __name__)
        profile_bp=Blueprint('friends',__name__)
        register_routes(activities_bp, db)
        create_mood_routes(app, db)
        create_community_routes(app, db)
        register_auth_routes(auth_bp, db, bcrypt, login_manager)
        register_user_routes(users_bp, db)
        register_chat_routes(chats_bp, db, socketio)
        register_bot_routes(bot_bp, db)
        register_profile_routes(profile_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(users_bp, url_prefix='/users')
        app.register_blueprint(chats_bp, url_prefix='/chats')
        app.register_blueprint(bot_bp, url_prefix='/bot')
        app.register_blueprint(blogs_bp)
        app.register_blueprint(activities_bp)
        app.register_blueprint(workshops_bp, url_prefix='/workshops')
        app.register_blueprint(profile_bp, url_prefix='/profile')
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    @app.route('/upload/image', methods=['POST'])
    def upload_image():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return jsonify({
                'message': 'File uploaded successfully',
                'url': f'/uploads/{filename}'
            })
            
        return jsonify({'error': 'File type not allowed'}), 400

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app

app = create_app()
print(app.url_map)
if __name__ == '__main__':
    try:
        socketio.run(app, debug=True, port=8000, host='127.0.0.1', allow_unsafe_werkzeug=True)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise