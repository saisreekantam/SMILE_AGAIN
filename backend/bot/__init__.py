# bot/__init__.py
from flask import Blueprint
from flask_cors import CORS

# Create blueprint for the bot routes
bot_bp = Blueprint('bot', __name__)

# Configure CORS specifically for bot routes
CORS(bot_bp, resources={
    r"/bot/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

def create_bot_routes(app, db):
    """
    Register bot routes with the Flask application.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    from .routes import register_routes
    register_routes(bot_bp, db)
    app.register_blueprint(bot_bp, url_prefix='/bot')
    return bot_bp