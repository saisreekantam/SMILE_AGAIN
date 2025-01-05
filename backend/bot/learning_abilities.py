from datetime import datetime, timedelta
from sqlalchemy import func
import json
from backend.models import (
    ChatSession, ChatMessage, EmotionalPattern, 
    ResponseTemplate, ConversationFlow, UserPreference,
    BotLearning, SupportiveResource
)

class BotLearningSystem:
    def __init__(self, db):
        self.db = db

    def analyze_user_emotion(self, user_id, message_content):
        """Analyze user's emotional state from message"""
        # Here you would integrate with sentiment analysis service
        # For now using simple keyword matching
        emotions = {
            'joy': ['happy', 'great', 'wonderful', 'blessed', 'fantastic'],
            'sadness': ['sad', 'down', 'unhappy', 'depressed', 'miserable'],
            'anger': ['angry', 'frustrated', 'annoyed', 'mad', 'irritated'],
            'anxiety': ['worried', 'nervous', 'anxious', 'stressed', 'concerned'],
            'fear': ['scared', 'terrified', 'afraid', 'fearful', 'panicked']
        }
        
        message_lower = message_content.lower()
        detected_emotions = []
        
        for emotion, keywords in emotions.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_emotions.append(emotion)
        
        return detected_emotions[0] if detected_emotions else 'neutral'

    def update_emotional_pattern(self, user_id, emotion):
        """Track and update user's emotional patterns"""
        pattern = EmotionalPattern.query.filter_by(user_id=user_id).first()
        
        if not pattern:
            pattern = EmotionalPattern(
                user_id=user_id,
                pattern_type='daily',
                emotion_data={}
            )
            self.db.session.add(pattern)
        
        today = datetime.utcnow().date().isoformat()
        emotion_data = pattern.emotion_data or {}
        
        if today not in emotion_data:
            emotion_data[today] = {}
        
        if emotion in emotion_data[today]:
            emotion_data[today][emotion] += 1
        else:
            emotion_data[today][emotion] = 1
            
        pattern.emotion_data = emotion_data
        pattern.last_updated = datetime.utcnow()
        self.db.session.commit()

    def get_best_response_template(self, emotion, stress_level):
        """Get the most effective response template for the situation"""
        return ResponseTemplate.query.filter_by(
            emotion_context=emotion
        ).filter(
            ResponseTemplate.stress_level <= stress_level + 2,
            ResponseTemplate.stress_level >= stress_level - 2
        ).order_by(
            ResponseTemplate.success_rate.desc(),
            ResponseTemplate.use_count.desc()
        ).first()

    def update_response_success(self, template_id, success_rating):
        """Update success rate of response template"""
        template = ResponseTemplate.query.get(template_id)
        if template:
            template.use_count += 1
            template.success_rate = (
                (template.success_rate * (template.use_count - 1) + success_rating)
                / template.use_count
            )
            template.last_used = datetime.utcnow()
            self.db.session.commit()

    def learn_conversation_pattern(self, session_id):
        """Learn from successful conversation flows"""
        session = ChatSession.query.get(session_id)
        if not session or not session.messages:
            return

        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(
            ChatMessage.timestamp
        ).all()

        # Only learn from positive interactions
        positive_emotions = ['joy', 'neutral']
        if any(msg.response_rating >= 4 for msg in messages):
            flow = ConversationFlow(
                initial_emotion=messages[0].detected_emotion,
                steps=[{
                    'sender_type': msg.sender_type,
                    'emotion': msg.detected_emotion,
                    'sequence': idx
                } for idx, msg in enumerate(messages)],
                success_rate=1.0,
                avg_duration=len(messages)
            )
            self.db.session.add(flow)
            self.db.session.commit()

    def get_supportive_resource(self, emotion, stress_level):
        """Get appropriate supportive resource"""
        return SupportiveResource.query.filter(
            func.json_contains(
                SupportiveResource.applicable_emotions,
                json.dumps(emotion)
            ),
            func.json_contains(
                SupportiveResource.stress_level_range,
                json.dumps(stress_level)
            )
        ).order_by(
            SupportiveResource.success_count.desc()
        ).first()

    def update_user_preferences(self, user_id, interaction_data):
        """Update user preferences based on interactions"""
        pref = UserPreference.query.filter_by(user_id=user_id).first()
        if not pref:
            pref = UserPreference(user_id=user_id)
            self.db.session.add(pref)

        if 'humor_response' in interaction_data:
            pref.humor_level = (
                (pref.humor_level or 3) * 0.8 +
                interaction_data['humor_response'] * 0.2
            )

        if 'preferred_topics' in interaction_data:
            current_topics = pref.preferred_topics or []
            new_topics = interaction_data['preferred_topics']
            pref.preferred_topics = list(set(current_topics + new_topics))

        pref.last_updated = datetime.utcnow()
        self.db.session.commit()

    def get_learning_insights(self):
        """Get insights from learned patterns"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        return {
            'successful_patterns': ConversationFlow.query.filter(
                ConversationFlow.success_rate >= 0.8
            ).count(),
            'active_learnings': BotLearning.query.filter_by(
                is_active=True
            ).count(),
            'new_templates': ResponseTemplate.query.filter(
                ResponseTemplate.created_at >= week_ago
            ).count()
        }
