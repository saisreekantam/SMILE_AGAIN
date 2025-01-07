from flask import Blueprint

workshops_bp = Blueprint('workshops', __name__)

# Import routes after creating blueprint to avoid circular imports
from . import routes