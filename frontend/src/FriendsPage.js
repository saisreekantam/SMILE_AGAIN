import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './FriendsPage.css';

const ViewFriends = () => {
  const [friends, setFriends] = useState([]);

  useEffect(() => {
    const fetchFriends = async () => {
      try {
        const response = await axios.get('/api/friends');
        setFriends(response.data);
      } catch (error) {
        console.error('Error fetching friends:', error);
      }
    };

    fetchFriends();
  }, []);

  return (
    <div className="view-friends-page">
      <h2>Your Friends</h2>
      <div className="friend-list">
        {friends.map((friend) => (
          <div key={friend.id} className="friend-item">
            <h3>{friend.name}</h3>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ViewFriends;
