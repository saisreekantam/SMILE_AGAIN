from flask import request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from .utils import SmileBot
from backend.models import Message

def smilebot_routes(smilebot_bp, db):
    bot = SmileBot()
    
    @smilebot_bp.route('/chat', methods=['POST'])
    @login_required
    async def chat():
        """Handle chat interactions with emotion detection"""
        data = request.json
        user_message = data.get('message')
        image_data = data.get('image_data')  # Base64 encoded image from webcam
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

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

    @smilebot_bp.route('/chat/history', methods=['GET'])
    @login_required
    def get_chat_history():
        """Get user's chat history"""
        messages = Message.query.filter(
            (Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)
        ).order_by(Message.timestamp).all()

        chat_history = []
        for msg in messages:
            chat_history.append({
                'content': msg.content,
                'type': 'user' if msg.sender_id == current_user.id else 'bot',
                'timestamp': msg.timestamp.isoformat()
            })

        return jsonify(chat_history)
