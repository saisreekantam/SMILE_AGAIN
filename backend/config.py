# config.py
import os
from datetime import timedelta

class Config:
    # Base configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', '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')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    JSON_SORT_KEYS = False
    
    # Security settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS settings
    CORS_ORIGINS = ["http://localhost:3000"]
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOWED_HEADERS = ["Content-Type", "Authorization"]
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    
    # Socket.IO settings
    SOCKETIO_CORS_ORIGINS = ["http://localhost:3000"]
    
    # OpenAI settings (for bot)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Emotion detection settings
    EMOTION_DETECTION_ENABLED = True
    EMOTION_DETECTION_THRESHOLD = 0.7

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    # Add any production-specific settings here

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}