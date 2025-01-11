# bot/routes.py
from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
import logging
from models import Message
from .utils import WebEmpatheticChatbot

logger = logging.getLogger(__name__)

def register_routes(bp, db):
    # Initialize chatbot instance
    chatbot = WebEmpatheticChatbot()

    @bp.route('/chat', methods=['POST', 'OPTIONS'])
    @login_required
    def chat():
        """
        Handle chat interactions with emotion detection and response generation.
        """
        # Handle preflight OPTIONS request
        if request.method == 'OPTIONS':
            response = current_app.make_default_options_response()
            return response

        try:
            # Validate request
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
                
            user_message = data.get('message')
            if not user_message:
                return jsonify({'error': 'Message is required'}), 400

            logger.debug(f"Received message from user {current_user.id}: {user_message}")
            
            # Generate response using chatbot instance
            response_data = chatbot.generate_response(user_message, current_user.id)
            return jsonify(response_data)

        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': {
                    'content': "I apologize, but I'm having trouble processing your message. Could you please try again?",
                    'type': 'bot'
                }
            }), 500

    @bp.route('/chat/history', methods=['GET'])
    @login_required
    def get_chat_history():
        try:
            # Get messages with pagination
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            messages = Message.query.filter(
                (Message.sender_id == current_user.id) | 
                (Message.receiver_id == current_user.id)
            ).order_by(
                Message.timestamp.desc()
            ).paginate(
                page=page, 
                per_page=per_page,
                error_out=False
            )

            chat_history = []
            for msg in messages.items:
                message_data = {
                    'id': msg.id,
                    'content': msg.content,
                    'type': 'user' if msg.sender_id == current_user.id else 'bot',
                    'timestamp': msg.timestamp.isoformat()
                }
                chat_history.append(message_data)

            return jsonify({
                'messages': chat_history,
                'pagination': {
                    'total': messages.total,
                    'pages': messages.pages,
                    'current': messages.page,
                    'per_page': messages.per_page
                }
            })

        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return jsonify({'error': 'Failed to retrieve chat history'}), 500