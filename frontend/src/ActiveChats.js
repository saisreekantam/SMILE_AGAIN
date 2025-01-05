import React, { useEffect, useState } from 'react';
import './ActiveChasts.css';
import axios from 'axios'

const ActiveChats = () => {
  const [activeChats, setActiveChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchActiveChats = async () => {
      try {
        const response = await axios.get('http://localhost:8000/chats/active',{headers: { 'Content-Type' : 'application/json'}});
        setActiveChats(response.data);

      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchActiveChats();
  }, []);

  if (loading) {
    return <div className="loading">Loading active chats...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="container">
      <h2 className="header">Active Chats</h2>
      {activeChats.length === 0 ? (
        <div className="no-chats">No active chats available.</div>
      ) : (
        <ul className="list">
          {activeChats.map((chat) => (
            <li key={chat.id} className="list-item">
              <span className="user-name">{chat.name}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ActiveChats;
