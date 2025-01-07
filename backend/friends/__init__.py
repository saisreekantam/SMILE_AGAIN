from flask import Blueprint

profile_bp = Blueprint('profile', __name__)

def create_profile_routes(app, db):
    """
    Register profile routes with the Flask application.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    from .routes import register_profile_routes
    register_profile_routes(profile_bp)
    app.register_blueprint(profile_bp, url_prefix='/profile')