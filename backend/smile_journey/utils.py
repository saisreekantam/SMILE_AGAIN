from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func
from models import (
    JourneyPath, JourneyMilestone, UserJourneyProgress,
    User, Group, UserProblem, db
)
import logging

logger = logging.getLogger(__name__)

class JourneyManager:
    """Utility class for managing journey-related operations"""
    
    @staticmethod
    def initialize_default_journey(community_id: int) -> Optional[JourneyPath]:
        """Initialize default journey path for a community"""
        try:
            # Check if journey already exists
            existing_path = JourneyPath.query.filter_by(community_id=community_id).first()
            if existing_path:
                return existing_path

            # Create new journey path
            path = JourneyPath(
                community_id=community_id,
                name="Stress Relief Journey",
                description="A step-by-step journey to manage your stress and find your smile again",
                total_milestones=7,
                coins_per_milestone=50
            )
            db.session.add(path)
            db.session.flush()

            # Define milestones
            milestones = [
                {
                    "title": "Begin Your Journey",
                    "description": "Complete the initial assessment and set your goals",
                    "order_number": 1,
                    "milestone_type": "reflection",
                    "coins_reward": 50,
                    "required_days": 1
                },
                {
                    "title": "Daily Positivity",
                    "description": "Record three positive moments each day for 3 days",
                    "order_number": 2,
                    "milestone_type": "activity",
                    "coins_reward": 75,
                    "required_days": 3
                },
                {
                    "title": "Connect and Share",
                    "description": "Share your experience with a community member",
                    "order_number": 3,
                    "milestone_type": "connection",
                    "coins_reward": 100,
                    "required_days": 1
                },
                {
                    "title": "Stress Management",
                    "description": "Learn and practice three stress management techniques",
                    "order_number": 4,
                    "milestone_type": "activity",
                    "coins_reward": 125,
                    "required_days": 4
                },
                {
                    "title": "Reflection Point",
                    "description": "Reflect on your progress and identify growth areas",
                    "order_number": 5,
                    "milestone_type": "reflection",
                    "coins_reward": 150,
                    "required_days": 1
                },
                {
                    "title": "Community Support",
                    "description": "Participate in group activities and support others",
                    "order_number": 6,
                    "milestone_type": "connection",
                    "coins_reward": 175,
                    "required_days": 5
                },
                {
                    "title": "Journey Champion",
                    "description": "Complete your journey and celebrate your progress",
                    "order_number": 7,
                    "milestone_type": "reflection",
                    "coins_reward": 200,
                    "required_days": 1
                }
            ]

            for milestone_data in milestones:
                milestone = JourneyMilestone(path_id=path.id, **milestone_data)
                db.session.add(milestone)

            db.session.commit()
            return path

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error initializing journey: {str(e)}")
            return None

    @staticmethod
    def calculate_streak(user_id: int, path_id: int) -> int:
        """Calculate user's current streak for a journey"""
        progress = UserJourneyProgress.query.filter_by(
            user_id=user_id,
            path_id=path_id
        ).first()

        if not progress or not progress.last_activity_date:
            return 0

        today = datetime.utcnow().date()
        last_activity = progress.last_activity_date.date()
        days_diff = (today - last_activity).days

        if days_diff > 1:  # Streak broken if more than 1 day gap
            progress.current_streak = 0
            db.session.commit()
            return 0

        return progress.current_streak

    @staticmethod
    def get_milestone_requirements(milestone_id: int) -> Dict:
        """Get requirements for completing a milestone"""
        milestone = JourneyMilestone.query.get(milestone_id)
        if not milestone:
            return {}

        base_requirements = {
            'type': milestone.milestone_type,
            'required_days': milestone.required_days,
            'required_activities': milestone.required_activities
        }

        # Add type-specific requirements
        if milestone.milestone_type == 'reflection':
            base_requirements['min_words'] = 50
        elif milestone.milestone_type == 'connection':
            base_requirements['interaction_type'] = ['comment', 'message', 'group_activity']
        elif milestone.milestone_type == 'activity':
            base_requirements['completion_proof'] = True

        return base_requirements

    @staticmethod
    def get_journey_analytics(user_id: int) -> Dict:
        """Get comprehensive analytics for user's journey progress"""
        try:
            progress_entries = UserJourneyProgress.query.filter_by(user_id=user_id).all()
            
            total_coins = sum(p.total_coins_earned for p in progress_entries)
            total_milestones = sum(p.completed_milestones for p in progress_entries)
            active_journeys = len(progress_entries)
            
            # Calculate completion rates
            completion_rates = []
            for progress in progress_entries:
                path = JourneyPath.query.get(progress.path_id)
                if path:
                    rate = (progress.completed_milestones / path.total_milestones) * 100
                    completion_rates.append(rate)
            
            avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0
            
            return {
                'total_coins': total_coins,
                'total_milestones': total_milestones,
                'active_journeys': active_journeys,
                'average_completion': round(avg_completion, 2),
                'highest_streak': max((p.current_streak for p in progress_entries), default=0)
            }
            
        except Exception as e:
            logger.error(f"Error getting journey analytics: {str(e)}")
            return {}

    @staticmethod
    def check_milestone_completion(user_id: int, milestone_id: int, data: Dict) -> Tuple[bool, str]:
        """Validate if milestone completion requirements are met"""
        try:
            milestone = JourneyMilestone.query.get(milestone_id)
            if not milestone:
                return False, "Milestone not found"

            # Get user's progress
            progress = UserJourneyProgress.query.filter_by(
                user_id=user_id,
                path_id=milestone.path_id
            ).first()

            if not progress:
                return False, "Journey not started"

            if milestone.order_number != progress.current_milestone:
                return False, "Cannot skip milestones"

            # Type-specific validation
            if milestone.milestone_type == 'reflection':
                if not data.get('reflection_text'):
                    return False, "Reflection text required"
                if len(data['reflection_text'].split()) < 50:
                    return False, "Reflection must be at least 50 words"

            elif milestone.milestone_type == 'activity':
                if not data.get('completed_activities'):
                    return False, "Activity completion proof required"
                if len(data['completed_activities']) < milestone.required_activities:
                    return False, "Not enough activities completed"

            elif milestone.milestone_type == 'connection':
                if not data.get('interactions'):
                    return False, "Connection proof required"
                if len(data['interactions']) < milestone.required_activities:
                    return False, "Not enough community interactions"

            return True, "Requirements met"

        except Exception as e:
            logger.error(f"Error checking milestone completion: {str(e)}")
            return False, str(e)

    @staticmethod
    def get_recommended_actions(user_id: int) -> List[Dict]:
        """Get personalized recommended actions based on user's progress"""
        try:
            progress_entries = UserJourneyProgress.query.filter_by(user_id=user_id).all()
            recommendations = []

            for progress in progress_entries:
                current_milestone = JourneyMilestone.query.filter_by(
                    path_id=progress.path_id,
                    order_number=progress.current_milestone
                ).first()

                if current_milestone:
                    # Add milestone-specific recommendations
                    recommendations.append({
                        'type': 'milestone',
                        'title': f"Complete {current_milestone.title}",
                        'description': current_milestone.description,
                        'reward': current_milestone.coins_reward
                    })

                # Check streak
                if not progress.last_activity_date or \
                   (datetime.utcnow() - progress.last_activity_date).days >= 1:
                    recommendations.append({
                        'type': 'streak',
                        'title': 'Maintain Your Streak',
                        'description': 'Complete an activity today to maintain your progress streak!',
                        'reward': 25
                    })

            return recommendations[:3]  # Return top 3 recommendations

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return []