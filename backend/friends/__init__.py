from flask import Blueprint
from flask_cors import CORS

friends_bp = Blueprint('friends', __name__)
CORS(friends_bp, resources={r"/friends/*": {"origins": "*"}})

def create_friend_routes(app, db, socketio):
    """
    Initialize and register friend request routes
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
        socketio: Flask-SocketIO instance for real-time notifications
    """
    from .routes import register_routes
    from .events import register_friend_events
    
    # Register HTTP routes
    register_routes(app)
    
    # Register WebSocket events
    register_friend_events(socketio)
    
    # Register the blueprint with the application
    app.register_blueprint(friends_bp, url_prefix='/friends')
