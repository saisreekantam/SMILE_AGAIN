from typing import Dict, Any, Tuple, List, Optional
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import logging
from sqlalchemy import func
from .utils import ActivityManager, ActivityRecommender
from models import Activity, UserActivity, ActivityStreak

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_routes(bp: Blueprint, db: SQLAlchemy) -> None:
    """
    Register all activity-related routes with the blueprint.
    
    Args:
        bp: Flask blueprint instance
        db: SQLAlchemy database instance
    """
    
    # Initialize managers
    activity_manager = ActivityManager(db.session)
    activity_recommender = ActivityRecommender(db.session)

    @bp.route('/recommended', methods=['GET'])
    @login_required
    def get_recommended_activities() -> Tuple[Dict[str, Any], int]:
        """
        Get personalized activity recommendations for the current user.
        
        Returns:
            Tuple containing response data and status code
        """
        try:
            limit = request.args.get('limit', default=5, type=int)
            activities = activity_recommender.get_recommendations(
                user_id=current_user.id,
                limit=limit
            )
            
            logger.info(f"Retrieved {len(activities)} recommendations for user {current_user.id}")
            return jsonify(activities), 200
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return jsonify({
                'error': 'Failed to get recommendations',
                'message': str(e)
            }), 500

    @bp.route('/activities', methods=['GET'])
    @login_required
    def get_activities() -> Tuple[Dict[str, Any], int]:
        """
        Get list of all available activities, optionally filtered by category.
        
        Returns:
            Tuple containing response data and status code
        """
        try:
            category = request.args.get('category')
            query = Activity.query

            if category:
                query = query.filter_by(category=category)

            activities = query.all()
            return jsonify([activity.to_dict() for activity in activities]), 200
            
        except Exception as e:
            logger.error(f"Error getting activities: {str(e)}")
            return jsonify({
                'error': 'Failed to get activities',
                'message': str(e)
            }), 500

    @bp.route('/start/<int:activity_id>', methods=['POST'])
    @login_required
    def start_activity(activity_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Start a new activity session.
        
        Args:
            activity_id: ID of the activity to start
            
        Returns:
            Tuple containing response data and status code
        """
        try:
            data = request.get_json()
            mood_before = data.get('mood_before', 5.0)
            
            # Validate mood rating
            if not isinstance(mood_before, (int, float)) or not 1 <= mood_before <= 10:
                return jsonify({
                    'error': 'Invalid mood rating',
                    'message': 'Mood must be between 1 and 10'
                }), 400

            result = activity_manager.start_activity(
                user_id=current_user.id,
                activity_id=activity_id,
                mood_before=mood_before
            )
            
            if 'error' in result:
                return jsonify(result), 400
                
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"Error starting activity: {str(e)}")
            return jsonify({
                'error': 'Failed to start activity',
                'message': str(e)
            }), 500

    @bp.route('/complete/<int:user_activity_id>', methods=['POST'])
    @login_required
    def complete_activity(user_activity_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Complete an activity session and record results.
        
        Args:
            user_activity_id: ID of the activity session to complete
            
        Returns:
            Tuple containing response data and status code
        """
        try:
            data = request.get_json()
            mood_after = data.get('mood_after', 5.0)
            effectiveness_rating = data.get('effectiveness_rating', 3)
            
            # Validate ratings
            if not isinstance(mood_after, (int, float)) or not 1 <= mood_after <= 10:
                return jsonify({
                    'error': 'Invalid mood rating',
                    'message': 'Mood must be between 1 and 10'
                }), 400
                
            if not isinstance(effectiveness_rating, int) or not 1 <= effectiveness_rating <= 5:
                return jsonify({
                    'error': 'Invalid effectiveness rating',
                    'message': 'Rating must be between 1 and 5'
                }), 400

            result = activity_manager.complete_activity(
                user_id=current_user.id,
                user_activity_id=user_activity_id,
                mood_after=mood_after,
                effectiveness_rating=effectiveness_rating
            )
            
            if 'error' in result:
                return jsonify(result), 400
                
            return jsonify(result), 200
            
        except Exception as e:
            logger.error(f"Error completing activity: {str(e)}")
            return jsonify({
                'error': 'Failed to complete activity',
                'message': str(e)
            }), 500

    @bp.route('/stats', methods=['GET'])
    @login_required
    def get_activity_stats() -> Tuple[Dict[str, Any], int]:
        """
        Get user's activity statistics and achievements.
        
        Returns:
            Tuple containing response data and status code
        """
        try:
            stats = activity_manager.get_activity_stats(current_user.id)
            return jsonify(stats), 200
            
        except Exception as e:
            logger.error(f"Error getting activity stats: {str(e)}")
            return jsonify({
                'error': 'Failed to get activity statistics',
                'message': str(e)
            }), 500

    @bp.route('/history', methods=['GET'])
    @login_required
    def get_activity_history() -> Tuple[Dict[str, Any], int]:
        """
        Get user's activity history with optional pagination.
        
        Returns:
            Tuple containing response data and status code
        """
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            # Get paginated activity history
            activities = UserActivity.query.filter_by(
                user_id=current_user.id
            ).order_by(
                UserActivity.started_at.desc()
            ).paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # Format activity data
            activity_data = []
            for ua in activities.items:
                activity = Activity.query.get(ua.activity_id)
                activity_data.append({
                    'id': ua.id,
                    'activity': activity.to_dict(),
                    'started_at': ua.started_at.isoformat(),
                    'completed_at': ua.completed_at.isoformat() if ua.completed_at else None,
                    'mood_before': ua.mood_before,
                    'mood_after': ua.mood_after,
                    'effectiveness_rating': ua.effectiveness_rating,
                    'mood_improvement': ua.mood_after - ua.mood_before if ua.mood_after else None
                })
            
            return jsonify({
                'activities': activity_data,
                'pagination': {
                    'total': activities.total,
                    'pages': activities.pages,
                    'current_page': activities.page,
                    'per_page': activities.per_page,
                    'has_next': activities.has_next,
                    'has_prev': activities.has_prev
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting activity history: {str(e)}")
            return jsonify({
                'error': 'Failed to get activity history',
                'message': str(e)
            }), 500

    logger.info("Activity routes registered successfully")