import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './GroupPage.css';

const GroupPage = () => {
  const { group_id } = useParams();
  const navigate = useNavigate();
  const [groupDetails, setGroupDetails] = useState(null);
  const [messages, setMessages] = useState([]);
  const [friends, setFriends] = useState([]);
  const [input, setInput] = useState('');
  const [friendPopUp, setFriendPopUp] = useState(false);
  const [selectedFriends, setSelectedFriends] = useState([]);

  useEffect(() => {
    const fetchGroupDetails = async () => {
      try {
        const response = await axios.get(`/api/groups/${group_id}`);
        setGroupDetails(response.data.group);
        setMessages(response.data.messages);
      } catch (error) {
        console.error('Error fetching group details:', error);
      }
    };

    const fetchFriendsDetails = async () => {
      try {
        const response = await axios.get('/api/friends');
        setFriends(response.data);
      } catch (error) {
        console.error('Error fetching friends:', error);
      }
    };

    fetchGroupDetails();
    fetchFriendsDetails();
  }, [group_id]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const newMessage = { sender: 'You', text: input };
    setMessages([...messages, newMessage]);
    setInput('');

    try {
      await axios.post(`/api/groups/${group_id}/messages`, { text: input });
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const handleLeaveGroup = async () => {
    try {
      await axios.post(`/api/groups/${group_id}/leave`);
      navigate('/groups');
    } catch (error) {
      console.error('Error leaving group:', error);
    }
  };

  const handleAddMembers = () => {
    setFriendPopUp(true);
  };

  const handleCheckboxChange = (friendId) => {
    if (selectedFriends.includes(friendId)) {
      setSelectedFriends(selectedFriends.filter((id) => id !== friendId));
    } else {
      setSelectedFriends([...selectedFriends, friendId]);
    }
  };

  const handleSubmitMembers = async () => {
    try {
      for (const friendId of selectedFriends) {
        await axios.post(`/api/groups/${group_id}/add-member`, { friend_id: friendId });
      }
      setFriendPopUp(false);
      setSelectedFriends([]);
    } catch (error) {
      console.error('Error adding members:', error);
    }
  };

  const handleClosePopup = () => {
    setFriendPopUp(false);
    setSelectedFriends([]);
  };

  if (!groupDetails) {
    return <div>Loading...</div>;
  }

  return (
    <div className="group-page">
      <div className="group-header">
        <h2>{groupDetails.name}</h2>
        <button onClick={handleAddMembers}>Add Members</button>
        <button onClick={handleLeaveGroup}>Leave Group</button>
      </div>
      <div className="group-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.sender === 'You' ? 'user' : 'bot'}`}
          >
            <strong>{message.sender}: </strong>
            {message.text}
          </div>
        ))}
      </div>
      <div className="group-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>

      {friendPopUp && (
        <>
            <div className="popup-overlay" onClick={() => setFriendPopUp(false)}></div>
                <div className="popup">
                <h3>Add Members</h3>
                <div>
                    {friends.map((friend) => (
                    <div key={friend.id}>
                        <input
                        type="checkbox"
                        id={`friend-${friend.id}`}
                        onChange={(e) => handleCheckboxChange(e, friend.id)}
                        />
                        <label htmlFor={`friend-${friend.id}`}>{friend.name}</label>
                    </div>
                    ))}
                </div>
                <button onClick={handleSubmitMembers}>Add Members</button>
                <button onClick={handleClosePopup}>Cancel</button>
                </div>
        </>
    )}

    </div>
  );
};

export default GroupPage;
