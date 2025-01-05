from datetime import datetime
from sqlalchemy import JSON
from .app import db

class ChatSession(db.Model):
    """Stores information about chat sessions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    session_mood = db.Column(db.String(50))  # Overall mood of the session
    stress_level = db.Column(db.Integer)     # 1-10 scale
    messages = db.relationship('ChatMessage', backref='session', lazy=True)

class ChatMessage(db.Model):
    """Individual messages in a chat session"""
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender_type = db.Column(db.String(20))  # 'user' or 'bot'
    content = db.Column(db.Text)
    detected_emotion = db.Column(db.String(50))
    response_rating = db.Column(db.Integer)  # User feedback (1-5)
    
class EmotionalPattern(db.Model):
    """Tracks emotional patterns for users"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pattern_type = db.Column(db.String(50))  # e.g., 'daily', 'weekly'
    emotion_data = db.Column(JSON)  # Stores emotional trends
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class ResponseTemplate(db.Model):
    """Stores successful response templates"""
    id = db.Column(db.Integer, primary_key=True)
    emotion_context = db.Column(db.String(50))  # Emotion this response works well for
    stress_level = db.Column(db.Integer)        # 1-10 scale
    template_text = db.Column(db.Text)
    success_rate = db.Column(db.Float)          # Percentage of positive feedback
    use_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ConversationFlow(db.Model):
    """Tracks successful conversation patterns"""
    id = db.Column(db.Integer, primary_key=True)
    initial_emotion = db.Column(db.String(50))
    steps = db.Column(JSON)  # Array of conversation steps
    success_rate = db.Column(db.Float)
    avg_duration = db.Column(db.Integer)  # Average duration in messages
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserPreference(db.Model):
    """Stores user preferences for bot interaction"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    humor_level = db.Column(db.Integer)  # 1-5 scale
    response_style = db.Column(db.String(50))  # e.g., 'direct', 'empathetic'
    preferred_topics = db.Column(JSON)
    trigger_words = db.Column(JSON)  # Words/phrases to avoid
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class BotLearning(db.Model):
    """Stores learned patterns and improvements"""
    id = db.Column(db.Integer, primary_key=True)
    pattern_type = db.Column(db.String(50))
    pattern_data = db.Column(JSON)
    success_metric = db.Column(db.Float)
    implementation_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupportiveResource(db.Model):
    """Stores helpful resources for different situations"""
    id = db.Column(db.Integer, primary_key=True)
    resource_type = db.Column(db.String(50))  # e.g., 'article', 'exercise', 'quote'
    content = db.Column(db.Text)
    applicable_emotions = db.Column(JSON)
    stress_level_range = db.Column(JSON)  # min and max stress level
    success_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
