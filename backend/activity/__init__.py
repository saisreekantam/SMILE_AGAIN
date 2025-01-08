from flask import Blueprint
from flask_cors import CORS

# Create blueprint for the activities routes
activities_bp = Blueprint('activities', __name__)

# Configure CORS specifically for activities routes
CORS(activities_bp, resources={
    r"/activities/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

def create_activity_routes(app, db):
    """
    Register activity routes with the Flask application.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    from .routes import register_routes
    register_routes(activities_bp, db)
    app.register_blueprint(activities_bp, url_prefix='/activities')
    
    # Initialize activity system
    from .utils import ActivityManager
    with app.app_context():
        ActivityManager.initialize_default_activities()
    
    return activities_bp