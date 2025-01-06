from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.models import User, Friendship, FriendRequest
from backend.extensions import db
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

friends_bp = Blueprint('friends', __name__)

def register_routes(app):
    """Register friend-related routes with the application"""
    app.register_blueprint(friends_bp, url_prefix='/friends')

@friends_bp.route('/request', methods=['POST'])
@login_required
def send_friend_request():
    """Send a friend request to another user"""
    try:
        data = request.get_json()
        recipient_id = data.get('recipient_id')
        message = data.get('message', '')

        # Validate request
        if not recipient_id:
            return jsonify({'error': 'Recipient ID is required'}), 400

        if recipient_id == current_user.id:
            return jsonify({'error': 'Cannot send friend request to yourself'}), 400

        recipient = User.query.get(recipient_id)
        if not recipient:
            return jsonify({'error': 'Recipient not found'}), 404

        # Check if they are already friends
        existing_friendship = Friendship.query.filter(
            ((Friendship.user_id == current_user.id) & (Friendship.friend_id == recipient_id)) |
            ((Friendship.user_id == recipient_id) & (Friendship.friend_id == current_user.id))
        ).first()

        if existing_friendship:
            return jsonify({'error': 'Already friends with this user'}), 400

        # Check for existing pending request
        existing_request = FriendRequest.query.filter_by(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            status='pending'
        ).first()

        if existing_request:
            return jsonify({'error': 'Friend request already sent'}), 400

        # Create new friend request
        friend_request = FriendRequest(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            message=message
        )
        db.session.add(friend_request)
        db.session.commit()

        return jsonify({
            'message': 'Friend request sent successfully',
            'request_id': friend_request.id
        }), 201

    except Exception as e:
        logger.error(f"Error in send_friend_request: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@friends_bp.route('/requests', methods=['GET'])
@login_required
def get_friend_requests():
    """Get all friend requests for the current user"""
    try:
        # Get received pending requests
        received_requests = FriendRequest.query.filter_by(
            recipient_id=current_user.id,
            status='pending'
        ).all()

        # Get sent pending requests
        sent_requests = FriendRequest.query.filter_by(
            sender_id=current_user.id,
            status='pending'
        ).all()

        requests_data = {
            'received': [{
                'id': req.id,
                'sender_id': req.sender_id,
                'sender_name': req.sender.name,
                'message': req.message,
                'created_at': req.created_at.isoformat()
            } for req in received_requests],
            'sent': [{
                'id': req.id,
                'recipient_id': req.recipient_id,
                'recipient_name': req.recipient.name,
                'message': req.message,
                'created_at': req.created_at.isoformat()
            } for req in sent_requests]
        }

        return jsonify(requests_data), 200

    except Exception as e:
        logger.error(f"Error in get_friend_requests: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@friends_bp.route('/request/<int:request_id>', methods=['POST'])
@login_required
def handle_friend_request(request_id):
    """Accept or reject a friend request"""
    try:
        data = request.get_json()
        action = data.get('action')  # 'accept' or 'reject'

        if action not in ['accept', 'reject']:
            return jsonify({'error': 'Invalid action'}), 400

        friend_request = FriendRequest.query.get_or_404(request_id)

        # Verify request recipient
        if friend_request.recipient_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        if friend_request.status != 'pending':
            return jsonify({'error': 'Request already processed'}), 400

        if action == 'accept':
            # Create friendship records
            friendship1 = Friendship(
                user_id=friend_request.sender_id,
                friend_id=friend_request.recipient_id,
                status='accepted'
            )
            friendship2 = Friendship(
                user_id=friend_request.recipient_id,
                friend_id=friend_request.sender_id,
                status='accepted'
            )
            db.session.add(friendship1)
            db.session.add(friendship2)
            
            friend_request.status = 'accepted'
            db.session.commit()

            return jsonify({'message': 'Friend request accepted'}), 200

        elif action == 'reject':
            friend_request.status = 'rejected'
            db.session.commit()
            return jsonify({'message': 'Friend request rejected'}), 200

    except Exception as e:
        logger.error(f"Error in handle_friend_request: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@friends_bp.route('/list', methods=['GET'])
@login_required
def get_friends():
    """Get list of current user's friends"""
    try:
        # Get all accepted friendships
        friendships = Friendship.query.filter_by(
            user_id=current_user.id,
            status='accepted'
        ).all()

        friends_list = [{
            'id': friendship.friend_id,
            'name': User.query.get(friendship.friend_id).name,
            'since': friendship.created_at.isoformat()
        } for friendship in friendships]

        return jsonify({'friends': friends_list}), 200

    except Exception as e:
        logger.error(f"Error in get_friends: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@friends_bp.route('/unfriend/<int:friend_id>', methods=['POST'])
@login_required
def unfriend_user(friend_id):
    """Remove a friend from the current user's friend list"""
    try:
        if friend_id == current_user.id:
            return jsonify({'error': 'Cannot unfriend yourself'}), 400

        # Delete both friendship records
        deleted_count = Friendship.query.filter(
            (
                (Friendship.user_id == current_user.id) & 
                (Friendship.friend_id == friend_id)
            ) | (
                (Friendship.user_id == friend_id) & 
                (Friendship.friend_id == current_user.id)
            )
        ).delete()

        if deleted_count == 0:
            return jsonify({'error': 'Friendship not found'}), 404

        db.session.commit()
        return jsonify({'message': 'Friend removed successfully'}), 200

    except Exception as e:
        logger.error(f"Error in unfriend_user: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
