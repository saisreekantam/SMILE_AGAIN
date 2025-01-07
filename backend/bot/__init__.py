from flask import Blueprint
from flask_cors import CORS

emotionalbot_bp = Blueprint('emotionalbot', __name__)
CORS(emotionalbot_bp, resources={r"/emotionalbot/*": {"origins": "*"}})

def create_emotionalbot_routes(app, db, socketio):
    """Initialize emotional bot routes and WebSocket handlers"""
    from .routes import emotionalbot_routes
    emotionalbot_routes(emotionalbot_bp, db, socketio)
    app.register_blueprint(emotionalbot_bp, url_prefix='/emotionalbot')
