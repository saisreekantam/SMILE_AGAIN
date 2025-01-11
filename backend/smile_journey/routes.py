from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from typing import Dict, List, Optional

from models import (
    JourneyPath, JourneyMilestone, UserJourneyProgress,
    User, Group, UserProblem, db
)

journey_bp = Blueprint('journey', __name__)

def register_journey_routes(app, db):
    """Register all journey-related routes"""

    @journey_bp.route('/paths/<int:community_id>', methods=['GET'])
    @login_required
    def get_community_paths(community_id: int):
        """Get available journey paths for a community"""
        try:
            # Verify the community exists
            community = Group.query.get(community_id)
            if not community:
                return jsonify({'error': 'Community not found'}), 404

            # Get paths for the community
            paths = JourneyPath.query.filter_by(community_id=community_id).all()
            paths_data = []

            for path in paths:
                # Get user's progress for this path
                progress = UserJourneyProgress.query.filter_by(
                    user_id=current_user.id,
                    path_id=path.id
                ).first()

                # Get milestones for this path
                milestones = JourneyMilestone.query.filter_by(
                    path_id=path.id
                ).order_by(JourneyMilestone.order_number).all()

                # Build response data
                paths_data.append({
                    'id': path.id,
                    'name': path.name,
                    'description': path.description,
                    'total_milestones': path.total_milestones,
                    'coins_per_milestone': path.coins_per_milestone,
                    'user_progress': {
                        'started': bool(progress),
                        'completed_milestones': progress.completed_milestones if progress else 0,
                        'total_coins_earned': progress.total_coins_earned if progress else 0,
                        'current_milestone': progress.current_milestone if progress else None,
                        'current_streak': progress.current_streak if progress else 0
                    },
                    'milestones': [{
                        'id': m.id,
                        'title': m.title,
                        'description': m.description,
                        'type': m.milestone_type,
                        'order_number': m.order_number,
                        'coins_reward': m.coins_reward
                    } for m in milestones]
                })

            return jsonify(paths_data)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @journey_bp.route('/start/<int:path_id>', methods=['POST'])
    @login_required
    def start_journey(path_id: int):
        """Start a new journey path"""
        try:
            # Check if path exists
            path = JourneyPath.query.get(path_id)
            if not path:
                return jsonify({'error': 'Journey path not found'}), 404

            # Check if user already started this path
            existing_progress = UserJourneyProgress.query.filter_by(
                user_id=current_user.id,
                path_id=path_id
            ).first()

            if existing_progress:
                return jsonify({'message': 'Journey already started',
                              'progress_id': existing_progress.id}), 200

            # Create new progress entry
            new_progress = UserJourneyProgress(
                user_id=current_user.id,
                path_id=path_id,
                started_at=datetime.utcnow()
            )
            db.session.add(new_progress)
            db.session.commit()

            return jsonify({
                'message': 'Journey started successfully',
                'progress_id': new_progress.id
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @journey_bp.route('/milestone/<int:milestone_id>/complete', methods=['POST'])
    @login_required
    def complete_milestone(milestone_id: int):
        """Mark a milestone as completed"""
        try:
            milestone = JourneyMilestone.query.get(milestone_id)
            if not milestone:
                return jsonify({'error': 'Milestone not found'}), 404

            # Get user's progress for this path
            progress = UserJourneyProgress.query.filter_by(
                user_id=current_user.id,
                path_id=milestone.path_id
            ).first()

            if not progress:
                return jsonify({'error': 'Journey not started'}), 400

            if milestone.order_number != progress.current_milestone:
                return jsonify({'error': 'Cannot skip milestones'}), 400

            # Update progress
            progress.completed_milestones += 1
            progress.current_milestone += 1
            progress.total_coins_earned += milestone.coins_reward
            progress.last_activity_date = datetime.utcnow()

            # Update streak
            if progress.last_activity_date:
                days_diff = (datetime.utcnow() - progress.last_activity_date).days
                if days_diff <= 1:
                    progress.current_streak += 1
                else:
                    progress.current_streak = 1
            else:
                progress.current_streak = 1

            db.session.commit()

            return jsonify({
                'message': 'Milestone completed',
                'coins_earned': milestone.coins_reward,
                'current_streak': progress.current_streak
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @journey_bp.route('/progress', methods=['GET'])
    @login_required
    def get_progress():
        """Get user's progress across all journeys"""
        try:
            progress_entries = UserJourneyProgress.query.filter_by(
                user_id=current_user.id
            ).all()

            progress_data = []
            for entry in progress_entries:
                path = JourneyPath.query.get(entry.path_id)
                current_milestone = JourneyMilestone.query.filter_by(
                    path_id=path.id,
                    order_number=entry.current_milestone
                ).first()

                progress_data.append({
                    'path_name': path.name,
                    'completed_milestones': entry.completed_milestones,
                    'total_milestones': path.total_milestones,
                    'current_milestone': {
                        'title': current_milestone.title if current_milestone else None,
                        'description': current_milestone.description if current_milestone else None
                    },
                    'coins_earned': entry.total_coins_earned,
                    'current_streak': entry.current_streak
                })

            return jsonify(progress_data)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @journey_bp.route('/stats', methods=['GET'])
    @login_required
    def get_journey_stats():
        """Get user's journey statistics"""
        try:
            # Get all user progress entries
            progress_entries = UserJourneyProgress.query.filter_by(
                user_id=current_user.id
            ).all()

            total_coins = sum(p.total_coins_earned for p in progress_entries)
            total_milestones = sum(p.completed_milestones for p in progress_entries)
            current_streaks = [p.current_streak for p in progress_entries]
            max_streak = max(current_streaks) if current_streaks else 0

            return jsonify({
                'total_coins_earned': total_coins,
                'total_milestones_completed': total_milestones,
                'highest_streak': max_streak,
                'active_journeys': len(progress_entries)
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Register the blueprint with the app
    app.register_blueprint(journey_bp, url_prefix='/journey')