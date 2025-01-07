import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from typing import Dict, Tuple, Optional
import logging
from langchain.llms import Ollama
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLTKManager:
    """Manages NLTK resources and initialization"""
    
    @staticmethod
    def initialize_resources():
        """Initialize required NLTK resources"""
        try:
            # Set NLTK data path to user's home directory
            home_dir = os.path.expanduser("~")
            nltk_data_dir = os.path.join(home_dir, "nltk_data")
            
            if not os.path.exists(nltk_data_dir):
                os.makedirs(nltk_data_dir)
            
            nltk.data.path.append(nltk_data_dir)
            
            # Download required resources
            resources = ['vader_lexicon', 'punkt', 'stopwords']
            for resource in resources:
                try:
                    nltk.data.find(f'tokenizers/{resource}' if resource != 'vader_lexicon' 
                                else f'sentiment/{resource}')
                except LookupError:
                    nltk.download(resource, download_dir=nltk_data_dir)
            
            return True
        except Exception as e:
            logger.error(f"Error initializing NLTK resources: {str(e)}")
            return False

class EmotionDetector:
    """Handles emotion detection in text"""
    
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        
        # Emotion keywords for different categories
        self.emotion_patterns = {
            'joy': ['happy', 'excited', 'delighted', 'grateful', 'love'],
            'sadness': ['sad', 'depressed', 'unhappy', 'miserable', 'lonely'],
            'anxiety': ['worried', 'anxious', 'nervous', 'scared', 'stressed'],
            'anger': ['angry', 'mad', 'furious', 'irritated', 'frustrated'],
            'hope': ['hope', 'optimistic', 'better', 'improve', 'positive'],
            'neutral': ['okay', 'fine', 'normal', 'alright']
        }
        
        self.crisis_keywords = [
            'suicide', 'kill', 'die', 'end it', 'worthless',
            'hopeless', "can't take it", 'give up'
        ]
    
    def analyze_emotion(self, text: str) -> Dict:
        """
        Analyze text for emotional content
        
        Args:
            text (str): User input text
            
        Returns:
            Dict containing emotion analysis results
        """
        # Get sentiment scores
        sentiment = self.sia.polarity_scores(text)
        
        # Count emotion keywords
        text_lower = text.lower()
        emotion_scores = {
            emotion: sum(1 for word in words if word in text_lower)
            for emotion, words in self.emotion_patterns.items()
        }
        
        # Determine primary emotion
        if sentiment['compound'] >= 0.5:
            primary_emotion = 'joy'
            confidence = sentiment['pos']
        elif sentiment['compound'] <= -0.5:
            primary_emotion = 'sadness'
            confidence = abs(sentiment['neg'])
        else:
            # Use keyword counts for neutral sentiment
            max_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            primary_emotion = max_emotion[0] if max_emotion[1] > 0 else 'neutral'
            confidence = max_emotion[1] / len(text.split()) if max_emotion[1] > 0 else 0.5
        
        # Check for crisis indicators
        crisis_level = sum(1 for word in self.crisis_keywords if word in text_lower)
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': confidence,
            'sentiment': sentiment,
            'emotion_scores': emotion_scores,
            'crisis_level': crisis_level
        }

class EmotionalChatbot:
    """Main emotional chatbot implementation"""
    
    def __init__(self):
        """Initialize the emotional chatbot"""
        self.llm = Ollama(model="llama3")
        self.emotion_detector = EmotionDetector()
        self.conversation_memories = {}  # Store memories per user
        
        # Response templates for different emotional states
        self.templates = {
            'joy': """You are Joy, an empathetic AI companion for the Smile Again platform.
                     Current emotional state: User is feeling positive
                     Approach: Share in their happiness and encourage expression
                     
                     Current conversation:
                     {history}
                     Human: {input}
                     Assistant:""",
                     
            'sadness': """You are Joy, an empathetic AI companion for the Smile Again platform.
                         Current emotional state: User is feeling down
                         Approach: Show understanding, validate feelings, offer gentle support
                         
                         Current conversation:
                         {history}
                         Human: {input}
                         Assistant:""",
                         
            'anxiety': """You are Joy, an empathetic AI companion for the Smile Again platform.
                         Current emotional state: User is feeling anxious
                         Approach: Provide calm reassurance, help with grounding
                         
                         Current conversation:
                         {history}
                         Human: {input}
                         Assistant:""",
                         
            'neutral': """You are Joy, an empathetic AI companion for the Smile Again platform.
                         Approach: Be warm and attentive while monitoring emotional state
                         
                         Current conversation:
                         {history}
                         Human: {input}
                         Assistant:"""
        }
    
    def get_crisis_response(self) -> Dict:
        """Generate response for crisis situations"""
        return {
            'content': """I hear how much pain you're in, and I want you to know that you're not alone. 
                       While I'm here to listen, it's important to talk to someone who can provide immediate help.
                       
                       Please consider these resources:
                       1. 24/7 Crisis Hotline: 988
                       2. Crisis Text Line: Text HOME to 741741
                       3. Emergency Services: 911
                       
                       Would you like me to connect you with a professional counselor?""",
            'type': 'crisis',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_memory(self, user_id: str) -> ConversationBufferMemory:
        """Get or create memory for a user"""
        if user_id not in self.conversation_memories:
            self.conversation_memories[user_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="history"
            )
        return self.conversation_memories[user_id]
    
    async def generate_response(self, user_id: str, text: str) -> Dict:
        """
        Generate a response to user input
        
        Args:
            user_id (str): Unique identifier for the user
            text (str): User's message
            
        Returns:
            Dict containing response and metadata
        """
        try:
            # Analyze emotion
            emotion_analysis = self.emotion_detector.analyze_emotion(text)
            
            # Check for crisis
            if emotion_analysis['crisis_level'] > 0:
                return self.get_crisis_response()
            
            # Get appropriate template
            template = self.templates.get(
                emotion_analysis['primary_emotion'], 
                self.templates['neutral']
            )
            
            # Create prompt and conversation chain
            prompt = PromptTemplate(
                input_variables=["history", "input"],
                template=template
            )
            
            conversation = ConversationChain(
                llm=self.llm,
                memory=self.get_memory(user_id),
                prompt=prompt,
                verbose=False
            )
            
            # Generate response
            response = await conversation.apredict(input=text)
            
            return {
                'content': response,
                'type': 'chat',
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': {
                    'emotion': emotion_analysis['primary_emotion'],
                    'confidence': emotion_analysis['confidence'],
                    'sentiment': emotion_analysis['sentiment']
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                'content': "I apologize, but I'm having trouble processing that right now. Could you try again?",
                'type': 'error',
                'timestamp': datetime.utcnow().isoformat()
            }

# Initialize NLTK resources when module is imported
NLTKManager.initialize_resources()
