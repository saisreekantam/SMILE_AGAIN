# meditation/routes.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .utils import MeditationManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_meditation_routes(bp, db):
    meditation_manager = MeditationManager(db)

    @bp.route('/meditation/start', methods=['POST'])
    @login_required
    def start_meditation():
        """Start a new meditation session"""
        try:
            data = request.get_json()
            duration = data.get('duration')
            ambient_sound = data.get('ambient_sound')

            if not duration:
                return jsonify({'error': 'Duration is required'}), 400

            session_data = meditation_manager.create_session(
                user_id=current_user.id,
                duration=duration,
                ambient_sound=ambient_sound
            )

            return jsonify({
                'message': 'Meditation session started',
                'session': session_data
            })

        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error starting meditation: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @bp.route('/meditation/complete/<int:session_id>', methods=['POST'])
    @login_required
    def complete_meditation(session_id):
        """Complete a meditation session"""
        try:
            data = request.get_json()
            actual_duration = data.get('actual_duration')

            if not actual_duration:
                return jsonify({'error': 'Actual duration is required'}), 400

            completion_data = meditation_manager.complete_session(
                session_id=session_id,
                actual_duration=actual_duration
            )

            return jsonify({
                'message': 'Meditation session completed',
                'session': completion_data
            })

        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error completing meditation: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @bp.route('/meditation/stats', methods=['GET'])
    @login_required
    def get_meditation_stats():
        """Get user's meditation statistics"""
        try:
            stats = meditation_manager.get_user_stats(current_user.id)
            return jsonify({
                'stats': {
                    'total_sessions': stats.total_sessions,
                    'total_minutes': stats.total_minutes,
                    'longest_streak': stats.longest_streak,
                    'current_streak': stats.current_streak,
                    'average_duration': round(stats.average_duration, 2),
                    'favorite_duration': stats.favorite_duration,
                    'completion_rate': round(stats.completion_rate, 2)
                }
            })

        except Exception as e:
            logger.error(f"Error getting meditation stats: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @bp.route('/meditation/recommendations', methods=['GET'])
    @login_required
    def get_recommendations():
        """Get personalized meditation recommendations"""
        try:
            recommendations = meditation_manager.get_recommended_sessions(
                current_user.id
            )
            return jsonify({'recommendations': recommendations})

        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    @bp.route('/meditation/presets', methods=['GET'])
    @login_required
    def get_meditation_presets():
        """Get available meditation presets and ambient sounds"""
        try:
            return jsonify({
                'durations': meditation_manager.preset_durations,
                'ambient_sounds': meditation_manager.default_ambient_sounds
            })

        except Exception as e:
            logger.error(f"Error getting presets: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500