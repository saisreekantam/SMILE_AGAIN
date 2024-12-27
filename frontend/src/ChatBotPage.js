import React, { useState, useRef, useEffect } from 'react';
import './ChatBotPage.css';
import NavAfterLogin from './NavAfterLogin';
import { useAuth } from './contexts/AuthContext';
import { Navigate } from 'react-router-dom';

const ChatBotPage = () => {
  const [quote, setQuote] = useState(
    "Smile doesn't mean that someone's happy. Sometimes it just means that you are strong"
  );
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const chatContainerRef = useRef(null);
  const chatSectionRef = useRef(null);
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);
  // if(!isLoggedIn){
  //   return <Navigate to="/login" />
  // }

  const handleSendMessage = () => {
    if (!input.trim()) return;
    const newMessages = [...messages, { sender: 'user', text: input }];
    setMessages(newMessages);

    setTimeout(() => {
      const botResponse = `Bot response to "${input}"`;
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'bot', text: botResponse },
      ]);
    }, 1000);
    setInput('');
  };

  const scrollToChat = () => {
    if (chatSectionRef.current) {
      chatSectionRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="ChatBotPage">
      <NavAfterLogin />
      <div className="QuoteContainer">
        <p style={{fontSize:'80px'}}>{quote}</p>
        <button className="scroll-to-chat" onClick={scrollToChat}>
          Talk to our Chatbot
        </button>
      </div>
      <div className="chat-container" ref={chatSectionRef}>
        <h2>How Can I Help You?</h2>
        <div className="chat-messages" ref={chatContainerRef}>
          {messages.map((message, index) => (
            <div
              key={index}
              className={`chat-message ${message.sender === 'user' ? 'user' : 'bot'}`}
            >
              {message.text}
            </div>
          ))}
        </div>
        <div className="chat-input">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
          />
          <button onClick={handleSendMessage}>Send</button>
        </div>
      </div>
      <div className="ColorDonation">
        <div className="ColorDonationMessage">
          <h3>Life is just dark without happiness</h3>
          <p>
            We started this platform to find your smile back, and for every smile found,
            we are making a life colorful. Everybody loses their smile in the bad phase,
            but those who get them back are real winners.
          </p>
          <h3>
            <a href="#" style={{ color: 'white' }}>
              IF WE MADE YOUR LIFE COLORFUL ----
            </a>
          </h3>
        </div>
      </div>
    </div>
  );
};

export default ChatBotPage;
