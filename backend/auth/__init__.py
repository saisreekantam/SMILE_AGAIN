from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

def create_auth_routes(app, db, bcrypt, login_manager):
    """Initialize auth blueprint and register routes"""
    # Import the routes function
    from .routes import register_routes
    
    # Register the routes with the blueprint
    register_routes(auth_bp, db, bcrypt, login_manager)
    
    # Register the blueprint with the app
    app.register_blueprint(auth_bp, url_prefix='/auth')
