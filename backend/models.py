from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from flask import Flask, jsonify
from flask_login import LoginManager, UserMixin
from sqlalchemy import func
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
class MeditationMetrics:
    """Data class for meditation statistics"""
    total_minutes: int
    session_count: int
    average_duration: float
    completion_rate: float
    current_streak: int
    longest_streak: int

class MeditationSession(db.Model):
    """Model for storing meditation session data with comprehensive tracking"""
    __tablename__ = 'meditation_session'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Planned duration in minutes
    actual_duration = db.Column(db.Integer)  # Actual duration in minutes
    ambient_sound = db.Column(db.String(50))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    completion_status = db.Column(db.String(20), default='started')  
    mood_before = db.Column(db.Integer)  # Scale 1-10
    mood_after = db.Column(db.Integer)   # Scale 1-10
    notes = db.Column(db.Text)
    interruption_count = db.Column(db.Integer, default=0)
    focus_rating = db.Column(db.Integer)  # Scale 1-5
    
    # Relationships
    user = db.relationship('User', backref=db.backref('meditation_sessions', lazy=True))
    preset = db.relationship('MeditationPreset', backref='sessions', lazy=True)
    preset_id = db.Column(db.Integer, db.ForeignKey('meditation_preset.id'))

    @property
    def duration_minutes(self) -> int:
        """Get session duration in minutes"""
        if self.completed_at and self.started_at:
            return int((self.completed_at - self.started_at).total_seconds() / 60)
        return 0

    @property
    def is_completed(self) -> bool:
        """Check if session was completed"""
        return self.completion_status == 'completed'

    @property
    def mood_improvement(self) -> Optional[int]:
        """Calculate mood improvement if both ratings exist"""
        if self.mood_before is not None and self.mood_after is not None:
            return self.mood_after - self.mood_before
        return None

    def complete_session(self, actual_duration: int, mood_after: int, 
                        focus_rating: int, notes: Optional[str] = None) -> None:
        """Mark session as complete with final metrics"""
        self.completed_at = datetime.utcnow()
        self.actual_duration = actual_duration
        self.mood_after = mood_after
        self.focus_rating = focus_rating
        self.notes = notes
        self.completion_status = 'completed'

    def to_dict(self) -> Dict:
        """Convert session to dictionary for API responses"""
        return {
            'id': self.id,
            'duration': self.duration,
            'actual_duration': self.actual_duration,
            'ambient_sound': self.ambient_sound,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.completion_status,
            'mood_improvement': self.mood_improvement,
            'focus_rating': self.focus_rating,
            'notes': self.notes
        }

