from flask import jsonify
from flask_login import current_user
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, 'is_admin', False):  # Using getattr for safety
            return jsonify({
                'error': 'Permission denied',
                'message': 'This feature requires admin privileges',
                'code': 'ADMIN_REQUIRED'
            }), 403
            
        return f(*args, **kwargs)
    return decorated_function
