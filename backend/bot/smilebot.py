from typing import Optional
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import openai
from datetime import datetime, timedelta
import json
import random
from .database_bot import (
    ChatSession, ChatMessage, UserEmotionalState, BotResponse,
    SmileProgress, UserInteractionPreference, SupportResource
)

chatbot_bp = Blueprint('chatbot', __name__)

# Configure OpenAI
openai.api_key = 'your-openai-api-key'

SYSTEM_PROMPT = """You are Joy, an empathetic and supportive AI companion for the Smile Again platform. Your goal is to help users rediscover their smile through:

Core traits:
- Warm, understanding, and genuinely caring
- Validates feelings while gently encouraging positive steps
- Uses appropriate humor to lift spirits when suitable
- Provides practical coping strategies and smile-inducing activities
- Recognizes emotional states and adapts communication style
- Celebrates small wins and progress in the smile journey

Key responsibilities:
- Help users identify what makes them smile
- Guide them through difficult moments with empathy
- Share uplifting stories and activities
- Provide emotional support and understanding
- Connect users to professional help when needed
- Track and celebrate smile progress"""

class SmileBot:
    def __init__(self, db):
        self.db = db
        self.mood_emojis = {
            'joy': '😊', 'peace': '😌', 'hope': '🌟',
            'sadness': '😔', 'anxiety': '😰', 'stress': '😓',
            'neutral': '🙂', 'progress': '💫', 'motivation': '💪'
        }
        # Initialize joke categories (same as before)
        self.joke_categories = {...}  # Your existing joke categories

    async def analyze_emotional_state(self, message: str, user_id: int) -> dict:
        """Enhanced emotional analysis with smile focus"""
        # Get user's emotional history
        emotional_state = UserEmotionalState.query.filter_by(
            user_id=user_id,
            date=datetime.utcnow().date()
        ).first()

        # Analyze current message
        sentiment = self._analyze_sentiment_and_stress(message)
        
        # Update emotional state
        if emotional_state:
            emotional_state.mood_pattern[datetime.utcnow().strftime('%H:%M')] = sentiment
            if 'smile' in message.lower() or 'happy' in message.lower():
                emotional_state.smile_frequency += 1
        else:
            emotional_state = UserEmotionalState(
                user_id=user_id,
                mood_pattern={datetime.utcnow().strftime('%H:%M'): sentiment},
                stress_level=sentiment['stress_level']
            )
            self.db.session.add(emotional_state)
        
        self.db.session.commit()
        return sentiment

    def _analyze_sentiment_and_stress(self, message: str) -> dict:
        """Analyze message for emotional content and stress indicators"""
        # Your existing sentiment analysis code here
        # Add smile-specific analysis
        smile_indicators = {
            'positive': ['smile', 'happy', 'laugh', 'joy', 'better', 'hope'],
            'negative': ['cant smile', 'lost smile', 'never smile', 'fake smile']
        }
        
        message_lower = message.lower()
        smile_state = {
            'can_smile': any(word in message_lower for word in smile_indicators['positive']),
            'smile_difficulty': any(word in message_lower for word in smile_indicators['negative'])
        }
        
        # Combine with your existing stress analysis
        stress_analysis = self.analyze_sentiment(message)
        return {**stress_analysis, **smile_state}

    async def generate_response(self, user_id: int, message: str, session_id: int) -> dict:
        """Generate personalized response with smile focus"""
        try:
            # Get user preferences and context
            user_pref = UserInteractionPreference.query.filter_by(user_id=user_id).first()
            emotional_state = await self.analyze_emotional_state(message, user_id)
            
            # Get chat history
            chat_history = ChatMessage.query.filter_by(
                session_id=session_id
            ).order_by(ChatMessage.timestamp.desc()).limit(5).all()
            
            # Build conversation context
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": f"User's smile progress: {self._get_smile_progress(user_id)}"}
            ]
            
            # Add chat history
            for msg in reversed(chat_history):
                messages.append({
                    "role": "user" if msg.sender_type == "user" else "assistant",
                    "content": msg.content
                })
            
            # Add current message
            messages.append({"role": "user", "content": message})

            # Generate response
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )

            bot_response = response.choices[0].message.content

            # Add appropriate humor if needed
            if not emotional_state['is_high_stress'] and user_pref and user_pref.humor_preference > 3:
                bot_response = self.add_humor(bot_response, emotional_state)

            # Save interaction
            chat_message = ChatMessage(
                session_id=session_id,
                sender_type='bot',
                content=bot_response,
                detected_emotion=emotional_state.get('primary_concern'),
                stress_indicator=emotional_state.get('stress_level')
            )
            self.db.session.add(chat_message)
            
            # Get relevant support resource
            resource = self._get_relevant_resource(emotional_state)
            
            # Prepare response data
            response_data = {
                'message': {
                    'content': bot_response,
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'bot'
                },
                'metadata': {
                    'emotional_state': emotional_state,
                    'resource': resource.content if resource else None,
                    'smile_progress': self._get_smile_progress(user_id),
                    'suggestions': self._generate_suggestions(emotional_state)
                }
            }

            return response_data

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                'message': {
                    'content': "I'm having a moment. Could you try that again?",
                    'type': 'bot'
                }
            }

    def _get_smile_progress(self, user_id: int) -> dict:
        """Get user's smile journey progress"""
        progress = SmileProgress.query.filter_by(
            user_id=user_id
        ).order_by(SmileProgress.date.desc()).first()
        
        if not progress:
            return {'status': 'beginning', 'score': 0}
            
        return {
            'status': 'progressing' if progress.smile_score > 5 else 'beginning',
            'score': progress.smile_score,
            'recent_wins': progress.strategies_working
        }

    def _get_relevant_resource(self, emotional_state: dict) -> Optional[SupportResource]:
        """Get appropriate support resource based on emotional state"""
        return SupportResource.query.filter(
            SupportResource.applicable_emotions.contains(emotional_state['primary_concern']),
            SupportResource.stress_level_range['min'] <= emotional_state['stress_level'],
            SupportResource.stress_level_range['max'] >= emotional_state['stress_level']
        ).order_by(SupportResource.success_count.desc()).first()

    def _generate_suggestions(self, emotional_state: dict) -> list:
        """Generate contextual suggestions based on emotional state"""
        suggestions = []
        
        if emotional_state['stress_level'] > 7:
            suggestions.append({
                'type': 'professional_help',
                'message': "Would you like to talk to one of our counselors?",
                'action': '/counselors'
            })
            
        if emotional_state.get('smile_difficulty'):
            suggestions.append({
                'type': 'smile_exercise',
                'message': "Let's try a simple smile exercise together",
                'action': '/exercises/smile'
            })
            
        return suggestions

# Initialize routes
def create_chatbot_routes(app, db):
    bot = SmileBot(db)
    
    # Your existing routes with updated response handling
    @chatbot_bp.route('/chat', methods=['POST'])
    @login_required
    async def chat():
        data = request.json
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # Get or create session
        session = ChatSession.query.filter_by(user_id=current_user.id).first()
        if not session:
            session = ChatSession(user_id=current_user.id)
            db.session.add(session)
            db.session.commit()

        # Save user message
        user_msg = ChatMessage(
            session_id=session.id,
            sender_type='user',
            content=user_message
        )
        db.session.add(user_msg)
        db.session.commit()

        # Generate response
        response_data = await bot.generate_response(
            user_id=current_user.id,
            message=user_message,
            session_id=session.id
        )
        
        return jsonify(response_data)

    # Add your other routes here
    
    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
