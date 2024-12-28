import React, { useState } from 'react';
import './ChatsPage.css';
import ActiveChats from './ActiveChats';
import ChatRequests from './ChatRequests';
import GroupChats from './GroupChat';
import NavAfterLogin from './NavAfterLogin';

const ChatsPage = () => {
  const [activeSection, setActiveSection] = useState('active');

  return (
    <div className="chats-page">
      <NavAfterLogin />
      <nav className="navigation">
        <button
          className={`nav-button ${activeSection === 'active' ? 'active' : ''}`}
          onClick={() => setActiveSection('active')}
          
        >
          Active
        </button>
        <button
          className={`nav-button ${activeSection === 'requests' ? 'active' : ''}`}
          onClick={() => setActiveSection('requests')}
        >
          Chat Requests
        </button>
        <button
          className={`nav-button ${activeSection === 'unread' ? 'active' : ''}`}
          onClick={() => setActiveSection('unread')}
        >
          Unread
        </button>
      </nav>

      <div className="content">
        {activeSection === 'active' && <ActiveChats />}
        {activeSection === 'requests' && <ChatRequests />}
        {activeSection === 'unread' && <GroupChats />}
      </div>
    </div>
  );
};

export default ChatsPage;
