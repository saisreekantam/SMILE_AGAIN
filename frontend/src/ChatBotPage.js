// ChatBotPage.js
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import NavAfterLogin from './NavAfterLogin';
import { FaPaperPlane, FaSpinner } from 'react-icons/fa';
import './ChatBotPage.css';

// Configure axios defaults
// axios.defaults.withCredentials = true;
// axios.defaults.baseURL = 'http://localhost:8000';

const ChatBotPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const chatContainerRef = useRef(null);
  const inputRef = useRef(null);
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();

  // Redirect if not logged in
  // useEffect(() => {
  //   if (!isLoggedIn) {
  //     navigate('/login');
  //   }
  // }, [isLoggedIn, navigate]);

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

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);

    // Add user message immediately
    const userMessage = { sender: 'user', text: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await axios.post("http://localhost:8000/smilebot/chat", {
        message: input
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        withCredentials:true,
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      // Add bot response
      const botMessage = {
        sender: 'bot',
        text: response.data.message.content,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (err) {
      console.error('Error sending message:', err);
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

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
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
              className={`message ${message.sender}-message ${message.isError ? 'error-message' : ''}`}
            >
              <div className="message-content">
                {message.text}
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
            <button onClick={() => setError(null)}>✕</button>
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
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !input.trim()}
            className="send-button"
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