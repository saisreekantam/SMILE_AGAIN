from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import openai
from datetime import datetime
import json
import random
from .models import ChatSession, UserProblem, Message, User
from .utils import save_chat_history

chatbot_bp = Blueprint('chatbot', __name__)

# Configure OpenAI
openai.api_key = 'your-openai-api-key'

SYSTEM_PROMPT = """You are an empathetic and occasionally humorous AI friend named Joy, designed to help users of the Smile Again platform. Your personality traits:
- Warm and understanding, always validating users' feelings
- Occasionally uses appropriate humor to lighten the mood
- Provides practical suggestions and coping strategies
- Knows when to be serious and when to be light-hearted
- Can recognize signs of severe distress and recommend professional help
- Maintains context of conversations to provide personalized support"""

class SmileBot:
    def __init__(self, db):
        self.db = db
        self.joke_categories = {
            'motivation': [
                "Why did the gym close down? It just didn't work out! 💪😄",
                "What did the coffee say to the stressed person? Brew-the it! ☕️😊",
                "How does a positive thought read a book? One optimistic page at a time! 📚✨",
                "Why did the happiness app crash? Too many good vibes! 🌈😄",
                "What did the calendar say to Monday? You look fine! 📅😎"
            ],
            'mindfulness': [
                "Why do meditation apps make terrible comedians? They're always pausing for effect! 🧘‍♀️😄",
                "What did one yoga mat say to the other? Let's roll with it! 🤸‍♂️😊",
                "Why did the mindfulness teacher bring a ladder to class? To reach higher consciousness! 🪜✨",
                "What do you call a peaceful vegetable? A meditation! 🥬🧘‍♂️",
                "How does a zen master order a hot dog? Make me one with everything! 🌭😌"
            ],
            'friendship': [
                "Why did the cookie go to therapy? Because it was feeling crumbly! 🍪💝",
                "What did one friend say to another during meditation? You've got my om-divided attention! 🤗",
                "Why are group therapists great party planners? They know all about group dynamics! 👥💫",
                "What did one smile say to the other? It's been curve-y knowing you! 😊😄",
                "Why did the hug go to school? To become more uplifting! 🤗💕"
            ],
            'self_care': [
                "What did the bath bomb say to stress? It's time to fizz-le out! 🛁✨",
                "Why did the pillow go to the wellness center? It needed some fluff therapy! 🛏️😴",
                "What's a stressed person's favorite music? Calm-edy! 🎵😌",
                "How does a self-care day end? Happily spa after! 💆‍♀️✨",
                "Why did the relaxation app take a break? It needed some me-time! 📱🧘‍♀️"
            ],
            'resilience': [
                "What did one rainbow say to the other after the storm? We've got this arc covered! 🌈💪",
                "Why did the resilient tree take up meditation? To branch out into wellness! 🌳🧘‍♂️",
                "What did the optimist say to the pessimist? Let's look on the bright cider life! 🌟😊",
                "How does a positive thought cross the road? With confidence! 💫🚶‍♀️",
                "Why did the healing crystal go to school? To become more brilliant! 💎✨"
            ]
        }
    
    def analyze_sentiment(self, message):
        """Analyze message sentiment and stress level with comprehensive keyword detection"""
        high_stress_keywords = {
            'crisis_indicators': [
                'suicide', 'kill myself', 'end it all', 'better off dead',
                'no reason to live', 'can\'t go on', 'want to die'
            ],
            'emotional_distress': [
                'desperate', 'hopeless', 'worthless', 'helpless', 'trapped',
                'unbearable', 'miserable', 'suffering', 'overwhelmed', 'breaking down'
            ],
            'anxiety_indicators': [
                'panic', 'anxiety attack', 'can\'t breathe', 'heart racing',
                'terrified', 'paranoid', 'scared to death', 'extreme fear'
            ],
            'depression_indicators': [
                'severely depressed', 'deep depression', 'extreme sadness',
                'totally alone', 'completely numb', 'empty inside', 'no future'
            ],
            'social_isolation': [
                'nobody cares', 'all alone', 'no friends', 'nobody understands',
                'complete isolation', 'abandoned', 'rejected by everyone'
            ]
        }

        message_lower = message.lower()
        stress_indicators = {
            category: any(keyword in message_lower for keyword in keywords)
            for category, keywords in high_stress_keywords.items()
        }

        # Determine stress severity and type
        stress_level = sum(stress_indicators.values())
        primary_concern = None
        if stress_level > 0:
            primary_concern = next(
                (category for category, triggered in stress_indicators.items() if triggered),
                None
            )

        return {
            'is_high_stress': stress_level > 0,
            'stress_level': stress_level,
            'primary_concern': primary_concern
        }

    def generate_response(self, user_message, chat_history):
        """Generate contextual response using OpenAI"""
        try:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *chat_history,
                {"role": "user", "content": user_message}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )

            return response.choices[0].message.content

        except Exception as e:
            return "I'm having trouble processing that right now. Could you try rephrasing?"

    def add_humor(self, message, sentiment_analysis):
        """Add contextually appropriate humor based on conversation tone and user state"""
        if sentiment_analysis['is_high_stress']:
            return message  # No jokes during high-stress situations
        
        message_lower = message.lower()
        
        # Match joke category to context
        if any(word in message_lower for word in ['tired', 'exhausted', 'sleep']):
            category = 'self_care'
        elif any(word in message_lower for word in ['friend', 'alone', 'lonely']):
            category = 'friendship'
        elif any(word in message_lower for word in ['stress', 'anxiety', 'worried']):
            category = 'mindfulness'
        elif any(word in message_lower for word in ['give up', 'cant do it', 'difficult']):
            category = 'resilience'
        else:
            category = 'motivation'

        # Add encouraging emojis based on context
        emoji_sets = {
            'self_care': '💆‍♀️✨🌙',
            'friendship': '🤗💝👥',
            'mindfulness': '🧘‍♀️🌈✨',
            'resilience': '💪🌟🎯',
            'motivation': '🌈💫⭐'
        }

        selected_joke = random.choice(self.joke_categories[category])
        selected_emojis = emoji_sets[category]

        # Construct response with appropriate spacing and formatting
        return f"{message}\n\nHere's a little something to brighten your day {selected_emojis}\n{selected_joke}"

    def check_for_redirection(self, message):
        """Check if user needs to be redirected to specific features"""
        redirects = {
            'join group': '/chats/groups',
            'find friends': '/users/friends',
            'update profile': '/users/profile',
            'need professional help': '/counselors'
        }
        
        for key, url in redirects.items():
            if key in message.lower():
                return url
        return None

