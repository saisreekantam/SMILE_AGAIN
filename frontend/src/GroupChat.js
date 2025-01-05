import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './GroupChats.css';

const GroupChatPage = () => {
  const [groups, setGroups] = useState([]);
  const navigate = useNavigate(); 

  // Fetch groups on mount
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await axios.get('/api/groups');
        setGroups(response.data);
      } catch (error) {
        console.error('Error fetching groups:', error);
      }
    };
    fetchGroups();
  }, []);

  const handleGroupClick = (group) => {
    // Navigate to the individual group page
    navigate(`/groups/${group.id}`);
  };

  return (
    <div className="group-chat-page">
      <div className="group-list">
        <h2>Your Groups</h2>
        {groups.map((group) => (
          <div
            key={group.id}
            className="group-item"
            onClick={() => handleGroupClick(group)}
          >
            {group.name}
          </div>
        ))}
      </div>
    </div>
  );
};

export default GroupChatPage;
