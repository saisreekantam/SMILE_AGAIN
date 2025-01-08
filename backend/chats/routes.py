from flask import request, jsonify
from flask_login import login_required, current_user
from models import User, Message, Friendship
import nltk
from datetime import datetime
from sqlalchemy import or_, and_
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
nltk.download('stopwords')
nltk.download('punkt')

def contains_hate_speech(text):
    """
    Check if text contains hate speech using NLTK
    
    Args:
        text (str): Message text to check
        
    Returns:
        bool: True if hate speech detected, False otherwise
    """
    hate_words = ["hate", "kill", "abuse"]  
    tokens = nltk.word_tokenize(text.lower())
    return any(word in hate_words for word in tokens)

def register_routes(bp, db, socketio):
    """
    Register chat routes with the blueprint
    
    Args:
        bp: Flask blueprint instance
        db: SQLAlchemy database instance
        socketio: Socket.IO instance for real-time communication
    """
    
    def is_friend(user_id, friend_id):
        """Verify friendship status between two users"""
        friendship = Friendship.query.filter(
            or_(
                and_(Friendship.user_id == user_id, 
                     Friendship.friend_id == friend_id,
                     Friendship.status == 'accepted'),
                and_(Friendship.user_id == friend_id,
                     Friendship.friend_id == user_id,
                     Friendship.status == 'accepted')
            )
        ).first()
        return bool(friendship)

    @bp.route('/friends/chat/<int:friend_id>', methods=['GET'])
    @login_required
    def get_chat_history(friend_id):
        """Get chat history with a specific friend"""
        try:
            if not is_friend(current_user.id, friend_id):
                return jsonify({'error': 'Can only view messages from friends'}), 403

            # Get messages between current user and friend
            messages = Message.query.filter(
                or_(
                    and_(Message.sender_id == current_user.id,
                         Message.receiver_id == friend_id),
                    and_(Message.sender_id == friend_id,
                         Message.receiver_id == current_user.id)
                )
            ).order_by(Message.timestamp.asc()).all()

            # Mark unread messages as read
            unread_messages = [msg for msg in messages 
                             if msg.receiver_id == current_user.id and not msg.is_read]
            for msg in unread_messages:
                msg.is_read = True
            db.session.commit()

            return jsonify([{
                'id': msg.id,
                'sender_id': msg.sender_id,
                'sender_name': User.query.get(msg.sender_id).name,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'is_read': msg.is_read
            } for msg in messages])

        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return jsonify({'error': 'Failed to retrieve chat history'}), 500

    @bp.route('/friends/send/<int:friend_id>', methods=['POST'])
    @login_required
    def send_message(friend_id):
        """Send a message to a friend"""
        try:
            if not is_friend(current_user.id, friend_id):
                return jsonify({'error': 'Can only send messages to friends'}), 403

            data = request.json
            if not data or 'message' not in data:
                return jsonify({'error': 'Message content is required'}), 400

            message_text = data['message']
            
            # Check for inappropriate content
            if contains_hate_speech(message_text):
                return jsonify({'error': 'Message contains inappropriate content'}), 403

            # Create and save message
            message = Message(
                sender_id=current_user.id,
                receiver_id=friend_id,
                content=message_text,
                timestamp=datetime.utcnow(),
                is_read=False
            )
            db.session.add(message)
            db.session.commit()

            # Emit real-time notification
            socketio.emit(
                'new_message',
                {
                    'message_id': message.id,
                    'sender_id': current_user.id,
                    'sender_name': current_user.name,
                    'content': message_text,
                    'timestamp': message.timestamp.isoformat()
                },
                room=str(friend_id)
            )

            return jsonify({
                'message': 'Message sent successfully',
                'message_id': message.id
            })

        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            db.session.rollback()
            return jsonify({'error': 'Failed to send message'}), 500

    @bp.route('/friends/unread', methods=['GET'])
    @login_required
    def get_unread_counts():
        """Get count of unread messages from each friend"""
        try:
            # Get counts of unread messages grouped by sender
            unread_counts = db.session.query(
                Message.sender_id,
                db.func.count(Message.id).label('count')
            ).filter(
                Message.receiver_id == current_user.id,
                Message.is_read == False
            ).group_by(Message.sender_id).all()

            return jsonify([{
                'friend_id': sender_id,
                'friend_name': User.query.get(sender_id).name,
                'unread_count': count
            } for sender_id, count in unread_counts if is_friend(current_user.id, sender_id)])

        except Exception as e:
            logger.error(f"Error getting unread counts: {str(e)}")
            return jsonify({'error': 'Failed to get unread message counts'}), 500

    # Socket.IO event handlers
    @socketio.on('connect')
    def handle_connect():
        """Handle new WebSocket connection"""
        if current_user.is_authenticated:
            # Join a room named after the user's ID for private messages
            socketio.emit('user_connected', {'user_id': current_user.id})

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle WebSocket disconnection"""
        if current_user.is_authenticated:
            socketio.emit('user_disconnected', {'user_id': current_user.id})

    # Initialize Socket.IO for message events
    socketio.on_event('join', lambda: socketio.emit('joined', room=str(current_user.id)))
    socketio.on_event('leave', lambda: socketio.emit('left', room=str(current_user.id)))