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
  
  const handleAddGroup = (e) => {
    e.preventDefault();
    console.log("add group button clicked"); 
}
  return (
    <div className="group-chat-page">
      <div className="group-list">
      {groups.length > 0 ? (
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
      ) : (
        <div className="no-groups">
          <h2>No groups available</h2>
        </div>
      )}
      <button className="add-group-btn" onClick={handleAddGroup}>
        Add Group
      </button>
    </div>
    </div>
  );
};

export default GroupChatPage;
