import React, { useEffect, useState } from 'react';
import './ActiveChasts.css';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Chats = () => {
  const [Chats, setChats] = useState([]);
  const [activeUsers, setActiveUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate=useNavigate();

  useEffect(() => {
    const fetchChatsAndActiveUsers = async () => {
      try {
        // Fetch all chats
        const chatsResponse = await axios.get('http://localhost:8000/chats/messages', {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        });
        setChats(chatsResponse.data || []);

        // Fetch active users
        const activeUsersResponse = await axios.get('http://localhost:8000/chats/active', {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        });
        setActiveUsers(activeUsersResponse.data.map((user) => user.id));
      } catch (err) {
        console.error('Error loading chats or active users:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchChatsAndActiveUsers();
  }, []);

  if (loading) {
    return <div className="loading">Loading active chats...</div>;
  }

  return (
    <div className="container">
      <h2 className="header">Chats</h2>
      {Chats.length === 0 ? (
        <div className="no-chats">No chats available.</div>
      ) : (
        <ul className="list">
          {Chats.map((chat) => (
            <li
              key={chat.id}
              className={`list-item ${activeUsers.includes(chat.id) ? 'active' : ''}`}
              onClick={() => navigate(`/friends/${chat.id}`)}
              style={{cursor:'pointer'}}
            >
              <span className="user-name">{chat.sender}</span>
              {activeUsers.includes(chat.id) && <span className="active-indicator">●</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Chats;
