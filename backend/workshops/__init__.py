from flask import Blueprint

workshops_bp = Blueprint('workshops', __name__)

def create_workshop_routes(app, db):
    from .routes import workshop_routes
    workshop_routes(workshops_bp, db)
    app.register_blueprint(workshops_bp, url_prefix='/workshops')
