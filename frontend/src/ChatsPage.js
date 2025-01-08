import React, { useState } from 'react';
import './ChatsPage.css';
import Chats from './ActiveChats';
import ChatRequests from './ChatRequests';
import GroupChatPage from './GroupChat';
import NavAfterLogin from './NavAfterLogin';
import { useAuth } from './contexts/AuthContext';
import CommunityPage from './CommunitiesPage';

const ChatsPage = () => {
  const [activeSection, setActiveSection] = useState('active');
  // const { login,user } = useAuth();
  // login(user.username);

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
          className={`nav-button ${activeSection === 'groups' ? 'active' : ''}`}
          onClick={() => setActiveSection('groups')}
        >
        Communities
        </button>
      </nav>

      <div className="content">
        {activeSection === 'active' && <Chats />}
        {activeSection === 'requests' && <ChatRequests />}
        {activeSection === 'groups' && <CommunityPage />}
      </div>
    </div>
  );
};

export default ChatsPage;
