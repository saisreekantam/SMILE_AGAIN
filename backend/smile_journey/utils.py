from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import func
from models import (
    JourneyPath, JourneyMilestone, UserJourneyProgress,
    MilestoneProgress, UserCoins, CoinTransaction, Group
)
from extensions import db

class JourneyManager:
    """Utility class for managing journey paths and milestones"""
    
    @staticmethod
    def initialize_grade_stress_path(community_id: int) -> JourneyPath:
        """Initialize the grade stress journey path with its milestones"""
        try:
            # Create the journey path
            path = JourneyPath(
                community_id=community_id,
                name="Grade Stress Relief Journey",
                description="A step-by-step journey to manage academic stress and improve your grades",
                total_milestones=7,
                coins_per_milestone=50
            )
            db.session.add(path)
            db.session.flush()  # Get the path ID
            
            # Define milestones
            milestones = [
                {
                    "title": "Start Your Journey",
                    "description": "Complete the initial stress assessment and set your academic goals",
                    "order_number": 1,
                    "milestone_type": "reflection",
                    "coins_reward": 50,
                    "required_days": 1,
                    "required_activities": 1,
                    "reflection_prompt": "What specific academic situations cause you the most stress?"
                },
                {
                    "title": "Study Break Master",
                    "description": "Learn and practice the Pomodoro Technique for 3 study sessions",
                    "order_number": 2,
                    "milestone_type": "activity",
                    "coins_reward": 75,
                    "required_days": 3,
                    "required_activities": 3,
                    "activity_type": "study_technique"
                },
                {
                    "title": "Mindful Student",
                    "description": "Complete 5 mindfulness exercises before study sessions",
                    "order_number": 3,
                    "milestone_type": "activity",
                    "coins_reward": 100,
                    "required_days": 5,
                    "required_activities": 5,
                    "activity_type": "mindfulness"
                },
                {
                    "title": "Study Buddy Connection",
                    "description": "Connect with 2 peers from your community for study sessions",
                    "order_number": 4,
                    "milestone_type": "connection",
                    "coins_reward": 150,
                    "required_activities": 2,
                    "connection_requirement": "study_partner"
                },
                {
                    "title": "Progress Reflection",
                    "description": "Reflect on your study habits and stress management progress",
                    "order_number": 5,
                    "milestone_type": "reflection",
                    "coins_reward": 100,
                    "required_days": 1,
                    "required_activities": 1,
                    "reflection_prompt": "How have your study habits and stress levels changed?"
                },
                {
                    "title": "Stress-Free Study Group",
                    "description": "Create or join a study group and complete 3 group sessions",
                    "order_number": 6,
                    "milestone_type": "connection",
                    "coins_reward": 200,
                    "required_activities": 3,
                    "connection_requirement": "study_group"
                },
                {
                    "title": "Academic Balance Master",
                    "description": "Complete the journey by maintaining a study-life balance for a week",
                    "order_number": 7,
                    "milestone_type": "activity",
                    "coins_reward": 300,
                    "required_days": 7,
                    "required_activities": 7,
                    "activity_type": "balance"
                }
            ]
            
            # Create milestone records
            for milestone_data in milestones:
                milestone = JourneyMilestone(
                    path_id=path.id,
                    **milestone_data
                )
                db.session.add(milestone)
            
            db.session.commit()
            return path
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to initialize grade stress path: {str(e)}")

    @staticmethod
    def calculate_streak(user_id: int, path_id: int) -> int:
        """Calculate the current streak for a user's journey"""
        progress = UserJourneyProgress.query.filter_by(
            user_id=user_id,
            path_id=path_id
        ).first()
        
        if not progress or not progress.last_activity_date:
            return 0
            
        today = datetime.utcnow().date()
        last_activity = progress.last_activity_date.date()
        
        if (today - last_activity).days > 1:
            # Streak broken
            progress.current_streak = 0
            db.session.commit()
            return 0
            
        return progress.current_streak

    @staticmethod
    def award_bonus_coins(user_id: int, amount: int, reason: str) -> Dict:
        """Award bonus coins to a user"""
        try:
            user_coins = UserCoins.query.filter_by(user_id=user_id).first()
            if not user_coins:
                user_coins = UserCoins(user_id=user_id)
                db.session.add(user_coins)
            
            user_coins.balance += amount
            user_coins.last_updated = datetime.utcnow()
            
            # Record transaction
            transaction = CoinTransaction(
                user_id=user_id,
                amount=amount,
                transaction_type='earned',
                source='bonus',
                description=reason
            )
            db.session.add(transaction)
            db.session.commit()
            
            return {
                'coins_awarded': amount,
                'new_balance': user_coins.balance,
                'reason': reason
            }
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to award bonus coins: {str(e)}")

    @staticmethod
    def get_journey_stats(user_id: int, path_id: int) -> Dict:
        """Get comprehensive statistics for a user's journey"""
        try:
            progress = UserJourneyProgress.query.filter_by(
                user_id=user_id,
                path_id=path_id
            ).first()
            
            if not progress:
                return {
                    'started': False,
                    'message': 'Journey not started'
                }
            
            path = JourneyPath.query.get(path_id)
            completion_percentage = (progress.completed_milestones / path.total_milestones) * 100
            
            # Get milestone completion timeline
            milestone_timeline = []
            for detail in progress.progress_details:
                if detail.completed:
                    milestone = JourneyMilestone.query.get(detail.milestone_id)
                    milestone_timeline.append({
                        'milestone': milestone.title,
                        'completed_at': detail.completed_at.isoformat(),
                        'coins_earned': detail.coins_earned
                    })
            
            return {
                'started': True,
                'completion_percentage': completion_percentage,
                'current_streak': progress.current_streak,
                'total_coins_earned': progress.total_coins_earned,
                'milestone_timeline': milestone_timeline,
                'time_in_journey': (datetime.utcnow() - progress.started_at).days,
                'active_days': len(set(detail.completed_at.date() 
                    for detail in progress.progress_details 
                    if detail.completed_at))
            }
            
        except Exception as e:
            raise Exception(f"Failed to get journey stats: {str(e)}")

class ActivityValidator:
    """Utility class for validating journey activities"""
    
    @staticmethod
    def validate_study_session(data: Dict) -> Tuple[bool, str]:
        """Validate a study session activity"""
        required_fields = ['duration_minutes', 'subject', 'technique_used']
        
        if not all(field in data for field in required_fields):
            return False, "Missing required fields"
            
        if not isinstance(data['duration_minutes'], int) or data['duration_minutes'] < 15:
            return False, "Study session must be at least 15 minutes"
            
        return True, "Valid study session"

    @staticmethod
    def validate_reflection(data: Dict) -> Tuple[bool, str]:
        """Validate a reflection submission"""
        if 'content' not in data or len(data['content'].strip()) < 100:
            return False, "Reflection must be at least 100 characters"
            
        return True, "Valid reflection"

    @staticmethod
    def validate_connection(data: Dict) -> Tuple[bool, str]:
        """Validate a connection activity"""
        required_fields = ['connection_type', 'peer_id', 'activity_description']
        
        if not all(field in data for field in required_fields):
            return False, "Missing required fields"
            
        if data['connection_type'] not in ['study_partner', 'study_group']:
            return False, "Invalid connection type"
            
        return True, "Valid connection"