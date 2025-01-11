# activity_bot/utils.py
import random
from typing import Dict, List, Optional
from datetime import datetime
import logging
from models import Message, Activity, UserActivity

logger = logging.getLogger(__name__)

class ActivityGenerator:
    """Generates engaging community activities"""
    
    def __init__(self):
        self.activity_categories = {
            'community_building': [
                {
                    'title': 'Story Circle ⭐',
                    'description': 'Each participant shares a 2-minute story about their happiest memory. Let\'s create a chain of joy!',
                    'duration': '30 minutes',
                    'participants': '5-15',
                    'energy_level': 'medium'
                },
                {
                    'title': 'Talent Showcase 🎭',
                    'description': 'Share your hidden talents! Whether it\'s singing, juggling, or making funny sounds - everyone has something unique!',
                    'duration': '45 minutes',
                    'participants': '10-20',
                    'energy_level': 'high'
                }
            ],
            'creative': [
                {
                    'title': 'Group Art Challenge 🎨',
                    'description': 'Create a collaborative digital artwork where each person adds one element. Theme: Our Happy Place!',
                    'duration': '40 minutes',
                    'participants': '4-12',
                    'energy_level': 'medium'
                },
                {
                    'title': 'Music Mashup 🎵',
                    'description': 'Create a community playlist where everyone adds their favorite upbeat song. Then have a virtual dance party!',
                    'duration': '30 minutes',
                    'participants': 'unlimited',
                    'energy_level': 'high'
                }
            ],
            'competitive': [
                {
                    'title': 'Trivia Championship 🏆',
                    'description': 'Fun-filled trivia contest with categories like Movies, Music, and Random Facts. Form teams and compete!',
                    'duration': '45 minutes',
                    'participants': '6-24',
                    'energy_level': 'high'
                },
                {
                    'title': 'Scavenger Hunt 🔍',
                    'description': 'Virtual scavenger hunt! Find items in your home that match specific categories. First to complete wins!',
                    'duration': '30 minutes',
                    'participants': '4-20',
                    'energy_level': 'high'
                }
            ],
            'wellness': [
                {
                    'title': 'Group Meditation 🧘‍♂️',
                    'description': 'Guided group meditation session followed by sharing positive intentions for the week.',
                    'duration': '20 minutes',
                    'participants': 'unlimited',
                    'energy_level': 'low'
                },
                {
                    'title': 'Dance Break 💃',
                    'description': 'Quick 15-minute dance session to favorite upbeat songs. No skills required - just move and have fun!',
                    'duration': '15 minutes',
                    'participants': 'unlimited',
                    'energy_level': 'high'
                }
            ]
        }

        self.encouragement_messages = [
            "Ready to make this day amazing? Let's jump into some fun activities! 🌟",
            "Time to create some wonderful memories together! 🎉",
            "Get ready for an awesome community experience! 💫",
            "Let's bring some excitement to our day! 🎈",
            "Who's ready to have some fun? These activities are perfect for our community! ⭐"
        ]

class ActivityBot:
    """Bot for suggesting and managing community activities"""
    
    def __init__(self, db):
        self.db = db
        self.activity_generator = ActivityGenerator()
        
    def generate_response(self, user_message: str, user_id: int) -> Dict:
        """Generate activity suggestions based on user input"""
        try:
            # Detect activity preferences from message
            categories = self._detect_preferred_categories(user_message)
            
            # Get relevant activities
            activities = self._get_activities(categories)
            
            # Create encouraging response
            response = self._create_activity_response(activities)
            
            # Save interaction
            self._save_interaction(user_id, user_message, response)
            
            return {
                'message': {
                    'content': response,
                    'type': 'activity_bot'
                },
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'suggested_activities': activities[:3],
                    'categories': categories
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating activity response: {str(e)}")
            return self._get_fallback_response()

    def _detect_preferred_categories(self, message: str) -> List[str]:
        """Detect activity categories based on user message"""
        message = message.lower()
        categories = []
        
        if any(word in message for word in ['team', 'group', 'together', 'social']):
            categories.append('community_building')
        if any(word in message for word in ['art', 'create', 'music', 'draw']):
            categories.append('creative')
        if any(word in message for word in ['compete', 'win', 'game', 'challenge']):
            categories.append('competitive')
        if any(word in message for word in ['relax', 'calm', 'wellness', 'health']):
            categories.append('wellness')
            
        # If no specific categories detected, return all
        return categories if categories else list(self.activity_generator.activity_categories.keys())

    def _get_activities(self, categories: List[str]) -> List[Dict]:
        """Get activities from specified categories"""
        activities = []
        for category in categories:
            category_activities = self.activity_generator.activity_categories.get(category, [])
            activities.extend(category_activities)
        
        # Shuffle and return top activities
        random.shuffle(activities)
        return activities[:5]

    def _create_activity_response(self, activities: List[Dict]) -> str:
        """Create an encouraging response with activity suggestions"""
        intro = random.choice(self.activity_generator.encouragement_messages)
        
        activity_text = "\n\n".join([
            f"🌟 {activity['title']}\n"
            f"└ {activity['description']}\n"
            f"└ Duration: {activity['duration']} | Participants: {activity['participants']}"
            for activity in activities[:3]
        ])
        
        outro = "\n\nReady to get started? Just pick an activity and let's make it happen! 🎉"
        
        return f"{intro}\n\n{activity_text}{outro}"

    def _save_interaction(self, user_id: int, user_message: str, response: str):
        """Save bot interaction to database"""
        try:
            message = Message(
                sender_id=user_id,
                content=user_message,
                timestamp=datetime.utcnow(),
                message_type='activity_request'
            )
            self.db.session.add(message)
            
            bot_response = Message(
                receiver_id=user_id,
                content=response,
                timestamp=datetime.utcnow(),
                message_type='activity_suggestion'
            )
            self.db.session.add(bot_response)
            
            self.db.session.commit()
            
        except Exception as e:
            logger.error(f"Error saving activity bot interaction: {str(e)}")
            self.db.session.rollback()

    def _get_fallback_response(self) -> Dict:
        """Generate fallback response if error occurs"""
        return {
            'message': {
                'content': (
                    "Let's get the fun started! I have some amazing community activities ready. "
                    "Would you like to try something creative, competitive, or community-building? 🌟"
                ),
                'type': 'activity_bot'
            },
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'is_fallback': True
            }
        }