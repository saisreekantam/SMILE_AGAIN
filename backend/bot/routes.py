from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
import logging
from models import Message
from .utils import WebEmpatheticChatbot
from typing import Dict, Any
import asyncio

# Configure logging
logger = logging.getLogger(__name__)

def register_routes(bp, db):
    """
    Register bot routes with the blueprint.
    
    Args:
        bp: Flask blueprint instance
        db: SQLAlchemy database instance
    """
    
    @bp.route('/chat', methods=['POST'])
    @login_required
    async def chat():
        """
        Handle chat interactions with emotion detection and Llama 3 responses.
        
        Returns:
            JSON response containing bot message and metadata
        """
        try:
            # Validate request
            data = request.get_json()
            user_message = data.get('message')
            
            if not user_message:
                return jsonify({'error': 'Message is required'}), 400

            logger.debug(f"Received message from user {current_user.id}: {user_message}")
            
            # Get bot instance
            chatbot = current_app.chatbot
            
            # Process message and get response
            response_data = await chatbot.generate_response(
                user_message, 
                current_user.id
            )
            
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
        """
        Get user's chat history with emotional context.
        
        Returns:
            JSON response containing chat history with metadata
        """
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
                
                # Include emotional metadata if available
                if msg.metadata:
                    message_data['metadata'] = msg.metadata
                
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
            return jsonify({'error': 'Failed to retrieve chat history
