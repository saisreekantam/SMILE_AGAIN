import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Mic, MicOff, Loader2 } from 'lucide-react';

const SpeechInput = ({ onSpeechInput, isDisabled = false }) => {
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [error, setError] = useState(null);
  const recognitionRef = useRef(null);
  const stopTimeoutRef = useRef(null);

  const STOP_DELAY_MS = 5000; // Delay in milliseconds

  const initializeSpeechRecognition = useCallback(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setSpeechSupported(false);
      setError('Speech recognition is not supported in this browser.');
      return null;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true; // Keep the recognition running
    recognition.interimResults = false;
    recognition.lang = 'en-US';

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

      // Restart the stop timeout each time new speech is detected
      stopTimeoutRef.current = setTimeout(() => {
        recognition.stop();
      }, STOP_DELAY_MS);
    };

    recognition.onerror = (event) => {
      setError(event.error);
      setIsListening(false);
    };

    return recognition;
  }, [onSpeechInput]);

  useEffect(() => {
    setSpeechSupported(('webkitSpeechRecognition' in window) || ('SpeechRecognition' in window));
  }, []);

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

  if (!speechSupported) {
    return null;
  }

  return (
    <div className="relative inline-block">
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
        // title={isListening ? 'Stop listening' : 'Start voice input'}
      >
        {isListening ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="sr-only">Listening...</span>
          </>
        ) : (
          <>
            {error ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
            <span className="sr-only">
              {/* {error ? 'Speech recognition error' : 'Start voice input'} */}
            </span>
          </>
        )}
      </button>
      
      {error && (
        <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-red-100 text-red-600 text-sm py-1 px-2 rounded whitespace-nowrap">
          {error}
        </div>
      )}
    </div>
  );
};

export default SpeechInput;
