from flask import request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from .utils import EmotionalChatbot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def emotionalbot_routes(bp, db, socketio):
    """Register emotional bot routes and WebSocket handlers"""
    
    # Initialize the chatbot
    bot = EmotionalChatbot()
    
    @bp.route('/chat', methods=['POST'])
    @login_required
    async def chat():
        """Handle chat interactions with emotion detection"""
        try:
            data = request.get_json()
            user_message = data.get('message')
            
            if not user_message:
                return jsonify({'error': 'Message is required'}), 400
                
            # Get response from bot
            response = await bot.generate_response(
                user_id=str(current_user.id),
                text=user_message
            )
            
            # Save interaction to database if needed
            # This could be useful for tracking emotional states over time
            
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error in chat endpoint: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    @bp.route('/chat/history', methods=['GET'])
    @login_required
    def get_chat_history():
        """Get user's chat history"""
        try:
            # Get the user's conversation memory
            memory = bot.get_memory(str(current_user.id))
            
            # Format the history
            history = []
            if memory.buffer:
                for message in memory.buffer:
                    history.append({
                        'content': message.content,
                        'type': 'user' if message.type == 'human' else 'bot',
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            return jsonify(history)
            
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return jsonify({'error': 'Failed to retrieve chat history'}), 500
    
    @socketio.on('connect')
    def handle_connect():
        """Handle WebSocket connection"""
        if current_user.is_authenticated:
            logger.info(f"WebSocket connected for user {current_user.id}")
            socketio.emit(
                'bot_message',
                {
                    'content': "Hello! I'm Joy, your emotional support companion. How are you feeling today?",
                    'type': 'greeting',
                    'timestamp': datetime.utcnow().isoformat()
                },
                room=request.sid
            )
    
    @socketio.on('user_message')
    async def handle_message(message):
        """Handle WebSocket messages"""
        if current_user.is_authenticated:
            try:
                # Get response from bot
                response = await bot.generate_response(
                    user_id=str(current_user.id),
                    text=message.get('content', '')
                )
                
                # Emit response
                socketio.emit('bot_response', response, room=request.sid)
                
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {str(e)}")
                socketio.emit('bot_error', {
                    'error': 'Failed to process message',
                    'timestamp': datetime.utcnow().isoformat()
                }, room=request.sid)
