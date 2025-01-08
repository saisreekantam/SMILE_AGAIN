from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from typing import Dict, List, Optional
from models import User, UserProblem, Profile, Friendship, Blog, Notification
from extensions import db, socketio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_profile_routes(users_bp):
    """
    Register all profile and friendship related routes.
    Handles user profiles, friend requests, and notifications.
    """
    
    @users_bp.route('/profile/<int:user_id>', methods=['GET'])
    @login_required
    def get_user_profile(user_id: int):
        """
        Get user profile with friendship status and recent activity.
        
        Args:
            user_id (int): ID of the user whose profile is being requested
            
        Returns:
            JSON response with user profile data and friendship status
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
                
            # Check friendship status
            friendship = Friendship.query.filter(
                ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id)) |
                ((Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id))
            ).first()
            
            friendship_status = 'none'
            if friendship:
                friendship_status = friendship.status
                
            profile = Profile.query.filter_by(user_id=user_id).first()
            user_problem = UserProblem.query.filter_by(user_id=user_id).first()
            
            return jsonify({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'gender': user.gender,
                'description': profile.description if profile else '',
                'profile_pic': profile.profile_pic if profile else 'default.jpg',
                'smile_last_time': user_problem.smile_last_time if user_problem else None,
                'smile_reason': user_problem.smile_reason if user_problem else None,
                'friendship_status': friendship_status
            })
            
        except Exception as e:
            logger.error(f"Error in get_user_profile: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @users_bp.route('/send-friend-request/<int:user_id>', methods=['POST'])
    @login_required
    def send_friend_request(user_id: int):
        """
        Send a friend request to another user with real-time notification.
        
        Args:
            user_id (int): ID of the user to send friend request to
            
        Returns:
            JSON response indicating success or failure
        """
        try:
            if user_id == current_user.id:
                return jsonify({'error': 'Cannot send friend request to yourself'}), 400
                
            target_user = User.query.get(user_id)
            if not target_user:
                return jsonify({'error': 'User not found'}), 404
                
            existing_friendship = Friendship.query.filter(
                ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id)) |
                ((Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id))
            ).first()
            
            if existing_friendship:
                return jsonify({'error': 'Friend request already exists or users are already friends'}), 400
                
            # Create new friendship request
            friendship = Friendship(
                user_id=current_user.id,
                friend_id=user_id,
                status='pending',
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(friendship)
            db.session.commit()
            logger.info(f"Friend request created with ID: {friendship.id}")
            # Send real-time notification
            socketio.emit(
                'friend_request',
                {
                    'request_id': friendship.id,
                    'sender_id': current_user.id,
                    'sender_name': current_user.name,
                    'timestamp': datetime.utcnow().isoformat()
                },
                room=str(user_id)
            )
            
            return jsonify({'message': 'Friend request sent successfully'})
            
        except Exception as e:
            logger.error(f"Error in send_friend_request: {str(e)}")
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @users_bp.route('/respond-friend-request/<int:friendship_id>', methods=['POST'])
    @login_required
    def respond_friend_request(friendship_id: int):
        """
        Accept or reject a friend request with notification to sender.
        
        Args:
            friendship_id (int): ID of the friendship request to respond to
            
        Returns:
            JSON response indicating success or failure
        """
        try:
            data = request.get_json()
            action = data.get('action')
            
            if action not in ['accept', 'reject']:
                return jsonify({'error': 'Invalid action'}), 400
                
            friendship = Friendship.query.get(friendship_id)
            if not friendship or friendship.friend_id != current_user.id:
                return jsonify({'error': 'Friend request not found'}), 404
                
            if friendship.status != 'pending':
                return jsonify({'error': 'Friend request already processed'}), 400
                
            sender = User.query.get(friendship.user_id)
            
            if action == 'accept':
                friendship.status = 'accepted'
                db.session.commit()
                
                # Notify sender about acceptance
                socketio.emit(
                    'friend_request_response',
                    {
                        'status': 'accepted',
                        'responder_id': current_user.id,
                        'responder_name': current_user.name,
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    room=str(sender.id)
                )
                
                return jsonify({'message': 'Friend request accepted'})
            else:
                db.session.delete(friendship)
                db.session.commit()
                
                # Notify sender about rejection
                socketio.emit(
                    'friend_request_response',
                    {
                        'status': 'rejected',
                        'responder_id': current_user.id,
                        'responder_name': current_user.name,
                        'timestamp': datetime.utcnow().isoformat()
                    },
                    room=str(sender.id)
                )
                
                return jsonify({'message': 'Friend request rejected'})
                
        except Exception as e:
            logger.error(f"Error in respond_friend_request: {str(e)}")
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @users_bp.route('/pending-friend-requests', methods=['GET'])
    @login_required
    def get_pending_requests():
        """
        Get list of pending friend requests for the current user.
        
        Returns:
            JSON response with list of pending friend requests
        """
        try:
            pending_requests = Friendship.query.filter_by(
                friend_id=current_user.id,
                status='pending'
            ).all()
            
            requests_data = [{
                'id': req.id,
                'user_id': req.user_id,
                'user_name': User.query.get(req.user_id).name,
                'timestamp': req.created_at.isoformat() if hasattr(req, 'created_at') else None
            } for req in pending_requests]
            
            return jsonify(requests_data)
            
        except Exception as e:
            logger.error(f"Error in get_pending_requests: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @users_bp.route('/friend-requests/count', methods=['GET'])
    @login_required
    def get_friend_request_count():
        """
        Get count of pending friend requests for the current user.
        
        Returns:
            JSON response with count of pending requests
        """
        try:
            count = Friendship.query.filter_by(
                friend_id=current_user.id,
                status='pending'
            ).count()
            
            return jsonify({'count': count})
            
        except Exception as e:
            logger.error(f"Error in get_friend_request_count: {str(e)}")
            return jsonify({'error': str(e)}), 500