import random
import re
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin
import webbrowser

from dotenv import load_dotenv
from models import Message
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from groclake.modellake import ModelLake
logger = logging.getLogger(__name__)

class WorkshopRedirectManager:
    """
    Manages workshop page redirection and link generation.
    """
    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        Initialize the workshop redirect manager.
        
        Args:
            base_url (str): Base URL for the frontend application
        """
        self.base_url = base_url
        self.workshops_path = "/workshops"
        
    def get_workshops_url(self) -> str:
        """
        Generate the complete workshops page URL.
        
        Returns:
            str: Full URL to the workshops page
        """
        try:
            return f"{self.base_url}{self.workshops_path}"
        except Exception as e:
            logger.error(f"Error generating workshops URL: {str(e)}")
            return f"http://localhost:3000/workshops"  # Fallback URL

    def redirect_to_workshops(self) -> bool:
        """
        Prepare redirection to workshops page.
        
        Returns:
            bool: True if URL generation successful, False otherwise
        """
        try:
            _ = self.get_workshops_url()
            return True
        except Exception as e:
            logger.error(f"Error preparing workshop redirect: {str(e)}")
            return False

    def get_workshop_by_emotion(self, emotion: str) -> Optional[str]:
        """
        Get specific workshop URL based on emotion.
        
        Args:
            emotion (str): Detected emotion
            
        Returns:
            Optional[str]: Workshop URL if available, None otherwise
        """
        try:
            emotion_workshop_paths = {
                'anxiety': '/workshops/anxiety-management',
                'depression': '/workshops/mood-lifting',
                'stress': '/workshops/stress-relief',
                'anger': '/workshops/anger-management',
                'loneliness': '/workshops/connection-building'
            }
            
            if emotion in emotion_workshop_paths:
                return f"{self.base_url}{emotion_workshop_paths[emotion]}"
            return self.get_workshops_url()
            
        except Exception as e:
            logger.error(f"Error getting emotion-specific workshop URL: {str(e)}")
            return self.get_workshops_url()

    def get_crisis_resources(self) -> Dict[str, str]:
        """
        Get crisis resource URLs.
        
        Returns:
            Dict[str, str]: Dictionary of crisis resource URLs
        """
        try:
            return {
                'emergency': f"{self.base_url}/crisis-support",
                'helpline': f"{self.base_url}/helpline",
                'resources': f"{self.base_url}/crisis-resources"
            }
        except Exception as e:
            logger.error(f"Error getting crisis resources: {str(e)}")
            return {
                'emergency': "http://localhost:3000/crisis-support",
                'helpline': "http://localhost:3000/helpline",
                'resources': "http://localhost:3000/crisis-resources"
            }

class CrisisDetector:
    """Enhanced detection system for crisis situations."""
    def __init__(self):
        """Initialize crisis patterns and regex patterns."""
        self.crisis_patterns = {
            'suicidal': [
                'suicide', 'kill myself', 'end it all', 'better off dead',
                'no reason to live', 'want to die', 'cant go on',
                'whats the point', 'give up', 'never wake up',
                'end my life', 'rather be dead', 'life is pointless'
            ],
            'severe_distress': [
                'cant handle', 'too painful', 'make it stop',
                'no hope', 'trapped', 'worthless', 'hopeless',
                'everything is dark', 'no way out', 'cant take it',
                'unbearable', 'suffocating', 'drowning in pain'
            ],
            'self_harm': [
                'cut myself', 'hurt myself', 'self harm', 'cause pain',
                'punish myself', 'deserve pain', 'feel pain'
            ],
            'immediate_danger': [
                'in danger', 'help me', 'emergency', 'hurt me',
                'threatening me', 'scared for my life', 'not safe'
            ]
        }
        
        # Create regex patterns for each crisis category
        self.crisis_regex = {
            category: re.compile(
                r'\b(' + '|'.join(map(re.escape, keywords)) + r')\b', 
                re.IGNORECASE
            ) for category, keywords in self.crisis_patterns.items()
        }
        
        # Additional context patterns for better accuracy
        self.context_patterns = {
            'future_planning': [
                'tomorrow', 'next week', 'plans', 'future',
                'looking forward', 'will do', 'going to'
            ],
            'support_seeking': [
                'need help', 'can you help', 'please help',
                'advice', 'guidance', 'support'
            ]
        }
        
        self.context_regex = {
            category: re.compile(
                r'\b(' + '|'.join(map(re.escape, keywords)) + r')\b', 
                re.IGNORECASE
            ) for category, keywords in self.context_patterns.items()
        }

    def detect_crisis(self, text: str) -> Tuple[bool, str, float]:
        """
        Detect potential crisis situations in user messages.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Tuple[bool, str, float]: (is_crisis, crisis_type, confidence)
        """
        try:
            text_lower = text.lower()
            
            # Check each crisis category
            crisis_matches = {}
            for category, pattern in self.crisis_regex.items():
                matches = pattern.findall(text_lower)
                if matches:
                    crisis_matches[category] = len(matches)
            
            # If no crisis patterns detected
            if not crisis_matches:
                return False, 'none', 0.0
            
            # Determine the primary crisis type
            primary_crisis = max(crisis_matches.items(), key=lambda x: x[1])[0]
            
            # Calculate base confidence
            base_confidence = min(crisis_matches[primary_crisis] * 0.3, 0.9)
            
            # Adjust confidence based on context
            confidence = self._adjust_confidence(text_lower, base_confidence)
            
            return True, primary_crisis, confidence
            
        except Exception as e:
            logger.error(f"Error in crisis detection: {str(e)}")
            return False, 'none', 0.0

    def _adjust_confidence(self, text: str, base_confidence: float) -> float:
        """
        Adjust crisis confidence based on contextual factors.
        
        Args:
            text (str): Input text
            base_confidence (float): Initial confidence score
            
        Returns:
            float: Adjusted confidence score
        """
        # Check for future planning (might lower crisis risk)
        future_matches = len(self.context_regex['future_planning'].findall(text))
        if future_matches > 0:
            base_confidence *= 0.8  # Reduce confidence if future planning present
            
        # Check for support seeking (might increase risk)
        support_matches = len(self.context_regex['support_seeking'].findall(text))
        if support_matches > 0:
            base_confidence = min(base_confidence * 1.2, 0.95)
            
        # Consider message length
        if len(text.split()) > 20:  # Longer messages might indicate more serious intent
            base_confidence *= 1.1
            
        return min(max(base_confidence, 0.0), 1.0)  # Ensure confidence stays between 0 and 1

    def get_risk_assessment(self, text: str) -> Dict[str, Any]:
        """
        Get a detailed risk assessment of the message.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict[str, Any]: Detailed risk assessment
        """
        is_crisis, crisis_type, confidence = self.detect_crisis(text)
        
        # Get all crisis indicators
        crisis_indicators = {
            category: len(pattern.findall(text.lower()))
            for category, pattern in self.crisis_regex.items()
        }
        
        # Get contextual factors
        context_factors = {
            category: len(pattern.findall(text.lower()))
            for category, pattern in self.context_regex.items()
        }
        
        return {
            'is_crisis': is_crisis,
            'crisis_type': crisis_type,
            'confidence': confidence,
            'crisis_indicators': crisis_indicators,
            'context_factors': context_factors,
            'risk_level': 'high' if confidence > 0.7 else 'medium' if confidence > 0.4 else 'low',
            'requires_immediate_action': confidence > 0.7 or crisis_type == 'immediate_danger'
        }

class EmotionDetector:
    """Detects emotions from user messages."""
    def __init__(self):
        # Define emotion patterns with keywords and emojis
        self.emotion_patterns = {
            'joy': ['happy', 'glad', 'excited', 'good', 'great', 'wonderful', 'fantastic', ':)', '😊', '😃', 'joyful', 'delighted'],
            'sadness': ['sad', 'unhappy', 'depressed', 'down', 'miserable', 'hurt', 'crying', ':(', '😢', '😭', 'upset', 'heartbroken'],
            'anger': ['angry', 'mad', 'frustrated', 'annoyed', 'furious', 'hate', '>:(', '😠', '😡', 'rage', 'irritated'],
            'anxiety': ['anxious', 'worried', 'nervous', 'scared', 'afraid', 'stressed', 'panic', '😰', '😨', 'tense', 'uneasy'],
            'overwhelmed': ['overwhelmed', 'exhausted', 'too much', 'cant handle', 'burnt out', '😫', '😩', 'drained', 'swamped'],
            'lonely': ['lonely', 'alone', 'isolated', 'abandoned', 'forgotten', '💔', 'solitary', 'friendless'],
            'hopeful': ['hopeful', 'optimistic', 'looking forward', 'better', 'improving', '🌱', 'promising', 'encouraged'],
            'grateful': ['grateful', 'thankful', 'blessed', 'appreciated', 'lucky', '🙏', 'appreciative'],
            'neutral': ['okay', 'fine', 'alright', 'normal', 'so-so', 'meh']
        }
        
        # Create regex patterns for each emotion
        self.emotion_regex = {
            emotion: re.compile(
                r'\b(' + '|'.join(map(re.escape, keywords)) + r')\b', 
                re.IGNORECASE
            ) for emotion, keywords in self.emotion_patterns.items()
        }

    def detect_emotion(self, text: str) -> Tuple[str, float]:
        """
        Detect the dominant emotion in text.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Tuple[str, float]: Detected emotion and confidence score
        """
        # Initialize emotion scores
        emotion_scores = {
            emotion: len(pattern.findall(text.lower()))
            for emotion, pattern in self.emotion_regex.items()
        }
        
        # Get the total matches
        total_matches = sum(emotion_scores.values())
        
        # If no emotions detected, return neutral with medium confidence
        if total_matches == 0:
            return 'neutral', 0.5
        
        # Find dominant emotion
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence based on proportion of dominant emotion matches
        confidence = emotion_scores[dominant_emotion] / total_matches
        
        # Apply emotion-specific adjustments
        if dominant_emotion == 'neutral':
            confidence = min(confidence, 0.6)  # Cap neutral confidence
        elif dominant_emotion in ['anxiety', 'sadness']:
            confidence = min(confidence * 1.2, 1.0)  # Boost for important emotions
            
        return dominant_emotion, confidence

    def get_emotion_summary(self, text: str) -> Dict[str, Any]:
        """
        Get a detailed summary of emotional content.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            Dict[str, Any]: Detailed emotion analysis
        """
        # Get primary emotion
        primary_emotion, confidence = self.detect_emotion(text)
        
        # Get all detected emotions
        detected_emotions = {
            emotion: len(pattern.findall(text.lower()))
            for emotion, pattern in self.emotion_regex.items()
            if len(pattern.findall(text.lower())) > 0
        }
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': confidence,
            'all_detected_emotions': detected_emotions,
            'emotional_intensity': sum(detected_emotions.values()) / len(text.split()),
            'mixed_emotions': len(detected_emotions) > 1
        }

class WebEmpatheticChatbot:
    """Enhanced chatbot with crisis detection and workshop integration."""
    def __init__(self, db=None):
        """Initialize the chatbot with database connection."""
        self.db = db
        self.emotion_detector = EmotionDetector()
        self.crisis_detector = CrisisDetector()
        self.redirect_manager = WorkshopRedirectManager()
        
        # Initialize coping exercises
        self.coping_exercises = {
            'anxiety': [
                "Let's try a gentle breathing exercise together! 🌬 Breathe in for 4 counts, hold for 4, and exhale for 4. Repeat this 3 times. 🍃",
                "Here's a quick grounding technique: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste 🌟",
                "Imagine you're in your favorite peaceful place - maybe a beach or garden. What do you see and hear there? 🏖",
                "Let's try the butterfly hug! Cross your arms over your chest, and alternate gentle taps on each shoulder 🦋",
                "How about we play the color game? Find 3 blue things, then 3 red things, then 3 green things in your surroundings 🎨",
                "Try this hand-warming exercise: Rub your palms together gently, then place them over your eyes. Feel the warmth melting tension away ✨"
            ],
            'sadness': [
                "Would you like to try something uplifting? Let's name three tiny things that brought even a small smile today ✨",
                "Sometimes a gentle walk or stretch can shift our energy. Want to take 5 steps or do a small stretch together? 🌈",
                "Let's practice self-care together! What's one kind thing you could do for yourself right now? 💝",
                "Shall we try the 'joy memory snapshot'? Think of a happy moment and describe it using all five senses 📸",
                "How about creating a tiny achievement? Even arranging three objects on your desk beautifully can spark joy ⭐",
                "Let's try 'comfort spotting' - can you find something soft, something warm, and something that makes you feel safe? 🧸"
            ],
            'anger': [
                "When emotions feel intense, try this: Take a slow, deep breath and count to 5 with me 🌬",
                "Here's a calming visualization: Picture your tension flowing away like water in a stream 🌊",
                "Would you like to try releasing some energy safely? Maybe squeezing a soft object or taking 10 big steps? 🍃",
                "Try this 'cool down' technique: Imagine you're a hot air balloon slowly releasing heated air and gently descending 🎈",
                "Let's do the 'strong tree' pose - stand tall, feel your feet grounded, and sway gently like branches in a breeze 🌳",
                "Here's a playful release: Draw your anger as weather (maybe a storm?) and watch it gradually change to sunshine ⛈→☀"
            ],
            # NEW: Added exercises for overwhelmed emotion
            'overwhelmed': [
                "Let's break things down into tiny steps. Can you name just ONE small thing to focus on right now? 🌱",
                "Try this 'pause and reset' technique: Close your eyes, count to 3, and imagine pressing a refresh button in your mind 🔄",
                "Here's a simple declutter exercise: Find three things in your space you can organize or put away 📦",
                "Let's do the 'energy bubble' - imagine a protective bubble around you, keeping out all extra demands and pressure 🫧",
                "Try this 'mental bookmark' technique: Like saving a webpage, we can pause your tasks and come back later 📑",
                "How about a quick 'responsibility release'? Write down what's overwhelming you, then fold the paper away for later 📝"
            ],
            # NEW: Added exercises for lonely emotion
            'lonely': [
                "Let's try the 'connection journal' - write a brief message to someone you care about, even if you don't send it 📝",
                "How about some 'self-company' time? Let's plan a tiny treat for yourself, like making your favorite drink ☕",
                "Try this 'virtual hug' exercise: Wrap your arms around yourself and imagine someone you love hugging you back 🤗",
                "Let's practice 'community spotting' - notice signs of human connection around you, like a neighbor's garden 🌺",
                "Try the 'kindness ripple' - do something nice for someone else, even something tiny like smiling at a stranger 💫",
                "How about creating a 'comfort corner'? Arrange a few objects that remind you of happy connections 🏡"
            ],
            # NEW: Added exercises for hopeful emotion
            'hopeful': [
                "Let's capture this hopeful moment! Write down or say aloud what's making you feel optimistic 📝✨",
                "Try this 'growth garden' visualization: Imagine your hopes as seeds, and picture them growing stronger 🌱",
                "How about creating a 'possibility list'? Name 3 things you're looking forward to, no matter how small 🎯",
                "Let's do the 'sunshine stretch' - reach up high and imagine drawing positive energy from above ☀",
                "Try this 'hope anchor' - choose an object to remind you of this hopeful feeling when you need it 🔱",
                "Create a little 'victory dance' to celebrate this moment of hope - even a tiny shoulder wiggle counts! 💃"
            ],
            # NEW: Added exercises for grateful emotion
            'grateful': [
                "Let's create a quick 'gratitude snapshot' - take 10 seconds to soak in this feeling of appreciation 📸",
                "Try the 'thank you ripple' - express gratitude to someone, even in a small way 💌",
                "How about a 'grateful senses' moment? Notice one thing you're grateful for with each sense 🌟",
                "Let's do the 'appreciation pause' - close your eyes and replay a moment you're thankful for 🎬",
                "Create a tiny 'gratitude ritual' - maybe a special smile or gesture to mark thankful moments ✨",
                "Try this 'gratitude glow' - imagine your feeling of thanks as a warm light spreading outward 🌅"
            ],
            'neutral': [
                "Want to try a mindful moment? Let's notice three interesting things in your surroundings ✨",
                "Here's a gentle suggestion: Take a moment to stretch and smile, even if it feels small 🌟",
                "Let's play 'curiosity explorer' - find something nearby you've never really noticed before 🔍",
                "Try this energy check-in: If your energy was music right now, what kind of tune would it be? 🎵",
                "How about a mini-adventure? Change your perspective by looking at your surroundings from a different angle 🌎",
                "Let's try the 'wonder wander' - let your mind freely explore what makes you curious right now 💭"
            ]
        }
        
        # Default fallback responses for different emotions
        self.fallback_responses = {
            'joy': "I'm happy to hear you're feeling positive! Would you like to share what's making you feel good? 😊",
            'sadness': "I hear that you're feeling down. I'm here to listen if you'd like to talk about it. 💜",
            'anger': "I can sense that you're frustrated. Would you like to talk about what's bothering you? 🌟",
            'anxiety': "It sounds like you're feeling anxious. Let's take a moment to breathe together. 🍃",
            'overwhelmed': "I understand feeling overwhelmed. Let's break things down into smaller steps. 🌱",
            'lonely': "I hear that you're feeling lonely. Remember, you're not alone - I'm here with you. 🤗",
            'neutral': "I'm here to chat and support you. How can I help make your day better? ✨",
            'hopeful': "It's wonderful that you're feeling hopeful! Let's build on that positive energy. 🌟",
            'grateful': "That's a beautiful sense of gratitude. Would you like to share more about it? 💫"
        }

        # Initialize prompt template and other configurations
        self.prompt_template = """
        You are Joy, a knowledgeable and empathetic friend who combines factual accuracy with emotional support. You naturally switch between informative and supportive responses based on what's needed.

        Current Context:
        - Emotion: {emotion} (confidence: {confidence})
        - Crisis: {is_crisis} (type: {crisis_type}, confidence: {crisis_confidence})
        - Workshop URL: {workshop_url}

        Chat History:
        {chat_history}

        User Message: {user_input}

        Available Coping Exercises:
        {coping_exercises}

        Instructions for Different Types of Responses:

        1. For Knowledge Questions (math, science, history, etc.):
           - Provide accurate, clear information first
           - Add friendly context or interesting facts
           - Use appropriate emojis to keep it engaging
           Example: 
           Q: "What's 15 × 7?"
           A: "That's 105! 🔢 Math is fun - want to try another one? I love number puzzles! ✨"

        2. For Technical Questions:
           - Give precise, factual answers
           - Include relevant details and context
           - Keep it informative but friendly
           Example:
           Q: "What is HTML?"
           A: "HTML is the standard language for creating web pages 🌐 It uses tags like <p> for paragraphs and <h1> for headings to structure content. Want to learn some basic tags? 💻"

        3. For Emotional Support:
           - Listen and validate feelings
           - Share personal warmth
           - Offer coping exercises only if natural
           Example:
           User: "I'm feeling down"
           Joy: "I hear you, and it's okay to feel this way 💝 Would you like to talk about it? I'm here to listen, no judgments at all 🤗"

        4. For Crisis Situations:
           - Show immediate care and understanding
           - Naturally mention professional help
           - Share workshop link if appropriate
           Example:
           User: "Everything feels hopeless"
           Joy: "I'm here with you right now, and I hear how much pain you're in 💗 There are people who want to help - I know some great professionals in our workshops who really understand these feelings. Would you like to connect with them? 🤝"

        Always:
        - Be naturally conversational
        - Show genuine interest
        - Balance professionalism with warmth
        - Use emojis thoughtfully
        - Keep responses clear and concise
        - Share knowledge with enthusiasm
        - Support with understanding
        - Maintain friendly boundaries

        Now respond as Joy:"""
        self.emotional_responses = {
            'sadness': [
                "I hear that you're feeling sad today. It takes courage to share these feelings, and I'm here to listen. Would you like to tell me more about what's making you feel this way? 💜",
                "I'm sorry you're feeling sad. Your feelings matter, and it's okay to not be okay sometimes. What's been on your mind? 🌱",
                "Thank you for sharing that with me. Sadness can feel heavy, but you don't have to carry it alone. Would you like to explore what might help lift your spirits a bit? ✨",
                "I can hear the sadness in your words, and I want you to know that I'm here to support you. Sometimes talking about it can help - would you like to share what's causing these feelings? 🫂"
            ],
            'depression': [
                "I hear you, and I want you to know that your feelings are valid. Depression can feel overwhelming, but you're not alone in this. Would you like to talk about what you're experiencing? 💜",
                "Thank you for trusting me with these feelings. Depression can be really challenging, but support is available. Can you tell me more about how you've been feeling lately? 🌱",
                "I'm here to listen without judgment. Sometimes depression can make us feel isolated, but you don't have to face this alone. Would you like to explore some gentle ways we might help you feel more supported? 🤗",
                "I understand that depression can make everything feel heavier. Your feelings matter, and I'm here to support you. Would you like to share what's been particularly difficult lately? ✨"
            ]
        }
        
        # Supportive follow-up suggestions
        self.support_suggestions = {
            'sadness': [
                "Would you like to try a gentle mood-lifting activity together?",
                "Sometimes taking small steps can help. Would you like to explore some simple self-care ideas?",
                "Would you like to hear about some activities that others have found helpful when feeling sad?",
                "I'm here to listen if you'd like to talk more, or we could try some calming exercises together."
            ],
            'depression': [
                "Would you like to know about some professional support resources available to you?",
                "Sometimes having a daily routine can help. Would you like to explore creating a gentle self-care plan?",
                "Would you like to try some simple grounding exercises together?",
                "I'm here to support you. Would you like to talk about what might help you feel more connected?"
            ]
        }

        def generate_emotional_response(self, emotion: str, user_message: str) -> str:
            """Generate an appropriate emotional response with support suggestions."""
            try:
                primary_response = random.choice(self.emotional_responses.get(
                    emotion, 
                    self.emotional_responses['sadness']  # Default to sadness responses
                ))
            
                follow_up = random.choice(self.support_suggestions.get(
                emotion,
                self.support_suggestions['sadness']  # Default to sadness suggestions
                ))
            
                return f"{primary_response}\n\n{follow_up}"
            
            except Exception as e:
                logger.error(f"Error generating emotional response: {str(e)}")
                return ("I hear you and I'm here to support you. Would you like to tell me more "
                   "about what you're feeling? 💜")
        # Initialize ModelLake
        load_dotenv()
        try:
           self.model_lake = ModelLake()
           self.memory = []
        except Exception as e:
            logger.error(f"Error initializing ModelLake: {str(e)}")
            raise

    def _get_fallback_response(self, emotion: str) -> Dict:
        """Get appropriate fallback response based on emotion."""
        return {
            'message': {
                'content': self.fallback_responses.get(
                    emotion,
                    "I'm here to support you. Would you like to tell me more? 💫"
                ),
                'type': 'bot'
            }
        }

    def _save_interaction(self, user_id, user_message, response, is_crisis=False, 
                         redirect_attempted=False, redirect_success=False):
        """Save chat interaction to database."""
        if not self.db:
            logger.warning("Database not initialized, skipping interaction save")
            return
            
        try:
            metadata = {
                'is_crisis': is_crisis,
                'redirect_attempted': redirect_attempted,
                'redirect_success': redirect_success
            }
            
            user_msg = Message(
                sender_id=user_id,
                content=user_message,
                timestamp=datetime.utcnow(),
                metadata=metadata
            )
            self.db.session.add(user_msg)
            
            bot_msg = Message(
                receiver_id=user_id,
                content=response,
                timestamp=datetime.utcnow(),
                metadata=metadata
            )
            self.db.session.add(bot_msg)
            
            self.db.session.commit()
            
        except Exception as e:
            logger.error(f"Error saving interaction: {str(e)}")
            if self.db:
                self.db.session.rollback()

    def _get_chat_history(self, user_id):
        """Get recent chat history for context."""
        if not self.db:
            return ""
            
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

    def generate_response(self, user_message: str, user_id: int) -> Dict:
        """Generate a response to the user's message."""
        try:
            # Detect emotion and crisis
            emotion, confidence = self.emotion_detector.detect_emotion(user_message)
            is_crisis, crisis_type, crisis_confidence = self.crisis_detector.detect_crisis(user_message)
            
            # Get workshop URL
            workshop_url = self.redirect_manager.get_workshops_url()
            
            # Handle crisis redirection
            should_redirect = is_crisis and crisis_confidence > 0.7
            if emotion in ['sadness', 'depression'] and confidence > 0.5:
                bot_reply = self.generate_emotional_response(emotion, user_message)
            if should_redirect:
                redirect_success = self.redirect_manager.redirect_to_workshops()
            else:
                redirect_success = False
            
            # Get chat history and relevant coping exercises
            chat_history = self._get_chat_history(user_id)
            exercises = self.coping_exercises.get(emotion, self.coping_exercises['neutral'])
            exercises_text = "\n".join(exercises)
            
            # Prepare system context for ModelLake
            system_context = {
                "role": "system",
                "content": self.prompt_template.format(
                    emotion=emotion,
                    confidence=confidence,
                    is_crisis=is_crisis,
                    crisis_type=crisis_type,
                    crisis_confidence=crisis_confidence,
                    workshop_url=workshop_url,
                    chat_history=chat_history,
                    user_input=user_message,
                    coping_exercises=exercises_text
                )
            }
            
            # Prepare messages for ModelLake
            messages = [system_context] + self.memory + [{"role": "user", "content": user_message}]
            
            # Generate response using ModelLake
            try:
                payload = {
                    "messages": messages,
                    "token_size": 300
                }
                response = self.model_lake.chat_complete(payload=payload)
                bot_reply = response.get('answer', '')
                
                # Update conversation memory
                self.memory.append({"role": "user", "content": user_message})
                self.memory.append({"role": "assistant", "content": bot_reply})
                
                # Keep memory size manageable
                if len(self.memory) > 10:  # Keep last 5 exchanges
                    self.memory = self.memory[-10:]
                    
            except Exception as e:
                logger.error(f"Error in ModelLake response generation: {str(e)}")
                return self._get_fallback_response(emotion)
            
            # Clean up response
            bot_reply = bot_reply.strip()
            
            # Save interaction to database
            self._save_interaction(
                user_id, 
                user_message, 
                bot_reply, 
                is_crisis,
                redirect_attempted=should_redirect,
                redirect_success=redirect_success
            )
            
            # Return complete response with metadata
            return {
                'message': {
                    'content': bot_reply,
                    'type': 'bot'
                },
                'metadata': {
                    'emotion': emotion,
                    'confidence': confidence,
                    'is_crisis': is_crisis,
                    'crisis_type': crisis_type if is_crisis else None,
                    'timestamp': datetime.now().isoformat(),
                    'workshop_url': workshop_url if should_redirect else None,
                    'redirect_attempted': should_redirect,
                    'redirect_success': redirect_success,
                    'requires_immediate_help': is_crisis and crisis_confidence > 0.7,
                    'counselor_referral': self._should_refer_to_counselor(emotion, confidence),
                    'suggested_exercises': exercises[:2] if 'exercises' in locals() else []
                }
            }
                
        except Exception as e:
            logger.error(f"Error in response generation: {str(e)}")
            return self._get_fallback_response(
                emotion if 'emotion' in locals() else 'neutral'
            )

    def _should_refer_to_counselor(self, emotion: str, confidence: float) -> bool:
        """Determine if user should be referred to a counselor."""
        high_risk_emotions = ['sadness', 'anxiety']
        return emotion in high_risk_emotions and confidence > 0.7