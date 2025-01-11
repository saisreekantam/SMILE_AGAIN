import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './FriendsPage.css';
import NavAfterLogin from './NavAfterLogin';
import FriendChatPage from './FriendChatPage'; // Import your chat component

const ViewFriends = () => {
  const [friends, setFriends] = useState([]);
  const [selectedFriend, setSelectedFriend] = useState(null); // To manage selected friend for chat

  useEffect(() => {
    const fetchFriends = async () => {
      try {
        const response = await axios.get('http://localhost:8000/users/friends');
        console.log(response.data);
        setFriends(response.data);
      } catch (error) {
        console.error('Error fetching friends:', error);
      }
    };

    fetchFriends();
  }, []);

  const handleSelectFriend = (friend) => {
    setSelectedFriend(friend);
  };

  return (
    <div className="view-friends-page">
      {/* <NavAfterLogin /> */}
      <div className="friends-chat-container">
        {/* Friends List */}
        <div className="friend-list">
          <h2>Your Friends</h2>
          {friends.length === 0 ? (
            <p>No friends found!</p>
          ) : (
            friends.map((friend) => (
              <div
                key={friend.id}
                className={`friend-item ${selectedFriend?.id === friend.id ? 'active' : ''}`}
                onClick={() => handleSelectFriend(friend)}
              >
                <h3>{friend.name}</h3>
              </div>
            ))
          )}
        </div>

        {/* Chat Component */}
        <div className="chat-section">
          {selectedFriend ? (
            <FriendChatPage friend={selectedFriend} />
          ) : (
            <p>Select a friend to start chatting</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ViewFriends;
