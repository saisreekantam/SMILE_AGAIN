from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import User, UserProblem, Profile, Friendship, Blog
from extensions import db

def register_profile_routes(users_bp):
    @users_bp.route('/profile/<int:user_id>', methods=['GET'])
    @login_required
    def get_user_profile(user_id):
        """Get public profile information for a specific user"""
        try:
            # Get user and their problem info
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
                
            user_problem = UserProblem.query.filter_by(user_id=user_id).first()
            profile = Profile.query.filter_by(user_id=user_id).first()
            
            # Check if they are already friends
            friendship = Friendship.query.filter(
                ((Friendship.user_id == current_user.id) & (Friendship.friend_id == user_id)) |
                ((Friendship.user_id == user_id) & (Friendship.friend_id == current_user.id))
            ).first()
            
            # Get their blog posts
            blogs = Blog.query.filter_by(user_id=user_id).order_by(Blog.created_at.desc()).limit(5).all()
            
            return jsonify({
                'id': user.id,
                'name': user.name,
                'gender': user.gender,
                'smile_last_time': user_problem.smile_last_time if user_problem else None,
                'smile_reason': user_problem.smile_reason if user_problem else None,
                'profile_pic': profile.profile_pic if profile else 'static/default.jpg',
                'description': profile.description if profile else '',
                'friendship_status': friendship.status if friendship else 'none',
                'recent_blogs': [{
                    'id': blog.id,
                    'title': blog.title,
                    'created_at': blog.created_at.isoformat()
                } for blog in blogs]
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @users_bp.route('/send-friend-request/<int:user_id>', methods=['POST'])
    @login_required
    def send_friend_request(user_id):
        """Send a friend request to another user"""
        try:
            if user_id == current_user.id:
                return jsonify({'error': 'Cannot send friend request to yourself'}), 400
                
            target_user = User.query.get(user_id)
            if not target_user:
                return jsonify({'error': 'User not found'}), 404
                
            # Check if friendship already exists
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
                status='pending'
            )
            
            db.session.add(friendship)
            db.session.commit()
            
            return jsonify({'message': 'Friend request sent successfully'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @users_bp.route('/respond-friend-request/<int:friendship_id>', methods=['POST'])
    @login_required
    def respond_friend_request(friendship_id):
        """Accept or reject a friend request"""
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
                
            if action == 'accept':
                friendship.status = 'accepted'
                db.session.commit()
                return jsonify({'message': 'Friend request accepted'})
            else:
                db.session.delete(friendship)
                db.session.commit()
                return jsonify({'message': 'Friend request rejected'})
                
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @users_bp.route('/pending-friend-requests', methods=['GET'])
    @login_required
    def get_pending_requests():
        """Get list of pending friend requests"""
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
            return jsonify({'error': str(e)}), 500