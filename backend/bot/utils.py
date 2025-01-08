import re
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin
import webbrowser
from models import Message
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

logger = logging.getLogger(__name__)

class WorkshopRedirectManager:
    """
    Manages workshop page redirection and link generation.
    """
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.workshops_path = "/workshops"
        
    def get_workshops_url(self) -> str:
        """
        Generate the complete workshops page URL.
        
        Returns:
            str: Full URL to the workshops page
        """
        return urljoin(self.base_url, self.workshops_path)
    
    def redirect_to_workshops(self) -> bool:
        """
        Attempt to open the workshops page in the default browser.
        """
        try:
            url = self.get_workshops_url()
            webbrowser.open(url)
            return True
        except Exception as e:
            logger.error(f"Error opening workshops page: {str(e)}")
            return False

class CrisisDetector:
    """Enhanced detection system for crisis situations."""
    def __init__(self):
        self.crisis_patterns = {
            'suicidal': [
                'suicide', 'kill myself', 'end it all', 'better off dead',
                'no reason to live', 'want to die', 'cant go on',
                'whats the point', 'give up', 'never wake up'
            ],
            'severe_distress': [
                'cant handle', 'too painful', 'make it stop',
                'no hope', 'trapped', 'worthless', 'hopeless',
                'everything is dark', 'no way out', 'cant take it'
            ]
        }
        
        self.crisis_regex = {
            category: re.compile(r'\b(' + '|'.join(map(re.escape, keywords)) + r')\b', 
                               re.IGNORECASE) 
            for category, keywords in self.crisis_patterns.items()
        }
    
    def detect_crisis(self, text: str) -> Tuple[bool, str, float]:
        """Detect potential crisis situations in user messages."""
        text_lower = text.lower()
        
        for category, pattern in self.crisis_regex.items():
            matches = pattern.findall(text_lower)
            if matches:
                confidence = min(len(matches) * 0.3, 0.9)
                return True, category, confidence
                
        return False, 'none', 0.0

