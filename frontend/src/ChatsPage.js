import React, { useState } from 'react';
import './ChatsPage.css';
import Chats from './ActiveChats';
import ChatRequests from './ChatRequests';
import GroupChatPage from './GroupChat';
import NavAfterLogin from './NavAfterLogin';
import { useAuth } from './contexts/AuthContext';
import CommunityPage from './CommunitiesPage';
import FriendRequestsPage from './NotificationsPage';
import ViewFriends from './FriendsPage';

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
        Community
        </button>
      </nav>

      <div className="content">
        {activeSection === 'active' && <ViewFriends />}
        {activeSection === 'requests' && <FriendRequestsPage />}
        {activeSection === 'groups' && <CommunityPage />}
      </div>
    </div>
  );
};

export default ChatsPage;
