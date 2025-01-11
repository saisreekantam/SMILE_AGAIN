# activity_bot/routes.py
from datetime import datetime
from flask import request, jsonify, current_app
from flask_login import login_required, current_user
import logging
from models import Message, UserActivity
from .utils import ActivityBot

logger = logging.getLogger(__name__)

def register_routes(bp, db):
    # Initialize activity bot instance
    activity_bot = ActivityBot(db)

    @bp.route('/activities/suggest', methods=['POST'])
    @login_required
    def suggest_activities():
        """
        Handle activity suggestions and community engagement.
        """
        try:
            # Validate request
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
                
            user_message = data.get('message')
            if not user_message:
                return jsonify({'error': 'Message is required'}), 400

            logger.debug(f"Received activity request from user {current_user.id}: {user_message}")
            
            # Generate activity suggestions
            response_data = activity_bot.generate_response(user_message, current_user.id)
            return jsonify(response_data)

        except Exception as e:
            logger.error(f"Error in activity suggestion endpoint: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': {
                    'content': "Let's find some fun activities for you! What type of activities interest you most?",
                    'type': 'activity_bot'
                }
            }), 500

    @bp.route('/activities/history', methods=['GET'])
    @login_required
    def get_activity_history():
        """
        Retrieve user's activity participation history.
        """
        try:
            # Get messages with pagination
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            activities = Message.query.filter(
                (Message.sender_id == current_user.id) | 
                (Message.receiver_id == current_user.id),
                Message.message_type.in_(['activity_request', 'activity_suggestion'])
            ).order_by(
                Message.timestamp.desc()
            ).paginate(
                page=page, 
                per_page=per_page,
                error_out=False
            )

            activity_history = []
            for msg in activities.items:
                activity_data = {
                    'id': msg.id,
                    'content': msg.content,
                    'type': msg.message_type,
                    'timestamp': msg.timestamp.isoformat()
                }
                activity_history.append(activity_data)

            return jsonify({
                'activities': activity_history,
                'pagination': {
                    'total': activities.total,
                    'pages': activities.pages,
                    'current': activities.page,
                    'per_page': activities.per_page
                }
            })

        except Exception as e:
            logger.error(f"Error getting activity history: {str(e)}")
            return jsonify({'error': 'Failed to retrieve activity history'}), 500

    @bp.route('/activities/participate', methods=['POST'])
    @login_required
    def participate_activity():
        """
        Record user's participation in an activity.
        """
        try:
            data = request.get_json()
            print(data)
            if not data or 'activity_id' not in data:
                return jsonify({'error': 'Activity ID is required'}), 400

            # Record participation
            participation = UserActivity(
                user_id=current_user.id,
                activity_id=data['activity_id'],
                participated_at=datetime.utcnow(),
                feedback=data.get('feedback', '')
            )
            db.session.add(participation)
            db.session.commit()

            return jsonify({
                'message': 'Activity participation recorded successfully',
                'participation_id': participation.id
            })

        except Exception as e:
            logger.error(f"Error recording activity participation: {str(e)}")
            db.session.rollback()
            return jsonify({'error': 'Failed to record participation'}), 500