class MeditationPreset(db.Model):
    """Model for storing user's meditation presets with enhanced customization"""
    __tablename__ = 'meditation_preset'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    ambient_sound = db.Column(db.String(50))
    background_theme = db.Column(db.String(50), default='nature')
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime)
    use_count = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    is_guided = db.Column(db.Boolean, default=False)
    guide_voice = db.Column(db.String(50))
    interval_bells = db.Column(db.Boolean, default=False)
    bell_interval = db.Column(db.Integer)  # Interval in minutes
    
    # Relationships
    user = db.relationship('User', backref=db.backref('meditation_presets', lazy=True))

    def increment_usage(self) -> None:
        """Update preset usage statistics"""
        self.use_count += 1
        self.last_used_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        """Convert preset to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'duration': self.duration,
            'ambient_sound': self.ambient_sound,
            'background_theme': self.background_theme,
            'is_favorite': self.is_favorite,
            'is_guided': self.is_guided,
            'guide_voice': self.guide_voice,
            'interval_bells': self.interval_bells,
            'bell_interval': self.bell_interval,
            'use_count': self.use_count,
            'last_used': self.last_used_at.isoformat() if self.last_used_at else None
        }

class MeditationStreak(db.Model):
    """Model for tracking meditation streaks with detailed statistics"""
    __tablename__ = 'meditation_streak'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_meditation_date = db.Column(db.Date)
    total_sessions = db.Column(db.Integer, default=0)
    total_minutes = db.Column(db.Integer, default=0)
    streak_start_date = db.Column(db.Date)
    weekly_goal = db.Column(db.Integer, default=7)  # Sessions per week goal
    monthly_minutes_goal = db.Column(db.Integer, default=500)  # Minutes per month
    
    # Relationships
    user = db.relationship('User', backref=db.backref('meditation_streak', uselist=False))

    def update_streak(self, meditation_date: datetime) -> None:
        """Update streak information based on new meditation session"""
        today = meditation_date.date()
        
        if not self.last_meditation_date:
            self.current_streak = 1
            self.streak_start_date = today
        else:
            days_difference = (today - self.last_meditation_date).days
            
            if days_difference <= 1:  # Consecutive day
                self.current_streak += 1
            else:  # Streak broken
                self.current_streak = 1
                self.streak_start_date = today
        
        self.last_meditation_date = today
        self.longest_streak = max(self.current_streak, self.longest_streak)
        self.total_sessions += 1

    def add_session_minutes(self, minutes: int) -> None:
        """Add completed session minutes to total"""
        self.total_minutes += minutes

    def get_weekly_progress(self) -> Dict:
        """Calculate progress towards weekly goals"""
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        
        weekly_sessions = MeditationSession.query.filter(
            MeditationSession.user_id == self.user_id,
            func.date(MeditationSession.completed_at) >= week_start,
            MeditationSession.completion_status == 'completed'
        ).count()

        return {
            'sessions_completed': weekly_sessions,
            'sessions_goal': self.weekly_goal,
            'progress_percentage': (weekly_sessions / self.weekly_goal) * 100
        }

    def get_monthly_progress(self) -> Dict:
        """Calculate progress towards monthly goals"""
        today = datetime.utcnow().date()
        month_start = today.replace(day=1)
        
        monthly_minutes = db.session.query(
            func.sum(MeditationSession.actual_duration)
        ).filter(
            MeditationSession.user_id == self.user_id,
            func.date(MeditationSession.completed_at) >= month_start,
            MeditationSession.completion_status == 'completed'
        ).scalar() or 0

        return {
            'minutes_completed': monthly_minutes,
            'minutes_goal': self.monthly_minutes_goal,
            'progress_percentage': (monthly_minutes / self.monthly_minutes_goal) * 100
        }

    def to_dict(self) -> Dict:
        """Convert streak data to dictionary for API responses"""
        return {
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'total_sessions': self.total_sessions,
            'total_minutes': self.total_minutes,
            'streak_start': self.streak_start_date.isoformat() if self.streak_start_date else None,
            'last_meditation': self.last_meditation_date.isoformat() if self.last_meditation_date else None,
            'weekly_progress': self.get_weekly_progress(),
            'monthly_progress': self.get_monthly_progress()
        }

# Add to User model (assuming it exists)
def add_to_user_model():
    """Add meditation-related properties to User model"""
    
    @property
    def meditation_metrics(self) -> MeditationMetrics:
        """Calculate comprehensive meditation metrics for user"""
        completed_sessions = MeditationSession.query.filter_by(
            user_id=self.id,
            completion_status='completed'
        ).all()
        
        total_minutes = sum(session.actual_duration for session in completed_sessions)
        session_count = len(completed_sessions)
        average_duration = total_minutes / session_count if session_count > 0 else 0
        
        all_sessions = MeditationSession.query.filter_by(user_id=self.id).count()
        completion_rate = (session_count / all_sessions * 100) if all_sessions > 0 else 0
        
        streak = self.meditation_streak
        current_streak = streak.current_streak if streak else 0
        longest_streak = streak.longest_streak if streak else 0
        
        return MeditationMetrics(
            total_minutes=total_minutes,
            session_count=session_count,
            average_duration=average_duration,
            completion_rate=completion_rate,
            current_streak=current_streak,
            longest_streak=longest_streak
        )
    
    # Add this property to User model
    User.meditation_metrics = meditation_metrics
class JourneyPath(db.Model):
    """Model for different journey paths available in communities"""
    __tablename__ = 'journey_path'
    
    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    total_milestones = db.Column(db.Integer, default=0)
    coins_per_milestone = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JourneyMilestone(db.Model):
    """Model for individual milestones in a journey path"""
    __tablename__ = 'journey_milestone'
    
    id = db.Column(db.Integer, primary_key=True)
    path_id = db.Column(db.Integer, db.ForeignKey('journey_path.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order_number = db.Column(db.Integer, nullable=False)
    coins_reward = db.Column(db.Integer, default=50)
    required_days = db.Column(db.Integer, default=1)
    required_activities = db.Column(db.Integer, default=1)
    
    # Define what type of milestone this is
    milestone_type = db.Column(db.String(50), default='activity')  # activity, reflection, connection
    
    # Additional requirements based on type
    activity_type = db.Column(db.String(50))  # meditation, exercise, etc.
    reflection_prompt = db.Column(db.Text)
    connection_requirement = db.Column(db.String(100))

class UserJourneyProgress(db.Model):
    """Model to track user progress in journey paths"""
    __tablename__ = 'user_journey_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    path_id = db.Column(db.Integer, db.ForeignKey('journey_path.id'))
    current_milestone = db.Column(db.Integer, db.ForeignKey('journey_milestone.id'))
    completed_milestones = db.Column(db.Integer, default=0)
    total_coins_earned = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity_date = db.Column(db.DateTime)
    current_streak = db.Column(db.Integer, default=0)
    
    # Relationship
    progress_details = db.relationship('MilestoneProgress', backref='user_progress', lazy=True)

class MilestoneProgress(db.Model):
    """Model to track detailed progress for each milestone"""
    __tablename__ = 'milestone_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_progress_id = db.Column(db.Integer, db.ForeignKey('user_journey_progress.id'))
    milestone_id = db.Column(db.Integer, db.ForeignKey('journey_milestone.id'))
    activities_completed = db.Column(db.Integer, default=0)
    days_active = db.Column(db.Integer, default=0)
    reflection_submitted = db.Column(db.Boolean, default=False)
    connections_made = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    coins_earned = db.Column(db.Integer, default=0)

class UserCoins(db.Model):
    """Model to track user's coin balance and transactions"""
    __tablename__ = 'user_coins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    balance = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class CoinTransaction(db.Model):
    """Model to track coin transactions"""
    __tablename__ = 'coin_transaction'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(50))  # earned, spent
    source = db.Column(db.String(100))  # milestone, activity, bonus
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
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
    """Activity model representing wellness activities users can perform."""
    __tablename__ = 'activity'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    difficulty_level = db.Column(db.String(20), nullable=False)
    mood_tags = db.Column(db.JSON)  # Store as JSON array of mood tags
    resources_needed = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert activity to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'duration_minutes': self.duration_minutes,
            'difficulty_level': self.difficulty_level,
            'mood_tags': self.mood_tags,
            'resources_needed': self.resources_needed
        }

