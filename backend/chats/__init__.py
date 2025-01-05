from flask import Blueprint

chats_bp = Blueprint('chats', __name__)

def create_chat_routes(app, db, socketio):
    """Initialize chats blueprint and register routes"""
    # Import the routes function
    from .routes import register_routes
    
    # Register the routes with the blueprint
    register_routes(chats_bp, db, socketio)
    
    # Register the blueprint with the app
    app.register_blueprint(chats_bp, url_prefix='/chats')
