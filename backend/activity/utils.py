from typing import List, Dict, Optional
from datetime import datetime, timedelta
from models import Activity, UserActivity, ActivityStreak
from extensions import db

class ActivityManager:
    """
    Comprehensive utility class for managing activities and recommendations
    """
    DEFAULT_ACTIVITIES = {
        'anxiety': [
            {
                'title': 'Mindful Breathing Exercise',
                'description': 'A gentle breathing exercise: Breathe in for 4 counts, hold for 4, and exhale for 4. Repeat this 3 times. 🌬️',
                'category': 'meditation',
                'duration_minutes': 5,
                'difficulty_level': 'easy',
                'resources_needed': 'A quiet space'
            },
            {
                'title': '5-4-3-2-1 Grounding Technique',
                'description': 'Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste 🌟',
                'category': 'mindfulness',
                'duration_minutes': 10,
                'difficulty_level': 'easy',
                'resources_needed': 'None'
            },
            {
                'title': 'Peaceful Place Visualization',
                'description': 'Imagine your favorite peaceful place - maybe a beach or garden. Focus on the sights and sounds there 🏖️',
                'category': 'visualization',
                'duration_minutes': 15,
                'difficulty_level': 'easy',
                'resources_needed': 'A comfortable place to sit or lie down'
            }
        ],
        'depression': [
            {
                'title': 'Tiny Joy Journal',
                'description': 'Write down three tiny moments of joy from your day, no matter how small they seem 📝',
                'category': 'reflection',
                'duration_minutes': 10,
                'difficulty_level': 'easy',
                'resources_needed': 'Journal and pen'
            },
            {
                'title': 'Sunshine and Steps',
                'description': 'Take a short walk outside, focusing on the warmth of the sun and the rhythm of your steps 🌞',
                'category': 'physical',
                'duration_minutes': 15,
                'difficulty_level': 'medium',
                'resources_needed': 'Comfortable walking shoes'
            },
            {
                'title': 'Color Your Emotions',
                'description': 'Express your feelings through colors and shapes - no artistic skill needed! Just let the colors flow 🎨',
                'category': 'creative',
                'duration_minutes': 20,
                'difficulty_level': 'easy',
                'resources_needed': 'Paper and colored pencils/markers'
            }
        ],
        'stress': [
            {
                'title': 'Tea Mindfulness Ritual',
                'description': 'Prepare and drink a cup of tea mindfully, focusing on each sensation and the calming process 🫖',
                'category': 'mindfulness',
                'duration_minutes': 15,
                'difficulty_level': 'easy',
                'resources_needed': 'Tea and a quiet moment'
            },
            {
                'title': 'Tension Release Progressive Relaxation',
                'description': 'Systematically tense and relax each muscle group, releasing physical and mental tension 💆‍♀️',
                'category': 'relaxation',
                'duration_minutes': 20,
                'difficulty_level': 'medium',
                'resources_needed': 'Comfortable place to lie down'
            },
            {
                'title': 'Nature's Symphony',
                'description': 'Find a spot near nature and close your eyes. Focus on identifying different natural sounds 🌿',
                'category': 'mindfulness',
                'duration_minutes': 10,
                'difficulty_level': 'easy',
                'resources_needed': 'Access to outdoors or nature sounds recording'
            }
        ],
        'loneliness': [
            {
                'title': 'Self-Care Letter',
                'description': 'Write a compassionate letter to yourself, acknowledging your feelings and offering kind words 💌',
                'category': 'self-care',
                'duration_minutes': 15,
                'difficulty_level': 'medium',
                'resources_needed': 'Paper and pen'
            },
            {
                'title': 'Memory Album Creation',
                'description': 'Create a digital or physical collection of happy memories with loved ones 📸',
                'category': 'creative',
                'duration_minutes': 30,
                'difficulty_level': 'medium',
                'resources_needed': 'Photos or memory items'
            },
            {
                'title': 'Comfort Playlist',
                'description': 'Create a playlist of songs that make you feel connected and understood 🎵',
                'category': 'music',
                'duration_minutes': 20,
                'difficulty_level': 'easy',
                'resources_needed': 'Music player or streaming service'
            }
        ],
        'overwhelmed': [
            {
                'title': 'Task Declutter',
                'description': 'Break down one overwhelming task into tiny, manageable steps ✍️',
                'category': 'organization',
                'duration_minutes': 15,
                'difficulty_level': 'medium',
                'resources_needed': 'Paper and pen'
            },
            {
                'title': 'Five-Minute Reset',
                'description': 'Set a timer for 5 minutes and do absolutely nothing. Just observe your thoughts without judgment ⏰',
                'category': 'meditation',
                'duration_minutes': 5,
                'difficulty_level': 'easy',
                'resources_needed': 'Timer'
            },
            {
                'title': 'Worry Box',
                'description': 'Write down your worries and physically put them in a box, symbolically setting them aside 📦',
                'category': 'coping',
                'duration_minutes': 10,
                'difficulty_level': 'easy',
                'resources_needed': 'Paper, pen, and a box or container'
            }
        ]
    }

    @classmethod
    def initialize_default_activities(cls) -> None:
        """Initialize the database with default activities if empty"""
        try:
            if Activity.query.first() is None:
                for activity_data in cls.DEFAULT_ACTIVITIES:
                    activity = Activity(**activity_data)
                    db.session.add(activity)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to initialize activities: {str(e)}")

    @staticmethod
    def get_personalized_activities(user_id: int, mood_tag: str, limit: int = 5) -> List[Dict]:
        """Get personalized activity recommendations based on user history and mood"""
        try:
            # Get user's completed activities and their effectiveness
            completed_activities = UserActivity.query.filter_by(
                user_id=user_id,
                completed_at__isnot=None
            ).order_by(UserActivity.effectiveness_rating.desc()).all()

            # Get effective categories for this user
            effective_categories = set()
            if completed_activities:
                for ua in completed_activities:
                    activity = Activity.query.get(ua.activity_id)
                    if ua.effectiveness_rating and ua.effectiveness_rating >= 4:
                        effective_categories.add(activity.category)

            # Build query for recommendations
            query = Activity.query.filter(Activity.mood_tags.contains(mood_tag))

            # Prioritize activities from effective categories
            if effective_categories:
                query = query.order_by(
                    Activity.category.in_(list(effective_categories)).desc(),
                    Activity.created_at.desc()
                )
            else:
                query = query.order_by(Activity.created_at.desc())

            activities = query.limit(limit).all()

            return [{
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'category': activity.category,
                'duration_minutes': activity.duration_minutes,
                'difficulty_level': activity.difficulty_level,
                'resources_needed': activity.resources_needed,
                'recommended_reason': 'Based on your previous positive experiences' 
                    if activity.category in effective_categories else 'Matched to your current mood'
            } for activity in activities]

        except Exception as e:
            raise Exception(f"Error getting personalized activities: {str(e)}")

    @staticmethod
    def track_activity_completion(
        user_id: int,
        activity_id: int,
        mood_improvement: int,
        effectiveness_rating: int
    ) -> Dict:
        """Track activity completion and update user's streak"""
        try:
            # Update or create streak
            streak = ActivityStreak.query.filter_by(user_id=user_id).first()
            if not streak:
                streak = ActivityStreak(user_id=user_id)
                db.session.add(streak)

            completion_time = datetime.utcnow()
            streak.update_streak(completion_time)

            # Calculate achievements
            achievements = []
            if streak.current_streak == 7:
                achievements.append("7-Day Streak Achievement Unlocked!")
            if streak.total_activities_completed == 10:
                achievements.append("Activity Master Achievement Unlocked!")
            if mood_improvement >= 3:
                achievements.append("Mood Booster Achievement Unlocked!")

            db.session.commit()

            return {
                'streak': streak.current_streak,
                'total_completed': streak.total_activities_completed,
                'achievements': achievements
            }

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error tracking activity completion: {str(e)}")

    @staticmethod
    def get_activity_insights(user_id: int) -> Dict:
        """Get insights about user's activity patterns and effectiveness"""
        try:
            completed_activities = UserActivity.query.filter_by(
                user_id=user_id,
                completed_at__isnot=None
            ).all()

            if not completed_activities:
                return {
                    'total_activities': 0,
                    'average_mood_improvement': 0,
                    'most_effective_category': None,
                    'recommendation': "Try your first activity to start tracking your progress!"
                }

            # Calculate insights
            mood_improvements = []
            category_effectiveness = {}

            for ua in completed_activities:
                activity = Activity.query.get(ua.activity_id)
                if ua.mood_before and ua.mood_after:
                    improvement = ua.mood_after - ua.mood_before
                    mood_improvements.append(improvement)

                    if activity.category not in category_effectiveness:
                        category_effectiveness[activity.category] = []
                    category_effectiveness[activity.category].append(improvement)

            # Calculate averages per category
            category_averages = {
                category: sum(improvements) / len(improvements)
                for category, improvements in category_effectiveness.items()
            }

            most_effective_category = max(category_averages.items(), key=lambda x: x[1])[0]

            return {
                'total_activities': len(completed_activities),
                'average_mood_improvement': sum(mood_improvements) / len(mood_improvements),
                'most_effective_category': most_effective_category,
                'recommendation': f"Activities in the {most_effective_category} category seem to work best for you!"
            }

        except Exception as e:
            raise Exception(f"Error getting activity insights: {str(e)}")
    