def create_chatbot_routes(app, db):
    bot = SmileBot(db)
    
    @chatbot_bp.route('/init', methods=['POST'])
    @login_required
    def initialize_chat():
        """Initialize a new chat session"""
        try:
            # Get or create chat session
            chat_session = ChatSession.query.filter_by(user_id=current_user.id).first()
            if not chat_session:
                chat_session = ChatSession(user_id=current_user.id)
                db.session.add(chat_session)
                db.session.commit()
            
            # Get user's problem category if available
            user_problem = UserProblem.query.filter_by(user_id=current_user.id).first()
            
            return jsonify({
                'session_id': chat_session.id,
                'initial_message': {
                    'content': f"Hi {current_user.name}! I'm Joy, your friendly companion at Smile Again! 🌟 How are you feeling today?",
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'bot'
                },
                'user_context': {
                    'has_existing_problem': bool(user_problem),
                    'last_interaction': chat_session.last_interaction.isoformat() if chat_session.last_interaction else None
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @chatbot_bp.route('/history', methods=['GET'])
    @login_required
    def get_chat_history():
        """Retrieve chat history for the current user"""
        try:
            chat_session = ChatSession.query.filter_by(user_id=current_user.id).first()
            if not chat_session:
                return jsonify({'messages': []})
            
            history = json.loads(chat_session.chat_history) if chat_session.chat_history else []
            return jsonify({'messages': history})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @chatbot_bp.route('/chat', methods=['POST'])
    @login_required
    def chat():
        data = request.json
        user_message = data.get('message')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # Get or create chat session
        chat_session = ChatSession.query.filter_by(user_id=current_user.id).first()
        if not chat_session:
            chat_session = ChatSession(user_id=current_user.id)
            db.session.add(chat_session)
        
        # Check for high stress indicators
        is_high_stress = bot.analyze_sentiment(user_message)
        
        # Generate response
        chat_history = json.loads(chat_session.chat_history) if chat_session.chat_history else []
        bot_response = bot.generate_response(user_message, chat_history)
        
        # Perform detailed sentiment analysis
        sentiment_result = bot.analyze_sentiment(user_message)
        
        # Add humor if appropriate based on sentiment
        bot_response = bot.add_humor(bot_response, sentiment_result)
        
        # Update stress tracking in session
        chat_session.stress_level = sentiment_result['stress_level']
        db.session.commit()
            
        # Check for needed redirections
        redirect_url = bot.check_for_redirection(user_message)
        
        # Save to chat history
        save_chat_history(db, current_user.id, user_message, bot_response)
        
        response_data = {
            'message': {
                'content': bot_response,
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'bot'
            },
            'metadata': {
                'is_high_stress': sentiment_result['is_high_stress'],
                'stress_level': sentiment_result['stress_level'],
                'primary_concern': sentiment_result['primary_concern'],
                'redirect_url': redirect_url,
                'suggestions': []
            }
        }
        
        # Add relevant suggestions based on stress level
        if sentiment_result['is_high_stress']:
            response_data['metadata']['suggestions'].append({
                'type': 'counselor_recommendation',
                'message': 'Would you like to speak with a professional counselor?',
                'action_url': '/counselors'
            })
        
        if is_high_stress:
            response_data['counselor_recommendation'] = True
            
        return jsonify(response_data)

    app.register_blueprint(chatbot_bp, url_prefix='/chatbot')
