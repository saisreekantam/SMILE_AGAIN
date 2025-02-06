import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import NavAfterLogin from './NavAfterLogin';
import { FaPaperPlane, FaSpinner } from 'react-icons/fa';
import { Globe } from 'lucide-react';
import './ChatBotPage.css';
import BotSpeech from './Bot_Speech';
import SpeechInput from './Speech_Input';

// Supported languages configuration
const SUPPORTED_LANGUAGES = {
  en: { name: 'English', code: 'en-US' },
  hi: { name: 'हिंदी', code: 'hi-IN' },
  te: { name: 'తెలుగు', code: 'te-IN' },
  ta: { name: 'தமிழ்', code: 'ta-IN' },
  ml: { name: 'മലയാളം', code: 'ml-IN' },
  kn: { name: 'ಕನ್ನಡ', code: 'kn-IN' },
  bn: { name: 'বাংলা', code: 'bn-IN' },
  gu: { name: 'ગુજરાતી', code: 'gu-IN' },
  mr: { name: 'मराठी', code: 'mr-IN' }
};

// Configure axios defaults
axios.defaults.withCredentials = true;
axios.defaults.baseURL = 'http://localhost:8000';

const ChatBotPage = () => {
  // State management
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);

  // Refs
  const chatContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Auth and navigation
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();

  // Scroll to bottom when messages update
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleLanguageChange = (langCode) => {
    setSelectedLanguage(langCode);
    setShowLanguageMenu(false);
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);

    // Add user message immediately
    const userMessage = {
      sender: 'user',
      text: input.trim(),
      timestamp: new Date(),
      language: selectedLanguage
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await axios.post('/bot/chat', {
        message: input,
        language: selectedLanguage
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      // Add bot response
      const botMessage = {
        sender: 'bot',
        text: response.data.message.content,
        timestamp: new Date(),
        metadata: response.data.metadata,
        language: selectedLanguage
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (err) {
      console.error('Error sending message:', err);
      
      if (err.response?.status === 401) {
        navigate('/login');
        return;
      }

      setError('Failed to send message. Please try again.');
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        isError: true,
        language: selectedLanguage
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div>
      <div className="chatbot-page">
        <NavAfterLogin />

        <div className="chat-section">
          {/* Language Selector */}
          <div className="language-selector flex justify-end p-4">
            <div className="relative">
              <button
                onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                className="p-2 rounded-full hover:bg-gray-100 transition-colors text-gray-600"
                title="Select language"
              >
                <Globe className="w-6 h-6" />
              </button>
              
              {showLanguageMenu && (
                <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50">
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
                        style={{width:'350px',height:'50px',color:'white'}}
                      >
                        {name}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Chat Container */}
          <div className="chat-container" ref={chatContainerRef}>
            {/* Welcome message */}
            <div className="message bot-message-main">
              <div className="message-content">
                Hi! I'm here to listen and help. How are you feeling today?
                <BotSpeech message="Hi! I'm here to listen and help. How are you feeling today?" language={selectedLanguage} />
              </div>
              <div className="message-timestamp">
                {formatTimestamp(new Date())}
              </div>
            </div>

            {/* Chat messages */}
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message-m ${message.sender}-message-main ${message.isError ? 'error-message' : ''}`}
              >
                <div className="message-content">
                  {message.text}
                  {message.sender === 'bot' && (
                    <BotSpeech message={message.text} language={message.language} />
                  )}
                </div>
                <div className="message-timestamp">
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="message bot-message loading">
                <div className="message-content">
                  <FaSpinner className="spinner" />
                  <span>Joy is typing...</span>
                </div>
              </div>
            )}
          </div>

          {/* Error display */}
          {error && (
            <div className="error-banner">
              {error}
              <button onClick={() => setError(null)} className="error-close">✕</button>
            </div>
          )}

          {/* Input area */}
          <div className="chat-input-container">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here..."
              disabled={isLoading}
              rows="1"
              className="chat-input"
            />
            <div className="input-buttons" style={{zIndex:'100'}}>
              <SpeechInput 
                onSpeechInput={(text) => setInput(text)}
                isDisabled={isLoading}
                language={selectedLanguage}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !input.trim()}
              className="send-button"
              aria-label="Send message"
              style={{width:'100px',backgroundColor:'#4444cc'}}
            >
              {isLoading ? <FaSpinner className="spinner" /> : "Send"}
            </button>
          </div>
        </div>

        <div className="support-message">
          <h3>Need More Support?</h3>
          <p>
            If you're feeling overwhelmed, our professional counselors are here to help.
            Click here to connect with a mental health professional.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatBotPage;
