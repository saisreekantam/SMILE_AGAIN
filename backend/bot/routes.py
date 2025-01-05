# bot/routes.py
from flask import request, jsonify, Blueprint
from flask_login import login_required, current_user
from datetime import datetime
from .utils import SmileBot
from models import Message
import logging

logger = logging.getLogger(__name__)

def register_routes(bp, db):
    bot = SmileBot()
    
    @bp.route('/chat', methods=['POST'])
    @login_required
    async def chat():
        """Handle chat interactions with emotion detection"""


        try:
            data = request.get_json()
            user_message = data.get('message')
            image_data = data.get('image_data')  # Base64 encoded image from webcam
            
            if not user_message:
                return jsonify({'error': 'Message is required'}), 400

            logger.debug(f"Received message: {user_message}")

            # Save user message
            user_msg = Message(
                sender_id=current_user.id,
                content=user_message,
                timestamp=datetime.utcnow()
            )
            db.session.add(user_msg)
            db.session.commit()

            # Get recent chat history
            chat_history = Message.query.filter(
                (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
            ).order_by(Message.timestamp.desc()).limit(5).all()

            history_formatted = [
                {
                    'content': msg.content,
                    'sender_type': 'user' if msg.sender_id == current_user.id else 'bot',
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in reversed(chat_history)
            ]

            # Generate bot response with emotion analysis
            response_data = await bot.generate_response(
                text=user_message,
                image_data=image_data,
                chat_history=history_formatted
            )
            
            # Save bot response
            bot_msg = Message(
                receiver_id=current_user.id,
                content=response_data['message']['content'],
                timestamp=datetime.utcnow()
            )
            db.session.add(bot_msg)
            db.session.commit()
            
            return jsonify(response_data)

        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}")
            db.session.rollback()
            return jsonify({'error': 'Internal server error'}), 500

    @bp.route('/chat/history', methods=['GET', 'OPTIONS'])
    @login_required
    def get_chat_history():
        """Get user's chat history"""
        if request.method == 'OPTIONS':
            return jsonify({"message": "OK"}), 200

        try:
            messages = Message.query.filter(
                (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
            ).order_by(Message.timestamp).all()

            chat_history = [
                {
                    'content': msg.content,
                    'type': 'user' if msg.sender_id == current_user.id else 'bot',
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in messages
            ]

            return jsonify(chat_history)

        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return jsonify({'error': 'Failed to retrieve chat history'}), 500

    return bp