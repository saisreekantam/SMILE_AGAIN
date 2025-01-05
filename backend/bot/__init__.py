from flask import Blueprint
from flask_cors import CORS

smilebot_bp = Blueprint('smilebot', __name__)
CORS(smilebot_bp, resources={r"/smilebot/*": {"origins": "http://localhost:3000"}})

def create_smilebot_routes(app, db):
    from .routes import smilebot_routes
    smilebot_routes(smilebot_bp, db)
    app.register_blueprint(smilebot_bp, url_prefix='/smilebot')
