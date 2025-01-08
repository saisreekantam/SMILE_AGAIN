from flask import Blueprint

community_bp = Blueprint('community', __name__)

def create_community_routes(app, db):
    """
    Register community routes with the Flask application.
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
    """
    from .routes import register_community_routes
    register_community_routes(community_bp, db)
    app.register_blueprint(community_bp, url_prefix='/community')