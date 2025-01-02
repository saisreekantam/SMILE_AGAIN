from flask_login import current_user
from backend.models import User

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return {'error': 'Admin access required'}, 403
        return f(*args, **kwargs)
    return decorated_function

def get_online_users():
    
    return [
        {"id": user.id, "name": user.name}
        for user in User.query.filter_by(is_online=True).all()
        if user.id != current_user.id
    ]