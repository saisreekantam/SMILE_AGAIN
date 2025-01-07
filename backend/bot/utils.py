# bot/utils.py
import re
from datetime import datetime
import logging
from models import Message
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

logger = logging.getLogger(__name__)

class EmotionDetector:
    def __init__(self):
        self.emotion_patterns = {
            'joy': ['happy', 'glad', 'excited', 'good', 'great', 'wonderful', 'fantastic', ':)', '😊', '😃'],
            'sadness': ['sad', 'unhappy', 'depressed', 'down', 'miserable', 'hurt', 'crying', ':(', '😢', '😭'],
            'anger': ['angry', 'mad', 'frustrated', 'annoyed', 'furious', 'hate', '>:(', '😠', '😡'],
            'anxiety': ['anxious', 'worried', 'nervous', 'scared', 'afraid', 'stressed', 'panic', '😰', '😨'],
            'neutral': ['okay', 'fine', 'alright', 'normal']
        }
        
        self.emotion_regex = {
            emotion: re.compile(r'\b(' + '|'.join(map(re.escape, keywords)) + r')\b', 
                              re.IGNORECASE) 
            for emotion, keywords in self.emotion_patterns.items()
        }

    def detect_emotion(self, text):
        emotion_scores = {
            emotion: len(pattern.findall(text.lower()))
            for emotion, pattern in self.emotion_regex.items()
        }
        
        max_score = max(emotion_scores.values())
        if max_score == 0:
            return 'neutral', 0.5
        
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        confidence = max_score / (sum(emotion_scores.values()) or 1)
        
        return dominant_emotion, confidence

class WebEmpatheticChatbot:
    def __init__(self, db):
        self.db = db
        self.emotion_detector = EmotionDetector()
        
        # Initialize Llama 3
        self.prompt_template = """
        You are Joy, an empathetic AI companion designed to help users find happiness and emotional support.
        Your role is to provide understanding, warmth, and appropriate emotional support while maintaining authenticity.
        
        Current emotional context: The user appears to be feeling {emotion} (confidence: {confidence:.2f})
        
        Previous conversation context:
        {chat_history}
        
        User's message: {user_input}
        
        Respond with empathy and understanding while:
        1. Acknowledging their current emotional state
        2. Offering supportive and constructive perspectives
        3. Encouraging healthy expression and coping mechanisms
        4. Being genuine and warm in your response
        5. Providing specific suggestions or insights when appropriate
        
        Your response should feel natural and caring, like talking to a supportive friend.
        Keep your response concise but meaningful (2-3 sentences).

        Joy's response:
        """
        
        try:
            self.llm = Ollama(model="llama3")  # Using llama2 model
            self.memory = ConversationBufferMemory(
                input_key="user_input",
                memory_key="chat_history"
            )
            self.prompt = PromptTemplate(
                input_variables=["emotion", "confidence", "chat_history", "user_input"],
                template=self.prompt_template
            )
            self.conversation = LLMChain(
                llm=self.llm,
                prompt=self.prompt,
                memory=self.memory,
                verbose=True
            )
        except Exception as e:
            logger.error(f"Error initializing Llama: {str(e)}")
            raise

    def _get_chat_history(self, user_id):
        """Get recent chat history for context."""
        try:
            recent_messages = Message.query.filter(
                ((Message.sender_id == user_id) | (Message.receiver_id == user_id))
            ).order_by(Message.timestamp.desc()).limit(5).all()
            
            return "\n".join([
                f"{'User' if msg.sender_id == user_id else 'Joy'}: {msg.content}"
                for msg in reversed(recent_messages)
            ])
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return ""

    def generate_response(self, user_message, user_id):
        """Generate response using Llama 3 and emotion detection."""
        try:
            # Detect emotion
            emotion, confidence = self.emotion_detector.detect_emotion(user_message)
            
            # Get chat history
            chat_history = self._get_chat_history(user_id)
            
            # Generate response using Llama
            response = self.conversation.predict(
                emotion=emotion,
                confidence=confidence,
                chat_history=chat_history,
                user_input=user_message
            )
            
            # Clean up response
            response = response.strip()
            
            # Save interaction
            self._save_interaction(user_id, user_message, response)
            
            return {
                'message': {
                    'content': response,
                    'type': 'bot'
                },
                'metadata': {
                    'emotion': emotion,
                    'confidence': confidence,
                    'timestamp': datetime.now().isoformat(),
                    'counselor_referral': self._should_refer_to_counselor(emotion, confidence)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_fallback_response(emotion if 'emotion' in locals() else 'neutral')

    def _save_interaction(self, user_id, user_message, response):
        """Save chat interaction to database."""
        try:
            # Save user message
            user_msg = Message(
                sender_id=user_id,
                content=user_message,
                timestamp=datetime.utcnow()
            )
            self.db.session.add(user_msg)
            
            # Save bot response
            bot_msg = Message(
                receiver_id=user_id,
                content=response,
                timestamp=datetime.utcnow()
            )
            self.db.session.add(bot_msg)
            
            self.db.session.commit()
            
        except Exception as e:
            logger.error(f"Error saving interaction: {str(e)}")
            self.db.session.rollback()

    def _should_refer_to_counselor(self, emotion, confidence):
        """Determine if user should be referred to a counselor."""
        high_risk_emotions = ['sadness', 'anxiety']
        return emotion in high_risk_emotions and confidence > 0.7

    def _get_fallback_response(self, emotion):
        """Generate appropriate fallback response based on emotion."""
        fallback_responses = {
            'joy': "I'm glad you're feeling positive! Would you like to tell me more about what's making you happy?",
            'sadness': "I sense that you might be going through a difficult time. I'm here to listen if you'd like to share more.",
            'anxiety': "It's okay to feel anxious. We can take things step by step. Would you like to talk about what's on your mind?",
            'anger': "I understand you're feeling frustrated. Would you like to tell me more about what's bothering you?",
            'neutral': "I'm here to listen and chat. How would you like to continue our conversation?"
        }
        
        return {
            'message': {
                'content': fallback_responses.get(emotion, fallback_responses['neutral']),
                'type': 'bot'
            },
            'metadata': {
                'emotion': emotion,
                'confidence': 0.5,
                'timestamp': datetime.now().isoformat(),
                'fallback': True
            }
        }