from flask import Blueprint

chats_bp = Blueprint('chats', __name__)

def create_chat_routes(app, db, socketio):
    from .routes import chat_routes
    chat_routes(chats_bp, db, socketio)
    app.register_blueprint(chats_bp, url_prefix='/chats')
