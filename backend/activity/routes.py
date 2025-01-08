from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from models import UserProblem
from models import Activity, UserActivity, ActivityStreak

activities_bp = Blueprint('activities', __name__)

def register_routes(bp, db):
    @bp.route('/recommended', methods=['GET'])
    @login_required
    def get_recommended_activities():
        """Get personalized activity recommendations based on user's mood and history"""
        try:
            # Get user's smile reason
            user_problem = UserProblem.query.filter_by(user_id=current_user.id).first()
            if not user_problem or not user_problem.smile_reason:
                return jsonify({'error': 'Please complete your mood profile first'}), 400

            # Get user's activity history
            completed_activities = UserActivity.query.filter_by(
                user_id=current_user.id,
                completed_at__isnot=None
            ).all()
            
            completed_ids = [ua.activity_id for ua in completed_activities]
            
            # Find matching activities
            query = Activity.query.filter(
                Activity.mood_tags.contains(user_problem.smile_reason)
            )
            
            # Prioritize unfinished activities
            if completed_ids:
                query = query.filter(~Activity.id.in_(completed_ids))
            
            activities = query.order_by(func.random()).limit(5).all()
            
            return jsonify([{
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'category': activity.category,
                'duration_minutes': activity.duration_minutes,
                'difficulty_level': activity.difficulty_level,
                'resources_needed': activity.resources_needed
            } for activity in activities])

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @bp.route('/start/<int:activity_id>', methods=['POST'])
    @login_required
    def start_activity(activity_id):
        """Start an activity and record initial mood"""
        try:
            activity = Activity.query.get(activity_id)
            if not activity:
                return jsonify({'error': 'Activity not found'}), 404

            mood_before = request.json.get('mood_before')
            if not mood_before or not (1 <= mood_before <= 10):
                return jsonify({'error': 'Valid mood_before (1-10) is required'}), 400

            user_activity = UserActivity(
                user_id=current_user.id,
                activity_id=activity_id,
                mood_before=mood_before
            )
            
            db.session.add(user_activity)
            db.session.commit()

            return jsonify({
                'message': 'Activity started successfully',
                'user_activity_id': user_activity.id
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @bp.route('/complete/<int:user_activity_id>', methods=['POST'])
    @login_required
    def complete_activity(user_activity_id):
        """Complete an activity and record final mood and feedback"""
        try:
            user_activity = UserActivity.query.get(user_activity_id)
            if not user_activity or user_activity.user_id != current_user.id:
                return jsonify({'error': 'Activity not found'}), 404

            if user_activity.completed_at:
                return jsonify({'error': 'Activity already completed'}), 400

            data = request.json
            mood_after = data.get('mood_after')
            if not mood_after or not (1 <= mood_after <= 10):
                return jsonify({'error': 'Valid mood_after (1-10) is required'}), 400

            user_activity.completed_at = datetime.utcnow()
            user_activity.mood_after = mood_after
            user_activity.feedback = data.get('feedback')
            user_activity.effectiveness_rating = data.get('effectiveness_rating')

            # Update activity streak
            streak = ActivityStreak.query.filter_by(user_id=current_user.id).first()
            if not streak:
                streak = ActivityStreak(user_id=current_user.id)
                db.session.add(streak)
            
            streak.update_streak(datetime.utcnow())
            
            db.session.commit()

            return jsonify({
                'message': 'Activity completed successfully',
                'mood_improvement': mood_after - user_activity.mood_before,
                'current_streak': streak.current_streak,
                'total_completed': streak.total_activities_completed
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @bp.route('/stats', methods=['GET'])
    @login_required
    def get_activity_stats():
        """Get user's activity statistics and achievements"""
        try:
            streak = ActivityStreak.query.filter_by(user_id=current_user.id).first()
            
            completed_activities = UserActivity.query.filter_by(
                user_id=current_user.id,
                completed_at__isnot=None
            ).all()
            
            # Calculate average mood improvement
            mood_improvements = [
                (act.mood_after - act.mood_before) 
                for act in completed_activities 
                if act.mood_after and act.mood_before
            ]
            
            avg_improvement = sum(mood_improvements) / len(mood_improvements) if mood_improvements else 0
            
            # Get most effective activities
            most_effective = UserActivity.query.filter_by(
                user_id=current_user.id,
                completed_at__isnot=None
            ).order_by(
                UserActivity.effectiveness_rating.desc()
            ).limit(3).all()
            
            return jsonify({
                'streak_stats': {
                    'current_streak': streak.current_streak if streak else 0,
                    'longest_streak': streak.longest_streak if streak else 0,
                    'total_completed': streak.total_activities_completed if streak else 0
                },
                'mood_stats': {
                    'average_improvement': round(avg_improvement, 1),
                    'activities_with_improvement': len([i for i in mood_improvements if i > 0])
                },
                'most_effective_activities': [{
                    'activity_name': Activity.query.get(ua.activity_id).title,
                    'effectiveness_rating': ua.effectiveness_rating,
                    'mood_improvement': ua.mood_after - ua.mood_before
                } for ua in most_effective]
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @bp.route('/suggestions', methods=['GET'])
    @login_required
    def get_activity_suggestions():
        """Get personalized activity suggestions based on effectiveness"""
        try:
            # Get user's most effective activities
            effective_activities = UserActivity.query.filter_by(
                user_id=current_user.id,
                completed_at__isnot=None
            ).order_by(
                UserActivity.effectiveness_rating.desc()
            ).limit(5).all()
            
            # Get activities similar to effective ones
            if effective_activities:
                effective_categories = set(
                    Activity.query.get(ua.activity_id).category 
                    for ua in effective_activities
                )
                
                suggested_activities = Activity.query.filter(
                    Activity.category.in_(effective_categories)
                ).order_by(func.random()).limit(3).all()
                
                return jsonify([{
                    'id': activity.id,
                    'title': activity.title,
                    'description': activity.description,
                    'category': activity.category,
                    'why_suggested': f"Based on your enjoyment of {activity.category} activities"
                } for activity in suggested_activities])
            
            # Default suggestions if no history
            return jsonify([{
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'category': activity.category,
                'why_suggested': "Recommended for new users"
            } for activity in Activity.query.order_by(func.random()).limit(3).all()])

        except Exception as e:
            return jsonify({'error': str(e)}), 500