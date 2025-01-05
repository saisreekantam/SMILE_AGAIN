from flask import Blueprint

users_bp = Blueprint('users', __name__)

def create_user_routes(app, db):
    """Initialize users blueprint and register routes"""
    # Import the routes function
    from .routes import register_routes
    
    # Register the routes with the blueprint
    register_routes(users_bp, db)
    
    # Register the blueprint with the app
    app.register_blueprint(users_bp, url_prefix='/users')
