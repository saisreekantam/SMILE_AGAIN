import React, { useState, useEffect } from 'react';
import { Volume2, VolumeX, Globe } from 'lucide-react';

const VOICE_PREFERENCES = {
  en: {
    preferred: ['Microsoft Zira', 'Microsoft Ravi', 'hi-IN', 'en-IN','te-IN'],
    fallback: 'en-US'
  },
  hi: { preferred: ['hi-IN'], fallback: 'hi' },
  te: { preferred: ['te-IN'], fallback: 'te' },
  ta: { preferred: ['ta-IN'], fallback: 'ta' },
  ml: { preferred: ['ml-IN'], fallback: 'ml' },
  kn: { preferred: ['kn-IN'], fallback: 'kn' },
  bn: { preferred: ['bn-IN'], fallback: 'bn' },
  gu: { preferred: ['gu-IN'], fallback: 'gu' },
  mr: { preferred: ['mr-IN'], fallback: 'mr' }
};

const BotSpeech = ({ message, language = 'en' }) => {
  const [speaking, setSpeaking] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [voices, setVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);

  const removeEmojis = (text) => {
    return text
      .replace(
        /[\u{1F300}-\u{1F9FF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F900}-\u{1F9FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{1F200}-\u{1F2FF}]|[\u{1F700}-\u{1F77F}]|[\u{1F780}-\u{1F7FF}]|[\u{1F800}-\u{1F8FF}]|[\u{1F900}-\u{1F9FF}]|[\u{1FA00}-\u{1FA6F}]|[\u{1FA70}-\u{1FAFF}]/gu,
        ''
      )
      .replace(/\s+/g, ' ')
      .trim();
  };

  const findPreferredVoice = (availableVoices, languageCode) => {
    const prefs = VOICE_PREFERENCES[languageCode];
    if (!prefs) return null;

    // Try to find a voice matching preferred options
    for (const pref of prefs.preferred) {
      // First, try to find an exact match for Indian English or Indian accent
      const exactMatch = availableVoices.find(voice => 
        voice.lang.toLowerCase().includes(pref.toLowerCase()) ||
        voice.name.toLowerCase().includes(pref.toLowerCase())
      );
      if (exactMatch) return exactMatch;
    }

    // If no preferred voice found, try fallback
    const fallbackVoice = availableVoices.find(voice => 
      voice.lang.toLowerCase().startsWith(prefs.fallback.toLowerCase())
    );

    return fallbackVoice || availableVoices[0];
  };

  useEffect(() => {
    if ('speechSynthesis' in window) {
      setSpeechSupported(true);

      const loadVoices = () => {
        const availableVoices = window.speechSynthesis.getVoices();
        setVoices(availableVoices);
        
        // Set preferred voice based on language
        const voice = findPreferredVoice(availableVoices, language);
        setSelectedVoice(voice);
      };

      window.speechSynthesis.onvoiceschanged = loadVoices;
      loadVoices();
    }
  }, [language]);

  const speak = (text) => {
    try {
      if (!speechSupported) return;

      window.speechSynthesis.cancel();
      const cleanedText = removeEmojis(text);
      const utterance = new SpeechSynthesisUtterance(cleanedText);

      // Adjust voice properties for Indian accent when speaking English
      if (language === 'en' && selectedVoice) {
        utterance.voice = selectedVoice;
        utterance.rate = 0.9; // Slightly slower for clearer pronunciation
        utterance.pitch = 1.1; // Slightly higher pitch for Indian accent
      } else if (selectedVoice) {
        utterance.voice = selectedVoice;
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
      }

      utterance.volume = 1.0;

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