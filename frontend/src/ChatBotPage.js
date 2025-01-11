// ChatBotPage.js
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import NavAfterLogin from './NavAfterLogin';
import { FaPaperPlane, FaSpinner } from 'react-icons/fa';
import './ChatBotPage.css';
import BotSpeech from './Bot_Speech';
import SpeechInput from './Speech_Input';

// Configure axios defaults for all requests
axios.defaults.withCredentials = true;
axios.defaults.baseURL = 'http://localhost:8000';

/**
 * ChatBotPage Component
 * Provides an interface for users to interact with the AI chatbot
 * Features include real-time chat, message history, and stress detection
 */
const ChatBotPage = () => {
  // State management
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Refs for DOM manipulation
  const chatContainerRef = useRef(null);
  const inputRef = useRef(null);
  
  // Navigation and authentication
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();

  // Effect to redirect if not logged in
  // useEffect(() => {
  //   if (!isLoggedIn) {
  //     navigate('/login');
  //   }
  // }, [isLoggedIn, navigate]);

  // Effect to scroll to bottom when messages update
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // Effect to focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  /**
   * Formats timestamp for message display
   * @param {Date} timestamp - Message timestamp
   * @returns {string} Formatted time string
   */
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  /**
   * Handles sending messages to the chatbot
   * Includes error handling and loading states
   */
  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);

    // Add user message immediately for better UX
    const userMessage = { 
      sender: 'user', 
      text: input.trim(), 
      timestamp: new Date() 
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      // Send message to backend
      const response = await axios.post('/bot/chat', {
        message: userMessage.text
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      // Add bot response to chat
      const botMessage = {
        sender: 'bot',
        text: response.data.message.content,
        timestamp: new Date(),
        metadata: response.data.metadata // Include any additional metadata
      };
      setMessages(prev => [...prev, botMessage]);

      // Handle counselor referral if needed
      if (botMessage.metadata?.counselor_referral) {
        handleCounselorReferral();
      }

    } catch (err) {
      console.error('Error sending message:', err);
      
      // Handle different types of errors
      if (err.response?.status === 401) {
        navigate('/login');
        return;
      }

      setError('Failed to send message. Please try again.');
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handles keypress events for message input
   * @param {KeyboardEvent} e - Keyboard event
   */
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  /**
   * Handles counselor referral process
   * Triggered when stress levels are high
   */
  const handleCounselorReferral = () => {
    // Implementation for counselor referral
    setMessages(prev => [...prev, {
      sender: 'bot',
      text: 'I notice you might be feeling overwhelmed. Would you like to connect with a professional counselor?',
      timestamp: new Date(),
      isReferral: true
    }]);
  };

  return (
    <div className="chatbot-page">
      <NavAfterLogin />
      
      <div className="quote-container">
        <h1>Find Your Smile Again</h1>
        <p className="quote">
          "A smile doesn't always mean you're happy. Sometimes it just means you're strong."
        </p>
      </div>

      <div className="chat-section">
        <div className="chat-container" ref={chatContainerRef}>
          {/* Welcome message */}
          <div className="message bot-message">
            <div className="message-content">
              Hi! I'm here to listen and help. How are you feeling today?
            </div>
            <div className="message-timestamp">
              {formatTimestamp(new Date())}
            </div>
          </div>

          {/* Chat messages */}
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.sender}-message ${message.isError ? 'error-message' : ''} ${message.isReferral ? 'referral-message' : ''}`}
            >
              <div className="message-content">
                {message.text}
                {message.sender==='bot' && (
                  <BotSpeech message={message.text}/>
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
          <div className='input-buttons'>
            <SpeechInput onSpeechInput={(text) => setInput(text)}
            isDisabled={isLoading}
          />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !input.trim()}
            className="send-button"
            aria-label="Send message"
          >
            {isLoading ? <FaSpinner className="spinner" /> : <FaPaperPlane />}
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
  );
};

export default ChatBotPage;