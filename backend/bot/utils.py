from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import logging
from models import Message, User

logger = logging.getLogger(__name__)

class EmotionDetector:
    """
    Emotion detection system using keyword matching and pattern recognition.
    Optimized for web-based chat interactions.
    """
    def __init__(self):
        # Define emotion categories with associated keywords
        self.emotion_patterns = {
            'joy': ['happy', 'glad', 'excited', 'good', 'great', 'wonderful', 'fantastic', ':)', '😊', '😃'],
            'sadness': ['sad', 'unhappy', 'depressed', 'down', 'miserable', 'hurt', 'crying', ':(', '😢', '😭'],
            'anger': ['angry', 'mad', 'frustrated', 'annoyed', 'furious', 'hate', '>:(', '😠', '😡'],
            'anxiety': ['anxious', 'worried', 'nervous', 'scared', 'afraid', 'stressed', 'panic', '😰', '😨'],
            'neutral': ['okay', 'fine', 'alright', 'normal']
        }
        
        # Compile regex patterns for efficient emotion detection
        self.emotion_regex = {
            emotion: re.compile(r'\b(' + '|'.join(map(re.escape, keywords)) + r')\b', 
                              re.IGNORECASE) 
            for emotion, keywords in self.emotion_patterns.items()
        }

    def detect_emotion(self, text: str) -> Tuple[str, float]:
        """
        Detect the primary emotion in the text and return confidence score.
        
        Args:
            text (str): User input text to analyze
            
        Returns:
            Tuple[str, float]: Detected emotion and confidence score
        """
        emotion_scores = {emotion: len(pattern.findall(text.lower()))
                         for emotion, pattern in self.emotion_regex.items()}
        
        max_score = max(emotion_scores.values())
        if max_score == 0:
            return 'neutral', 0.5
        
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        confidence = max_score / (sum(emotion_scores.values()) or 1)
        
        return dominant_emotion, confidence

class WebEmpatheticChatbot:
    """
    Web-integrated empathetic chatbot powered by Llama 3.
    Designed for seamless integration with Flask backend.
    """
    def __init__(self, db):
        self.emotion_detector = EmotionDetector()
        self.db = db
        
        # Initialize Llama 3 with emotion-aware prompting
        self.prompt_template = """
        You are Joy, an empathetic AI companion designed to help users find happiness and emotional support.
        You should respond with understanding, warmth, and appropriate emotional support.
        
        Current emotional context: The user is feeling {emotion} (confidence: {confidence})
        
        Previous conversation:
        {chat_history}
        
        User's message: {user_input}
        
        Please provide an empathetic response that:
        1. Acknowledges their emotional state
        2. Shows understanding and support
        3. Encourages healthy expression and coping
        4. Maintains a warm, caring tone
        
        Joy's response:
        """
        
        # Initialize LangChain components
        self.prompt = PromptTemplate(
            input_variables=["emotion", "confidence", "chat_history", "user_input"],
            template=self.prompt_template
        )
        
        try:
            self.llm = Ollama(model="llama3")
            self.memory = ConversationBufferMemory(
                input_key="user_input",
                memory_key="chat_history"
            )
            self.conversation = LLMChain(
                llm=self.llm,
                prompt=self.prompt,
                memory=self.memory,
                verbose=True
            )
        except Exception as e:
            logger.error(f"Error initializing Llama 3: {str(e)}")
            raise

    async def generate_response(self, user_input: str, user_id: int) -> Dict:
        """
        Generate an empathetic response for web interface.
        
        Args:
            user_input (str): User's message
            user_id (int): ID of the current user
            
        Returns:
            Dict: Response data with message content and metadata
        """
        try:
            # Detect emotion
            emotion, confidence = self.emotion_detector.detect_emotion(user_input)
            
            # Get recent chat history
            chat_history = self._get_chat_history(user_id)
            
            # Generate response using Llama 3
            response = await self.conversation.apredict(
                emotion=emotion,
                confidence=confidence,
                chat_history=chat_history,
                user_input=user_input
            )
            
            # Save interaction to database
            self._save_interaction(user_id, user_input, response, emotion, confidence)
            
            return {
                'message': {
                    'content': response,
                    'type': 'bot'
                },
                'metadata': {
                    'detected_emotion': emotion,
                    'confidence': confidence,
                    'timestamp': datetime.now().isoformat(),
                    'counselor_referral': self.should_refer_to_counselor(user_id)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_fallback_response(emotion if 'emotion' in locals() else 'neutral')

    def _get_chat_history(self, user_id: int) -> str:
        """Get formatted chat history for the user."""
        recent_messages = Message.query.filter(
            ((Message.sender_id == user_id) | (Message.receiver_id == user_id))
        ).order_by(Message.timestamp.desc()).limit(5).all()
        
        return "\n".join([
            f"{'User' if msg.sender_id == user_id else 'Joy'}: {msg.content}"
            for msg in reversed(recent_messages)
        ])

    def _save_interaction(self, user_id: int, user_input: str, response: str, 
                         emotion: str, confidence: float):
        """Save the interaction to database."""
        try:
            # Save user message
            user_msg = Message(
                sender_id=user_id,
                content=user_input,
                timestamp=datetime.utcnow(),
                metadata={'emotion': emotion, 'confidence': confidence}
            )
            self.db.session.add(user_msg)
            
            # Save bot response
            bot_msg = Message(
                receiver_id=user_id,
                content=response,
                timestamp=datetime.utcnow(),
                metadata={'emotion': emotion, 'confidence': confidence}
            )
            self.db.session.add(bot_msg)
            
            self.db.session.commit()
            
        except Exception as e:
            logger.error(f"Error saving interaction: {str(e)}")
            self.db.session.rollback()
            raise

    def _get_fallback_response(self, emotion: str) -> Dict:
        """Generate fallback response when LLM fails."""
        fallback_templates = {
            'joy': "I'm glad you're feeling positive! Would you like to share more?",
            'sadness': "I hear that you're going through a difficult time. I'm here to listen.",
            'anger': "I understand you're feeling frustrated. Would you like to talk about it?",
            'anxiety': "It's okay to feel anxious. Let's take this one step at a time.",
            'neutral': "I'm here to chat if you'd like to share anything."
        }
        
        return {
            'message': {
                'content': fallback_templates.get(emotion, "I'm here to listen and support you."),
                'type': 'bot'
            },
            'metadata': {
                'detected_emotion': emotion,
                'confidence': 0.5,
                'timestamp': datetime.now().isoformat(),
                'fallback': True
            }
        }

    def get_stress_level(self, user_id: int) -> float:
        """Calculate user's current stress level."""
        recent_messages = Message.query.filter(
            Message.sender_id == user_id
        ).order_by(Message.timestamp.desc()).limit(5).all()
        
        if not recent_messages:
            return 0.0
        
        stress_weights = {
            'joy': 0.0,
            'sadness': 0.6,
            'anger': 0.8,
            'anxiety': 0.9,
            'neutral': 0.3
        }
        
        total_stress = sum(
            stress_weights[msg.metadata.get('emotion', 'neutral')]
            for msg in recent_messages
            if msg.metadata
        )
        
        return total_stress / len(recent_messages)

    def should_refer_to_counselor(self, user_id: int) -> bool:
        """Determine if user should be referred to a professional counselor."""
        return self.get_stress_level(user_id) > 0.7
