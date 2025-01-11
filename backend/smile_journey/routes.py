from typing import Dict, List, Optional, Tuple
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError
from http import HTTPStatus

from models import (
    JourneyPath, JourneyMilestone, UserJourneyProgress,
    MilestoneProgress, UserCoins, CoinTransaction, User, Group
)
from extensions import db

# Configure logging
logger = logging.getLogger(__name__)

class ActivityValidator:
    """Validator for journey activities"""
    
    @staticmethod
    def validate_activity(activity_type: str, data: Dict) -> Tuple[bool, str]:
        """
        Validate activity data based on type.
        
        Args:
            activity_type: Type of activity to validate
            data: Activity data to validate
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        if activity_type == 'study_session':
            return ActivityValidator._validate_study_session(data)
        elif activity_type == 'reflection':
            return ActivityValidator._validate_reflection(data)
        elif activity_type == 'connection':
            return ActivityValidator._validate_connection(data)
        return False, 'Invalid activity type'

    @staticmethod
    def _validate_study_session(data: Dict) -> Tuple[bool, str]:
        required_fields = ['duration_minutes', 'subject', 'technique_used']
        if not all(field in data for field in required_fields):
            return False, "Missing required fields"
        if not isinstance(data['duration_minutes'], int) or data['duration_minutes'] < 15:
            return False, "Study session must be at least 15 minutes"
        return True, "Valid study session"

    @staticmethod
    def _validate_reflection(data: Dict) -> Tuple[bool, str]:
        if 'content' not in data or len(data['content'].strip()) < 100:
            return False, "Reflection must be at least 100 characters"
        return True, "Valid reflection"

    @staticmethod
    def _validate_connection(data: Dict) -> Tuple[bool, str]:
        required_fields = ['connection_type', 'peer_id', 'activity_description']
        if not all(field in data for field in required_fields):
            return False, "Missing required fields"
        if data['connection_type'] not in ['study_partner', 'study_group']:
            return False, "Invalid connection type"
        return True, "Valid connection"

class JourneyManager:
    """Manager class for journey-related operations"""
    
    @staticmethod
    def initialize_default_paths():
        """Initialize default journey paths if they don't exist"""
        try:
            grade_stress_group = Group.query.filter_by(name="Grade Stress").first()
            if grade_stress_group:
                existing_path = JourneyPath.query.filter_by(community_id=grade_stress_group.id).first()
                if not existing_path:
                    JourneyManager._create_grade_stress_path(grade_stress_group.id)
        except Exception as e:
            logger.error(f"Failed to initialize paths: {str(e)}")
            raise

    @staticmethod
    def _create_grade_stress_path(group_id: int) -> JourneyPath:
        """Create the grade stress journey path"""
        path = JourneyPath(
            community_id=group_id,
            name="Grade Stress Relief Journey",
            description="A step-by-step journey to manage academic stress",
            total_milestones=7,
            coins_per_milestone=50
        )
        db.session.add(path)
        db.session.flush()

        milestones = [
            {
                "title": "Start Your Journey",
                "description": "Complete the initial stress assessment",
                "order_number": 1,
                "milestone_type": "reflection",
                "coins_reward": 50,
                "required_days": 1,
                "required_activities": 1
            },
            # Add more milestones here...
        ]

        for milestone_data in milestones:
            milestone = JourneyMilestone(path_id=path.id, **milestone_data)
            db.session.add(milestone)

        db.session.commit()
        return path

    @staticmethod
    def get_journey_stats(user_id: int, path_id: int) -> Dict:
        """Get comprehensive journey statistics"""
        progress = UserJourneyProgress.query.filter_by(
            user_id=user_id,
            path_id=path_id
        ).first()

        if not progress:
            return {'started': False, 'message': 'Journey not started'}

        return {
            'started': True,
            'completed_milestones': progress.completed_milestones,
            'total_coins_earned': progress.total_coins_earned,
            'current_streak': progress.current_streak
        }

    @staticmethod
    def get_leaderboard(path_id: int) -> List[Dict]:
        """Get leaderboard entries for a path"""
        entries = db.session.query(
            UserJourneyProgress, User
        ).join(
            User, User.id == UserJourneyProgress.user_id
        ).filter(
            UserJourneyProgress.path_id == path_id
        ).order_by(
            UserJourneyProgress.completed_milestones.desc(),
            UserJourneyProgress.total_coins_earned.desc()
        ).limit(10).all()

        return [{
            'user_id': entry.User.id,
            'name': entry.User.name,
            'completed_milestones': entry.UserJourneyProgress.completed_milestones,
            'total_coins': entry.UserJourneyProgress.total_coins_earned,
            'current_streak': entry.UserJourneyProgress.current_streak
        } for entry in entries]

class JourneyRoutes:
    """Journey routes handler"""
    
    def __init__(self, blueprint: Blueprint):
        """Initialize journey routes handler"""
        self.blueprint = blueprint
        self.validator = ActivityValidator()
        self.register_routes()

    def register_routes(self):
        """Register all journey-related routes"""
        
        @self.blueprint.route('/paths/<int:community_id>', methods=['GET'])
        @login_required
        def get_community_paths(community_id: int) -> Tuple[Dict, int]:
            try:
                paths = JourneyPath.query.filter_by(community_id=community_id).all()
                paths_data = []
                
                for path in paths:
                    user_progress = UserJourneyProgress.query.filter_by(
                        user_id=current_user.id,
                        path_id=path.id
                    ).first()
                    
                    paths_data.append({
                        'id': path.id,
                        'name': path.name,
                        'description': path.description,
                        'total_milestones': path.total_milestones,
                        'coins_per_milestone': path.coins_per_milestone,
                        'user_progress': {
                            'started': bool(user_progress),
                            'completed_milestones': user_progress.completed_milestones if user_progress else 0,
                            'total_coins_earned': user_progress.total_coins_earned if user_progress else 0
                        }
                    })
                    
                return jsonify(paths_data), HTTPStatus.OK
                
            except Exception as e:
                logger.error(f"Error in get_community_paths: {str(e)}")
                return jsonify({'error': 'Failed to retrieve paths'}), HTTPStatus.INTERNAL_SERVER_ERROR

        # Add other route handlers here...

def register_journey_routes(app):
    """Register journey routes with the application"""
    journey_bp = Blueprint('journey', __name__)
    routes_handler = JourneyRoutes(journey_bp)
    
    # Initialize journey paths
    with app.app_context():
        try:
            JourneyManager.initialize_default_paths()
        except Exception as e:
            logger.error(f"Failed to initialize journey paths: {str(e)}")
    
    app.register_blueprint(journey_bp, url_prefix='/journey')
    return journey_bp