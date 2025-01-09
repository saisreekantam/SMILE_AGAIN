from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta, date
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm.session import Session
from models import Activity, UserActivity, ActivityStreak, User
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActivityRecommender:
    """Handles personalized activity recommendations based on user history and preferences."""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_recommendations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get personalized activity recommendations for a user.
        
        Args:
            user_id: User's ID
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended activities with metadata
        """
        try:
            # Get user's completed activities
            completed_activities = UserActivity.query.filter(
                UserActivity.user_id == user_id,
                UserActivity.completed_at.isnot(None)
            ).all()

            # Calculate category effectiveness
            category_effectiveness = defaultdict(list)
            for ua in completed_activities:
                activity = Activity.query.get(ua.activity_id)
                if ua.effectiveness_rating:
                    category_effectiveness[activity.category].append(
                        ua.effectiveness_rating
                    )

            # Get average effectiveness per category
            category_scores = {
                cat: sum(ratings)/len(ratings)
                for cat, ratings in category_effectiveness.items()
            }

            recommended = []
            if category_scores:
                # Prioritize effective categories
                best_categories = sorted(
                    category_scores.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:2]

                for category, score in best_categories:
                    activities = Activity.query.filter(
                        Activity.category == category,
                        ~Activity.id.in_([ua.activity_id for ua in completed_activities])
                    ).limit(limit//2).all()

                    recommended.extend([{
                        **activity.to_dict(),
                        'recommendation_reason': f'Based on your success with {category} activities'
                    } for activity in activities])

            # Fill remaining slots with new activities
            remaining = limit - len(recommended)
            if remaining > 0:
                new_activities = Activity.query.filter(
                    ~Activity.id.in_([r['id'] for r in recommended])
                ).order_by(func.random()).limit(remaining).all()

                recommended.extend([{
                    **activity.to_dict(),
                    'recommendation_reason': 'Try something new!'
                } for activity in new_activities])

            return recommended

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []

class ActivityManager:
    """Main interface for activity-related operations."""
    
    DEFAULT_ACTIVITIES = {
        'anxiety': [
            {
                'title': 'Mindful Breathing',
                'description': 'Simple breathing exercise for anxiety relief',
                'category': 'meditation',
                'duration_minutes': 10,
                'difficulty_level': 'easy',
                'mood_tags': ['anxiety', 'stress'],
                'resources_needed': 'Quiet space'
            }
        ],
        'stress': [
            {
                'title': 'Progressive Relaxation',
                'description': 'Systematic muscle relaxation technique',
                'category': 'relaxation',
                'duration_minutes': 15,
                'difficulty_level': 'medium',
                'mood_tags': ['stress', 'anxiety'],
                'resources_needed': 'Comfortable space'
            }
        ],
        'mood': [
            {
                'title': 'Gratitude Journal',
                'description': 'Write three things youre grateful for',
                'category': 'reflection',
                'duration_minutes': 10,
                'difficulty_level': 'easy',
                'mood_tags': ['mood', 'depression'],
                'resources_needed': 'Journal and pen'
            }
        ]
    }

    def __init__(self, db_session: Session):
        self.db = db_session
        self.recommender = ActivityRecommender(db_session)

    @classmethod
    def initialize_default_activities(cls, db: Session) -> None:
        """Initialize database with default activities if empty."""
        try:
            if Activity.query.first() is None:
                for mood_category, activities in cls.DEFAULT_ACTIVITIES.items():
                    for activity_data in activities:
                        activity = Activity(**activity_data)
                        db.session.add(activity)
                db.session.commit()
                logger.info("Default activities initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing default activities: {str(e)}")
            db.session.rollback()

    def start_activity(self, user_id: int, activity_id: int, mood_before: float) -> Dict[str, Any]:
        """Start a new activity session."""
        try:
            activity = Activity.query.get(activity_id)
            if not activity:
                return {'error': 'Activity not found'}, 404

            user_activity = UserActivity(
                user_id=user_id,
                activity_id=activity_id,
                mood_before=mood_before,
                started_at=datetime.utcnow()
            )
            self.db.session.add(user_activity)
            self.db.session.commit()

            return {
                'success': True,
                'user_activity_id': user_activity.id,
                'message': 'Activity started successfully'
            }

        except Exception as e:
            logger.error(f"Error starting activity: {str(e)}")
            self.db.session.rollback()
            return {'error': str(e)}

    def complete_activity(
        self, 
        user_id: int, 
        user_activity_id: int, 
        mood_after: float,
        effectiveness_rating: int
    ) -> Dict[str, Any]:
        """Complete an activity session and update streak."""
        try:
            user_activity = UserActivity.query.get(user_activity_id)
            if not user_activity or user_activity.user_id != user_id:
                return {'error': 'Activity session not found'}, 404

            if user_activity.completed_at:
                return {'error': 'Activity already completed'}, 400

            # Update activity completion
            user_activity.completed_at = datetime.utcnow()
            user_activity.mood_after = mood_after
            user_activity.effectiveness_rating = effectiveness_rating

            # Update streak
            streak = ActivityStreak.query.filter_by(user_id=user_id).first()
            if not streak:
                streak = ActivityStreak(user_id=user_id)
                self.db.session.add(streak)

            streak.update_streak(user_activity.completed_at)
            
            self.db.session.commit()

            return {
                'success': True,
                'message': 'Activity completed successfully',
                'streak': streak.current_streak,
                'mood_improvement': mood_after - user_activity.mood_before
            }

        except Exception as e:
            logger.error(f"Error completing activity: {str(e)}")
            self.db.session.rollback()
            return {'error': str(e)}

    def get_activity_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive activity statistics for a user."""
        try:
            # Get user's streak info
            streak = ActivityStreak.query.filter_by(user_id=user_id).first()
            
            # Get completed activities
            completed_activities = UserActivity.query.filter(
                UserActivity.user_id == user_id,
                UserActivity.completed_at.isnot(None)
            ).all()

            # Calculate mood improvements
            mood_improvements = []
            for activity in completed_activities:
                if activity.mood_before and activity.mood_after:
                    mood_improvements.append(activity.mood_after - activity.mood_before)

            # Get recent activity trend
            recent_activities = UserActivity.query.filter(
                UserActivity.user_id == user_id,
                UserActivity.completed_at.isnot(None)
            ).order_by(
                UserActivity.completed_at.desc()
            ).limit(7).all()

            activity_trend = [{
                'date': ua.completed_at.strftime('%Y-%m-%d'),
                'mood_improvement': ua.mood_after - ua.mood_before 
                    if ua.mood_after and ua.mood_before else 0,
                'effectiveness': ua.effectiveness_rating or 0
            } for ua in recent_activities]

            return {
                'streak_stats': {
                    'current_streak': streak.current_streak if streak else 0,
                    'longest_streak': streak.longest_streak if streak else 0,
                    'total_completed': len(completed_activities)
                },
                'mood_stats': {
                    'average_improvement': sum(mood_improvements) / len(mood_improvements) 
                        if mood_improvements else 0,
                    'activities_with_improvement': len([i for i in mood_improvements if i > 0])
                },
                'recent_trend': activity_trend
            }

        except Exception as e:
            logger.error(f"Error getting activity stats: {str(e)}")
            return {
                'streak_stats': {'current_streak': 0, 'longest_streak': 0, 'total_completed': 0},
                'mood_stats': {'average_improvement': 0, 'activities_with_improvement': 0},
                'recent_trend': []
            }