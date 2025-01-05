import openai
import cv2
import numpy as np
from datetime import datetime
from typing import Optional, Dict, List
from deepface import DeepFace  
import base64
import io
from PIL import Image

class EmotionDetector:
    def __init__(self):
        self.emotion_mapping = {
            'happy': 'joy',
            'sad': 'sadness',
            'neutral': 'neutral',
            'fear': 'anxiety',
            'angry': 'stress',
            'surprise': 'hope',
            'disgust': 'stress'
        }

    def detect_from_text(self, text: str) -> Dict:
        """Detect emotion from text"""
        emotional_indicators = {
            'joy': ['happy', 'joy', 'excited', 'smile', 'great', 'wonderful'],
            'sadness': ['sad', 'down', 'unhappy', 'depressed', 'miserable'],
            'anxiety': ['worried', 'anxious', 'nervous', 'afraid', 'scared'],
            'stress': ['stressed', 'overwhelmed', 'pressure', 'tired'],
            'hope': ['hope', 'better', 'improve', 'optimistic', 'forward'],
            'neutral': ['okay', 'fine', 'normal', 'alright']
        }

        text_lower = text.lower()
        emotion_scores = {emotion: 0 for emotion in emotional_indicators}

        for emotion, indicators in emotional_indicators.items():
            emotion_scores[emotion] = sum(word in text_lower for word in indicators)

        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        if all(score == 0 for score in emotion_scores.values()):
            dominant_emotion = 'neutral'

        return {
            'emotion': dominant_emotion,
            'confidence': emotion_scores[dominant_emotion] / (sum(emotion_scores.values()) or 1)
        }

    def detect_from_image(self, image_data: str) -> Dict:
        """Detect emotion from base64 encoded image"""
        try:
            # Remove data:image/jpeg;base64 prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]

            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image_array = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            # Analyze using DeepFace
            analysis = DeepFace.analyze(frame, 
                                      actions=['emotion'],
                                      enforce_detection=False)

            dominant_emotion = analysis[0]['dominant_emotion']
            confidence = analysis[0]['emotion'][dominant_emotion] / 100

            return {
                'emotion': self.emotion_mapping.get(dominant_emotion, 'neutral'),
                'confidence': confidence
            }
        except Exception as e:
            print(f"Error in facial emotion detection: {str(e)}")
            return {
                'emotion': 'neutral',
                'confidence': 0.0
            }

class SmileBot:
    def __init__(self):
        self.emotion_detector = EmotionDetector()
        openai.api_key = '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'

    async def generate_response(self, text: str, image_data: Optional[str], chat_history: List[Dict]) -> Dict:
        """Generate response based on text and facial emotions"""
        try:
            # Get emotions from both sources
            text_emotion = self.emotion_detector.detect_from_text(text)
            facial_emotion = self.emotion_detector.detect_from_image(image_data) if image_data else None

            # Combine emotional analysis
            combined_emotion = self._combine_emotions(text_emotion, facial_emotion)

            # Build conversation context
            messages = [
                {"role": "system", "content": self._get_system_prompt(combined_emotion)}
            ]

            # Add chat history
            for msg in chat_history[-5:]:  # Last 5 messages
                messages.append({
                    "role": "user" if msg['sender_type'] == "user" else "assistant",
                    "content": msg['content']
                })

            # Add current message with emotional context
            messages.append({
                "role": "user",
                "content": f"{text} [Emotional State: {combined_emotion['emotion']}]"
            })

            # Generate response
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )

            return {
                'message': {
                    'content': response.choices[0].message.content,
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'bot'
                },
                'metadata': {
                    'text_emotion': text_emotion,
                    'facial_emotion': facial_emotion,
                    'combined_emotion': combined_emotion
                }
            }

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                'message': {
                    'content': "I'm having a moment. Could you try that again?",
                    'type': 'bot'
                }
            }

    def _combine_emotions(self, text_emotion: Dict, facial_emotion: Optional[Dict]) -> Dict:
        """Combine text and facial emotions to get overall emotional state"""
        if not facial_emotion:
            return text_emotion

        # Prioritize facial emotion if confidence is high
        if facial_emotion['confidence'] > 0.7:
            return facial_emotion
        # Prioritize text emotion if facial confidence is low
        elif text_emotion['confidence'] > facial_emotion['confidence']:
            return text_emotion
        # Default to facial emotion
        return facial_emotion

    def _get_system_prompt(self, emotion: Dict) -> str:
        """Get appropriate system prompt based on emotional state"""
        base_prompt = """You are Joy, an empathetic and supportive AI companion for the Smile Again platform. 
        Your goal is to help users rediscover their smile through validation, understanding, and gentle encouragement."""

        emotion_prompts = {
            'joy': " The user seems happy, maintain and build upon this positive state.",
            'sadness': " The user seems sad, offer gentle comfort and understanding.",
            'anxiety': " The user seems anxious, provide calm reassurance and grounding.",
            'stress': " The user seems stressed, help them find moments of peace.",
            'hope': " The user shows hope, encourage and reinforce this optimism.",
            'neutral': " Engage with warmth while being attentive to emotional cues."
        }

        return base_prompt + emotion_prompts.get(emotion['emotion'], "")
