from datetime import datetime
from typing import Any, Dict, Optional
from flask import Flask, jsonify
from flask_login import LoginManager, UserMixin
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    gender = db.Column(db.String(20))

class SessionLog(db.Model):
    __tablename__ = 'session_log'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class UserProblem(db.Model):
    __tablename__ = 'user_problem'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    smile_last_time = db.Column(db.String(200))
    smile_reason = db.Column(db.String(500))

class Profile(db.Model):
    __tablename__ = 'profile'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    profile_pic = db.Column(db.String(200), default='static/default.jpg')
    description = db.Column(db.Text, nullable=True)

class Friendship(db.Model):
    __tablename__ = 'friendship'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')

class Blog(db.Model):
    """
    Blog model for storing user blog posts with essential fields
    """
    __tablename__ = 'blog'
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Required fields
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('blogs', lazy=True))

    def __init__(self, title: str, content: str, user_id: int) -> None:
        """
        Initialize a new blog post
        
        Args:
            title (str): The blog post title
            content (str): The blog post content
            user_id (int): The ID of the user who created the post
        """
        self.title = title
        self.content = content
        self.user_id = user_id

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert blog post to dictionary representation
        
        Returns:
            Dict[str, Any]: Dictionary containing blog post data
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

   
class Comment(db.Model):
    __tablename__ = 'comment'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    
    # Add relationship to User model
    author = db.relationship('User', backref='comments')

class Like(db.Model):
    __tablename__ = 'like'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'message'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Group(db.Model):
    __tablename__ = 'group'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    members = db.relationship('User', secondary='group_members', backref='groups')

group_members = db.Table('group_members',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    extend_existing=True
)

class GroupJoinRequest(db.Model):
    __tablename__ = 'group_join_request'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatRequest(db.Model):
    __tablename__ = 'chat_request'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.LargeBinary)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
class AuthConfig:
    """
    Handles authentication configuration and setup for Flask application
    """
    def __init__(self, app: Flask, user_model: Any):
        """
        Initialize authentication configuration
        
        Args:
            app (Flask): Flask application instance
            user_model (Any): User model class for authentication
        """
        self.app = app
        self.user_model = user_model
        self.login_manager = LoginManager()
        self.setup_login_manager()

    def setup_login_manager(self) -> None:
        """
        Configure LoginManager with all necessary settings
        """
        # Initialize login manager with app
        self.login_manager.init_app(self.app)
        
        # Set the login view to handle unauthorized access
        self.login_manager.login_view = 'auth.login'
        
        # Configure login manager to return JSON response for unauthorized access
        @self.login_manager.unauthorized_handler
        def unauthorized() -> tuple:
            return jsonify({
                'error': 'Authentication required',
                'message': 'Please log in to access this resource',
                'login_required': True
            }), 401

        # User loader callback
        @self.login_manager.user_loader
        def load_user(user_id: str) -> Optional[Any]:
            if not user_id:
                return None
            return self.user_model.query.get(int(user_id))

def init_auth(app: Flask, user_model: Any) -> LoginManager:
    """
    Initialize authentication for Flask application
    
    Args:
        app (Flask): Flask application instance
        user_model (Any): User model class
    
    Returns:
        LoginManager: Configured login manager instance
    """
    auth_config = AuthConfig(app, user_model)
    return auth_config.login_manager