import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Mic, MicOff, Loader2, Globe } from 'lucide-react';

const SUPPORTED_LANGUAGES = {
  en: { name: 'English', code: 'en-US' },
  hi: { name: 'हिंदी', code: 'hi-IN' },
  te: { name: 'తెలుగు', code: 'te-IN' },
  ta: { name: 'தமிழ்', code: 'ta-IN' },
  ml: { name: 'മലയാളം', code: 'ml-IN' },
  kn: { name: 'ಕನ್ನಡ', code: 'kn-IN' },
  bn: { name: 'বাংলা', code: 'bn-IN' },
  gu: { name: 'ગુજરાતી', code: 'gu-IN' },
  mr: { name: 'मराठी', code: 'mr-IN' },
};

const SpeechInput = ({ onSpeechInput, isDisabled = false }) => {
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [error, setError] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const recognitionRef = useRef(null);
  const stopTimeoutRef = useRef(null);

  const STOP_DELAY_MS = 10000;

  const initializeSpeechRecognition = useCallback(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setSpeechSupported(false);
      setError('Speech recognition is not supported in this browser.');
      return null;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = SUPPORTED_LANGUAGES[selectedLanguage].code;

    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onresult = (event) => {
      if (stopTimeoutRef.current) {
        clearTimeout(stopTimeoutRef.current);
      }

      const transcript = event.results[event.results.length - 1][0].transcript;
      onSpeechInput(transcript);

      stopTimeoutRef.current = setTimeout(() => {
        recognition.stop();
      }, STOP_DELAY_MS);
    };

    recognition.onerror = (event) => {
      setError(event.error);
      setIsListening(false);
    };

    return recognition;
  }, [onSpeechInput, selectedLanguage]);

  useEffect(() => {
    setSpeechSupported(('webkitSpeechRecognition' in window) || ('SpeechRecognition' in window));
  }, []);

  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = SUPPORTED_LANGUAGES[selectedLanguage].code;
    }
  }, [selectedLanguage]);

  const toggleListening = useCallback(() => {
    if (isListening) {
      recognitionRef.current?.stop();
      clearTimeout(stopTimeoutRef.current);
    } else {
      try {
        if (!recognitionRef.current) {
          recognitionRef.current = initializeSpeechRecognition();
        }
        recognitionRef.current?.start();
      } catch (err) {
        setError('Error starting speech recognition');
        console.error('Speech recognition error:', err);
      }
    }
  }, [isListening, initializeSpeechRecognition]);

  const handleLanguageChange = (langCode) => {
    setSelectedLanguage(langCode);
    setShowLanguageMenu(false);
    if (isListening) {
      recognitionRef.current?.stop();
      clearTimeout(stopTimeoutRef.current);
    }
  };

  if (!speechSupported) return null;

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={toggleListening}
        disabled={isDisabled}
        className={`p-2 rounded-full transition-colors ${
          isDisabled
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
            : isListening
            ? 'bg-red-100 text-red-600 hover:bg-red-200'
            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        }`}
      >
        {isListening ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : (
          error ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />
        )}
      </button>

      <div className="relative">
        <button
          onClick={() => setShowLanguageMenu(!showLanguageMenu)}
          disabled={isDisabled || isListening}
          className={`p-2 rounded-full transition-colors ${
            isDisabled || isListening
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
          title="Select language"
        >
          <Globe className="w-5 h-5" />
        </button>

        {showLanguageMenu && (
          <div className="absolute z-10 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
            <div className="py-1" role="menu">
              {Object.entries(SUPPORTED_LANGUAGES).map(([code, { name }]) => (
                <button
                  key={code}
                  onClick={() => handleLanguageChange(code)}
                  className={`block w-full text-left px-4 py-2 text-sm ${
                    selectedLanguage === code
                      ? 'bg-purple-100 text-purple-900'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                  role="menuitem"
                >
                  {name}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-red-100 text-red-600 text-sm py-1 px-2 rounded whitespace-nowrap">
          {error}
        </div>
      )}
    </div>
  );
};

export default SpeechInput;