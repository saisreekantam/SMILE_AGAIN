import React, { useState, useEffect } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

const BotSpeech = ({ message }) => {
  const [speaking, setSpeaking] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [voices, setVoices] = useState([]);

  const emojiVoiceMapping = {
    happy: ["😊", "😁", "😃", "😄"],
    sad: ["😢", "😞", "😔"],
    angry: ["😡", "😠"],
    surprised: ["😲", "😮", "😯"],
  };

  const removeEmojis = (text) => {
    return text
      .replace(
        /[\u{1F300}-\u{1F9FF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F900}-\u{1F9FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{1F200}-\u{1F2FF}]|[\u{1F700}-\u{1F77F}]|[\u{1F780}-\u{1F7FF}]|[\u{1F800}-\u{1F8FF}]|[\u{1F900}-\u{1F9FF}]|[\u{1FA00}-\u{1FA6F}]|[\u{1FA70}-\u{1FAFF}]/gu,
        ''
      )
      .replace(/\s+/g, ' ')
      .trim();
  };

  const getVoiceByEmoji = (text) => {
    for (const [emotion, emojis] of Object.entries(emojiVoiceMapping)) {
      for (const emoji of emojis) {
        if (text.includes(emoji)) {
          switch (emotion) {
            case 'happy':
              return voices.find((voice) => voice.name.toLowerCase().includes('female'));
            case 'sad':
              return voices.find((voice) => voice.name.toLowerCase().includes('male'));
            case 'angry':
              return voices.find((voice) => voice.name.toLowerCase().includes('robot'));
            case 'surprised':
              return voices.find((voice) => voice.name.toLowerCase().includes('child'));
            default:
              return voices[0]; // Default voice
          }
        }
      }
    }
    return voices[0]; // Default voice if no emoji is matched
  };

  useEffect(() => {
    if ('speechSynthesis' in window) {
      setSpeechSupported(true);

      const loadVoices = () => {
        const availableVoices = window.speechSynthesis.getVoices();
        setVoices(availableVoices);
      };

      window.speechSynthesis.onvoiceschanged = loadVoices;
      loadVoices();
    }
  }, []);

  useEffect(() => {
    if (message && speechSupported) {
      speak(message);
    }
  }, [message]);

  const speak = (text) => {
    try {
      if (!speechSupported) return;

      window.speechSynthesis.cancel();

      // Remove emojis from text before speaking
      const cleanedText = removeEmojis(text);
      const utterance = new SpeechSynthesisUtterance(cleanedText);

      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      const selectedVoice = getVoiceByEmoji(text);
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }

      utterance.onstart = () => setSpeaking(true);
      utterance.onend = () => setSpeaking(false);
      utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
        setSpeaking(false);
      };

      window.speechSynthesis.speak(utterance);
    } catch (error) {
      console.error('Speech synthesis failed:', error);
      setSpeaking(false);
    }
  };

  const stopSpeaking = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
    }
  };

  useEffect(() => {
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  if (!speechSupported) return null;

  return (
    <button
      onClick={() => (speaking ? stopSpeaking() : speak(message))}
      className={`p-2 rounded-full hover:bg-gray-100 transition-colors ${
        speaking ? 'text-purple-600' : 'text-gray-600'
      }`}
      title={speaking ? 'Stop speaking' : 'Speak message'}
    >
      {speaking ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
    </button>
  );
};

export default BotSpeech;
