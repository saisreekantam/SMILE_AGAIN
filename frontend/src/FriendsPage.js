import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './FriendsPage.css';

const ViewFriends = () => {
  const [friends, setFriends] = useState([]);

  useEffect(() => {
    const fetchFriends = async () => {
      try {
        const response = await axios.get('/api/friends'); // Replace with your API endpoint
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
        {friends.length === 0 ? (
          <p>No friends found!</p>
        ) : (
          friends.map((friend) => (
            <Link
              to={`/messages/${friend.id}`} // Route to the messages page
              key={friend.id}
              className="friend-item"
            >
              <h3>{friend.name}</h3>
            </Link>
          ))
        )}
      </div>
    </div>
  );
};

export default ViewFriends;
