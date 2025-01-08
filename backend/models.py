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
    
    # Define the many-to-many relationship for friends
    friends = db.relationship(
        'User', 
        secondary='friendship',
        primaryjoin='User.id==Friendship.user_id',
        secondaryjoin='User.id==Friendship.friend_id',
        backref=db.backref('friend_of', lazy='dynamic')
    )
 
class Friendship(db.Model):
    """Model for managing friendships between users"""
    __tablename__ = 'friendship'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FriendRequest(db.Model):
    """Model for managing friend requests between users"""
    __tablename__ = 'friend_request'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500))  # Optional message with friend request
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_requests')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_requests')

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


# Add these to backend_models.py

# backend_models.py
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import relationship
from extensions import db
from flask_login import UserMixin

class Blog(db.Model):
    """
    Blog model for storing user blog posts.
    
    This model represents the core blog functionality, matching the existing
    database schema exactly to prevent migration issues.
    
    Attributes:
        id (int): Primary key for the blog post
        user_id (int): Foreign key reference to the user table
        title (str): Title of the blog post
        content (str): Main content of the blog post
        created_at (datetime): Timestamp of post creation
    """
    __tablename__ = 'blog'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert blog post to dictionary representation."""
        return {
            'blog_id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'created_by': self.user_id
        }

# In backend_models.py or wherever your models are defined

class Notification(db.Model):
    """
    Model for storing user notifications including friend requests.
    Each notification represents an event that needs user attention.
    """
    __tablename__ = 'notification'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'friend_request', 'message', etc.
    content = db.Column(db.Text, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    related_id = db.Column(db.Integer, nullable=True)  # For storing related entity IDs (e.g., friendship_id)

    # Relationships
    recipient = db.relationship(
        'User',
        foreign_keys=[recipient_id],
        backref=db.backref('received_notifications', lazy='dynamic')
    )
    
    sender = db.relationship(
        'User',
        foreign_keys=[sender_id],
        backref=db.backref('sent_notifications', lazy='dynamic')
    )

    def to_dict(self):
        """Convert notification to dictionary format"""
        return {
            'id': self.id,
            'type': self.type,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat(),
            'sender': {
                'id': self.sender_id,
                'name': User.query.get(self.sender_id).name
            } if self.sender_id else None,
            'related_id': self.related_id
        }

    @staticmethod
    def create_friend_request_notification(friendship):
        """
        Create a notification for a new friend request.
        
        Args:
            friendship (Friendship): The friendship request instance
        """
        notification = Notification(
            recipient_id=friendship.friend_id,
            sender_id=friendship.user_id,
            type='friend_request',
            content=f"{User.query.get(friendship.user_id).name} sent you a friend request",
            related_id=friendship.id
        )
        db.session.add(notification)
        db.session.commit()
class Comment(db.Model):
    """
    Comment model for storing blog comments.
    
    Attributes:
        id (int): Primary key for the comment
        content (str): Content of the comment
        created_at (datetime): Timestamp of comment creation
        user_id (int): Foreign key reference to user table
        blog_id (int): Foreign key reference to blog table
    """
    __tablename__ = 'comment'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert comment to dictionary representation."""
        return {
            'comment_id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'blog_id': self.blog_id
        }
class BlogInteraction(db.Model):
    _tablename_ = 'blog_interaction'
    
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    interaction_type = db.Column(db.String(10), nullable=False)  # 'like' or 'dislike'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    _table_args_ = (
        db.UniqueConstraint('blog_id', 'user_id', name='unique_blog_interaction'),
    )

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
class Workshop(db.Model):
    __tablename__ = 'workshop'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    banner_url = db.Column(db.String(200), nullable=False)
    meet_link = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, default=0.0)
    is_paid = db.Column(db.Boolean, default=False)
    sponsored = db.Column(db.Boolean, default=False)
    tag = db.Column(db.String(50), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_workshops')
    feedback = db.relationship('Feedback', backref='workshop', lazy='dynamic')

class Feedback(db.Model):
    __tablename__ = 'feedback'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshop.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.Column(db.Text)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 rating scale
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Add unique constraint to ensure one feedback per user per workshop
    __table_args__ = (
        db.UniqueConstraint('workshop_id', 'user_id', name='unique_workshop_feedback'),
        {'extend_existing': True}
    )
from datetime import datetime
from extensions import db

class Community(db.Model):
    __tablename__ = 'community'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    smile_reason = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    members = db.relationship('User', secondary='community_members', backref='communities')

# Association table for community members
community_members = db.Table('community_members',
    db.Column('community_id', db.Integer, db.ForeignKey('community.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow),
    extend_existing=True
)

class CommunityPost(db.Model):
    __tablename__ = 'community_post'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('community.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    
    # Relationship to get user information
    author = db.relationship('User', backref='community_posts')
    
class CommunityComment(db.Model):
    __tablename__ = 'community_comment'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='community_comments')
    post = db.relationship('CommunityPost', backref='comments')
class Activity(db.Model):
    """Model for predefined activities"""
    __tablename__ = 'activity'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'meditation', 'exercise', 'creative'
    mood_tags = db.Column(db.String(200))  # Comma-separated tags matching smile reasons
    duration_minutes = db.Column(db.Integer)
    difficulty_level = db.Column(db.String(20))  # 'easy', 'medium', 'hard'
    resources_needed = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserActivity(db.Model):
    """Model for tracking user activity participation"""
    __tablename__ = 'user_activity'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    mood_before = db.Column(db.Integer)  # Scale of 1-10
    mood_after = db.Column(db.Integer)  # Scale of 1-10
    feedback = db.Column(db.Text)
    effectiveness_rating = db.Column(db.Integer)  # Scale of 1-5

class ActivityStreak(db.Model):
    """Model for tracking user activity streaks"""
    __tablename__ = 'activity_streak'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.DateTime)
    total_activities_completed = db.Column(db.Integer, default=0)
    
    def update_streak(self, activity_date):
        """Update streak based on new activity completion"""
        if not self.last_activity_date:
            self.current_streak = 1
        else:
            days_diff = (activity_date - self.last_activity_date).days
            if days_diff <= 1:  # Maintain or increment streak
                self.current_streak += 1
            else:  # Reset streak
                self.current_streak = 1
                
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
            
        self.last_activity_date = activity_date
        self.total_activities_completed += 1
class MoodEntry(db.Model):
    __tablename__ = 'mood_entry'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_level = db.Column(db.Integer, nullable=False)  # 1-5 scale
    emotions = db.Column(db.JSON)  # Store selected emotion tags
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add relationship to User model
    user = db.relationship('User', backref=db.backref('mood_entries', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'mood_level': self.mood_level,
            'emotions': self.emotions,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat(),
        }
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