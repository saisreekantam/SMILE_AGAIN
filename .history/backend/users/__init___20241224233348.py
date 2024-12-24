from flask import Blueprint

users_bp = Blueprint('users', __name__)

def create_user_routes(app, db):
    from .routes import user_routes
    user_routes(users_bp, db)
    app.register_blueprint(users_bp, url_prefix='/users')
