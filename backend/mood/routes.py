from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from models import MoodEntry, User
from extensions import db

mood_bp = Blueprint('mood', __name__)

@mood_bp.route('/entry', methods=['POST'])
@login_required
def create_mood_entry():
    """Create a new mood entry"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'mood_level' not in data or not isinstance(data['mood_level'], int) or \
           not (1 <= data['mood_level'] <= 5):
            return jsonify({'error': 'Valid mood level (1-5) is required'}), 400
            
        # Create new mood entry
        new_entry = MoodEntry(
            user_id=current_user.id,
            mood_level=data['mood_level'],
            emotions=data.get('emotions', []),
            notes=data.get('notes', '')
        )
        
        db.session.add(new_entry)
        db.session.commit()
        
        # Update user's current emotional state for the chatbot
        current_user.current_mood = data['mood_level']
        current_user.current_emotions = data.get('emotions', [])
        db.session.commit()
        
        return jsonify({
            'message': 'Mood entry created successfully',
            'entry': new_entry.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mood_bp.route('/history', methods=['GET'])
@login_required
def get_mood_history():
    """Get user's mood history with optional date filtering"""
    try:
        # Get query parameters for filtering
        days = request.args.get('days', default=7, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query mood entries
        entries = MoodEntry.query.filter(
            MoodEntry.user_id == current_user.id,
            MoodEntry.timestamp >= start_date
        ).order_by(MoodEntry.timestamp).all()
        
        # Calculate mood statistics
        stats = {
            'average_mood': calculate_average_mood(entries),
            'common_emotions': get_common_emotions(entries),
            'total_entries': len(entries)
        }
        
        return jsonify({
            'entries': [entry.to_dict() for entry in entries],
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mood_bp.route('/recent', methods=['GET'])
@login_required
def get_recent_mood():
    """Get user's most recent mood entry"""
    try:
        recent_entry = MoodEntry.query.filter_by(
            user_id=current_user.id
        ).order_by(MoodEntry.timestamp.desc()).first()
        
        if not recent_entry:
            return jsonify({'message': 'No mood entries found'})
            
        return jsonify(recent_entry.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_average_mood(entries):
    """Calculate average mood level from entries"""
    if not entries:
        return None
    return sum(entry.mood_level for entry in entries) / len(entries)

def get_common_emotions(entries):
    """Get most common emotions from entries"""
    if not entries:
        return []
        
    emotion_counts = {}
    for entry in entries:
        for emotion in entry.emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
    # Sort by count and return top emotions
    sorted_emotions = sorted(
        emotion_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    return [emotion for emotion, _ in sorted_emotions[:5]]  # Return top 5

def register_mood_routes(app):
    """Register mood tracking routes with the application"""
    app.register_blueprint(mood_bp, url_prefix='/mood')