class EmotionDetector:
    """Detects emotions from user messages."""
    def __init__(self):
        # Your existing emotion patterns...
        self.emotion_patterns = {
            'joy': ['happy', 'glad', 'excited', 'good', 'great', 'wonderful', 'fantastic', ':)', '😊', '😃'],
            'sadness': ['sad', 'unhappy', 'depressed', 'down', 'miserable', 'hurt', 'crying', ':(', '😢', '😭'],
            'anger': ['angry', 'mad', 'frustrated', 'annoyed', 'furious', 'hate', '>:(', '😠', '😡'],
            'anxiety': ['anxious', 'worried', 'nervous', 'scared', 'afraid', 'stressed', 'panic', '😰', '😨'],
            'overwhelmed': ['overwhelmed', 'exhausted', 'too much', 'cant handle', 'burnt out', '😫', '😩'],
            'lonely': ['lonely', 'alone', 'isolated', 'abandoned', 'forgotten', '💔'],
            'hopeful': ['hopeful', 'optimistic', 'looking forward', 'better', 'improving', '🌱'],
            'grateful': ['grateful', 'thankful', 'blessed', 'appreciated', 'lucky', '🙏'],
            'neutral': ['okay', 'fine', 'alright', 'normal']
        }
        
        self.emotion_regex = {
            emotion: re.compile(r'\b(' + '|'.join(map(re.escape, keywords)) + r')\b', 
                              re.IGNORECASE) 
            for emotion, keywords in self.emotion_patterns.items()
        }

    def detect_emotion(self, text):
        """Detect the dominant emotion in text."""
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
    """Enhanced chatbot with crisis detection and workshop integration."""
    def __init__(self, db):
        self.db = db
        self.emotion_detector = EmotionDetector()
        self.crisis_detector = CrisisDetector()
        self.redirect_manager = WorkshopRedirectManager()
        
        # Your existing coping exercises...
        self.coping_exercises = {
            'anxiety': [
                "Let's try a gentle breathing exercise together! 🌬️ Breathe in for 4 counts, hold for 4, and exhale for 4. Repeat this 3 times. 🍃",
                "Here's a quick grounding technique: Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste 🌟",
                "Imagine you're in your favorite peaceful place - maybe a beach or garden. What do you see and hear there? 🏖️",
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
                "When emotions feel intense, try this: Take a slow, deep breath and count to 5 with me 🌬️",
                "Here's a calming visualization: Picture your tension flowing away like water in a stream 🌊",
                "Would you like to try releasing some energy safely? Maybe squeezing a soft object or taking 10 big steps? 🍃",
                "Try this 'cool down' technique: Imagine you're a hot air balloon slowly releasing heated air and gently descending 🎈",
                "Let's do the 'strong tree' pose - stand tall, feel your feet grounded, and sway gently like branches in a breeze 🌳",
                "Here's a playful release: Draw your anger as weather (maybe a storm?) and watch it gradually change to sunshine ⛈️→☀️"
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
                "Let's do the 'sunshine stretch' - reach up high and imagine drawing positive energy from above ☀️",
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
        # Initialize Llama with updated prompt template
        try:
            self.llm = Ollama(model="llama3")
            self.memory = ConversationBufferMemory(
                input_key="user_input",
                memory_key="chat_history"
            )
            self.prompt = PromptTemplate(
                input_variables=["emotion", "confidence", "chat_history", "user_input", "coping_exercises"],
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

    def generate_response(self, user_message: str, user_id: int) -> Dict:
        """Generate response with crisis detection and workshop redirection."""
        try:
            # Detect emotion and crisis
            emotion, confidence = self.emotion_detector.detect_emotion(user_message)
            is_crisis, crisis_type, crisis_confidence = self.crisis_detector.detect_crisis(user_message)
            
            # Get workshop URL
            workshop_url = self.redirect_manager.get_workshops_url()
            
            # Attempt redirection for crisis situations
            should_redirect = is_crisis and crisis_confidence > 0.7
            if should_redirect:
                redirect_success = self.redirect_manager.redirect_to_workshops()
            else:
                redirect_success = False
            
            # Get chat history
            chat_history = self._get_chat_history(user_id)
            
            # Get relevant coping exercises
            exercises = self.coping_exercises.get(emotion, self.coping_exercises['neutral'])
            exercises_text = "\n".join(exercises)
            
            # Generate response using Llama
            response = self.conversation.predict(
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
            
            # Clean up response
            response = response.strip()
            
            # Save interaction
            self._save_interaction(
                user_id, 
                user_message, 
                response, 
                is_crisis,
                redirect_attempted=should_redirect,
                redirect_success=redirect_success
            )
            
            return {
                'message': {
                    'content': response,
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
                    'suggested_exercises': exercises[:2]
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_crisis_fallback_response(
                emotion if 'emotion' in locals() else 'neutral',
                'crisis' in locals() and is_crisis,
                self.redirect_manager.get_workshops_url() if hasattr(self, 'redirect_manager') else None
            )

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

    def _save_interaction(self, user_id, user_message, response, is_crisis=False, 
                         redirect_attempted=False, redirect_success=False):
        """Save chat interaction to database."""
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
            self.db.session.rollback()

    def _should_refer_to_counselor(self, emotion, confidence):
        """Determine if user should be referred to a counselor."""
        high_risk_emotions = ['sadness', 'anxiety']
        return emotion in high_risk_emotions and confidence > 0.7

    def _get_crisis_fallback_response(self, emotion: str, is_crisis: bool, workshop_url: Optional[str] = None):
        """Generate appropriate fallback response with crisis handling."""
        if is_crisis:
            content = (
                f"I sense you're going through a really difficult time 💗 "
                f"It's important that you know you're not alone, and help is available right now. "
                f"I've opened our workshops page where caring professionals are ready to support you. "
                f"Would you be willing to explore these resources together? 🤝 {workshop_url if workshop_url else ''} 🌟"
            )
        else:
            content = self._get_fallback_response(emotion)['message']['content']

        return {
            'message': {
                'content': content,
                'type': 'bot'
            },
            'metadata': {
                'emotion': emotion,
                'is_crisis': is_crisis,
                'timestamp': datetime.now().isoformat(),
                'workshop_url': workshop_url,
                'fallback': True
            }
        }