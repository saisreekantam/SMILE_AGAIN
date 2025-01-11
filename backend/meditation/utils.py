# meditation/utils.py
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
from models import User, MeditationSession, MeditationPreset
from dataclasses import dataclass
import json

@dataclass
class MeditationStats:
    total_sessions: int
    total_minutes: int
    longest_streak: int
    current_streak: int
    average_duration: float
    favorite_duration: int
    completion_rate: float

class MeditationManager:
    """Comprehensive meditation session and progress management system"""
    
    def __init__(self, db):
        self.db = db
        self.preset_durations = [5, 10, 15, 20, 30, 45, 60]
        self.default_ambient_sounds = [
            'rain', 'ocean', 'forest', 'white_noise', 'tibetan_bells'
        ]

    def create_session(self, user_id: int, duration: int, 
                      ambient_sound: Optional[str] = None) -> Dict:
        """Create a new meditation session"""
        try:
            # Validate duration
            if duration not in self.preset_durations:
                raise ValueError("Invalid meditation duration")

            # Create session record
            session = MeditationSession(
                user_id=user_id,
                duration=duration,
                ambient_sound=ambient_sound,
                started_at=datetime.utcnow()
            )
            self.db.session.add(session)
            self.db.session.commit()

            return {
                'session_id': session.id,
                'duration': duration,
                'ambient_sound': ambient_sound,
                'started_at': session.started_at.isoformat()
            }

        except Exception as e:
            self.db.session.rollback()
            raise Exception(f"Error creating meditation session: {str(e)}")

    def complete_session(self, session_id: int, actual_duration: int) -> Dict:
        """Complete a meditation session and record progress"""
        try:
            session = MeditationSession.query.get(session_id)
            if not session:
                raise ValueError("Session not found")

            session.completed_at = datetime.utcnow()
            session.actual_duration = actual_duration
            session.completion_status = 'completed'

            # Update user's meditation stats
            self._update_user_stats(session.user_id, actual_duration)
            
            self.db.session.commit()

            return {
                'session_id': session.id,
                'planned_duration': session.duration,
                'actual_duration': actual_duration,
                'completion_status': 'completed',
                'achievements': self._check_achievements(session.user_id)
            }

        except Exception as e:
            self.db.session.rollback()
            raise Exception(f"Error completing meditation session: {str(e)}")

    def get_user_stats(self, user_id: int) -> MeditationStats:
        """Get comprehensive meditation statistics for a user"""
        try:
            sessions = MeditationSession.query.filter_by(
                user_id=user_id,
                completion_status='completed'
            ).all()

            if not sessions:
                return MeditationStats(
                    total_sessions=0,
                    total_minutes=0,
                    longest_streak=0,
                    current_streak=0,
                    average_duration=0,
                    favorite_duration=0,
                    completion_rate=0
                )

            # Calculate streaks
            current_streak, longest_streak = self._calculate_streaks(sessions)

            # Calculate favorite duration
            duration_counts = {}
            for session in sessions:
                duration_counts[session.duration] = duration_counts.get(session.duration, 0) + 1
            favorite_duration = max(duration_counts.items(), key=lambda x: x[1])[0]

            # Calculate completion rate
            all_sessions = MeditationSession.query.filter_by(user_id=user_id).count()
            completed_sessions = len(sessions)
            completion_rate = (completed_sessions / all_sessions) * 100 if all_sessions > 0 else 0

            return MeditationStats(
                total_sessions=completed_sessions,
                total_minutes=sum(session.actual_duration for session in sessions),
                longest_streak=longest_streak,
                current_streak=current_streak,
                average_duration=sum(session.actual_duration for session in sessions) / len(sessions),
                favorite_duration=favorite_duration,
                completion_rate=completion_rate
            )

        except Exception as e:
            raise Exception(f"Error getting meditation stats: {str(e)}")

    def _calculate_streaks(self, sessions: List[MeditationSession]) -> tuple:
        """Calculate current and longest meditation streaks"""
        if not sessions:
            return 0, 0

        # Sort sessions by date
        sorted_sessions = sorted(sessions, key=lambda x: x.completed_at)
        
        # Calculate streaks
        current_streak = 1
        longest_streak = 1
        temp_streak = 1
        
        for i in range(1, len(sorted_sessions)):
            prev_date = sorted_sessions[i-1].completed_at.date()
            curr_date = sorted_sessions[i].completed_at.date()
            
            if (curr_date - prev_date).days == 1:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 1
                
        # Check if current streak is still active
        if (datetime.utcnow().date() - sorted_sessions[-1].completed_at.date()).days <= 1:
            current_streak = temp_streak
        else:
            current_streak = 0
            
        return current_streak, longest_streak

    def _update_user_stats(self, user_id: int, duration: int) -> None:
        """Update user's meditation statistics"""
        # Implementation for updating user stats
        pass

    def _check_achievements(self, user_id: int) -> List[Dict]:
        """Check and award meditation-related achievements"""
        stats = self.get_user_stats(user_id)
        achievements = []

        # Session count achievements
        session_milestones = {
            5: "Meditation Beginner",
            20: "Regular Meditator",
            50: "Meditation Enthusiast",
            100: "Meditation Master"
        }

        for count, title in session_milestones.items():
            if stats.total_sessions >= count:
                achievements.append({
                    'type': 'meditation',
                    'title': title,
                    'description': f"Completed {count} meditation sessions!"
                })

        # Streak achievements
        if stats.current_streak >= 7:
            achievements.append({
                'type': 'streak',
                'title': "Week of Zen",
                'description': "Maintained a 7-day meditation streak!"
            })

        return achievements

    def get_recommended_sessions(self, user_id: int) -> List[Dict]:
        """Get personalized session recommendations"""
        stats = self.get_user_stats(user_id)
        
        recommendations = []
        
        # Based on favorite duration
        recommendations.append({
            'duration': stats.favorite_duration,
            'type': 'Favorite',
            'ambient_sound': 'tibetan_bells',
            'description': "Your most successful duration"
        })
        
        # Based on time of day
        current_hour = datetime.utcnow().hour
        if 5 <= current_hour <= 9:
            recommendations.append({
                'duration': 15,
                'type': 'Morning',
                'ambient_sound': 'forest',
                'description': "Perfect for morning mindfulness"
            })
        elif 14 <= current_hour <= 16:
            recommendations.append({
                'duration': 10,
                'type': 'Afternoon',
                'ambient_sound': 'white_noise',
                'description': "Quick afternoon reset"
            })
        
        return recommendations