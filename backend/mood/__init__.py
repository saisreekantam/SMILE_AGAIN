from flask import Blueprint
from flask_cors import CORS

# Create blueprint for mood routes
mood_bp = Blueprint('mood', __name__)

# Configure CORS specifically for mood routes
CORS(mood_bp, resources={
    r"/mood/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

def create_mood_routes(app, db):
    """
    Register mood tracking routes with the Flask application.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    from .routes import register_mood_routes
    register_mood_routes(mood_bp)
    app.register_blueprint(mood_bp, url_prefix='/mood')
    
    # Initialize any required mood tracking components
    return mood_bp