class UserActivity(db.Model):
    """Model tracking user's activity sessions and progress."""
    __tablename__ = 'user_activity'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    mood_before = db.Column(db.Float)  # Scale of 1-10
    mood_after = db.Column(db.Float)   # Scale of 1-10
    effectiveness_rating = db.Column(db.Integer)  # Scale of 1-5
    notes = db.Column(db.Text)

    # Reference the Activity model
    activity = db.relationship('Activity', backref=db.backref('user_activities', lazy=True))

    def to_dict(self):
        """Convert user activity to dictionary representation."""
        return {
            'id': self.id,
            'activity_id': self.activity_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'mood_before': self.mood_before,
            'mood_after': self.mood_after,
            'effectiveness_rating': self.effectiveness_rating,
            'notes': self.notes
        }

class ActivityStreak(db.Model):
    """Model tracking user's activity completion streaks."""
    __tablename__ = 'activity_streak'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    total_activities_completed = db.Column(db.Integer, default=0)

    def update_streak(self, completion_time: datetime):
        """
        Update streak based on activity completion.
        
        Args:
            completion_time: Datetime when activity was completed
        """
        today = completion_time.date()
        
        if not self.last_activity_date:
            self.current_streak = 1
        elif (today - self.last_activity_date).days == 1:
            self.current_streak += 1
        elif (today - self.last_activity_date).days > 1:
            self.current_streak = 1
        # If completed on same day, streak stays the same
        
        self.longest_streak = max(self.longest_streak, self.current_streak)
        self.last_activity_date = today
        self.total_activities_completed += 1

    def to_dict(self):
        """Convert streak info to dictionary representation."""
        return {
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'total_activities_completed': self.total_activities_completed,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None
        }
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