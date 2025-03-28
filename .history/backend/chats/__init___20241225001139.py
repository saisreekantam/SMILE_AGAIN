from flask import Blueprint


auth_bp = Blueprint('auth', __name__)

def create_auth_routes(app, db, bcrypt, login_manager):
    from .routes import chats
    auth_routes(auth_bp, db, bcrypt, login_manager)
    app.register_blueprint(auth_bp, url_prefix='/auth')