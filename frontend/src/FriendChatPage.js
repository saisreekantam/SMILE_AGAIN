import React, { useEffect, useState } from "react";
import axios from "axios";
import './FriendChatPage.css'
import { useParams } from "react-router-dom";

const FriendChatPage = () => {
  const { friendId } = useParams();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [unreadCounts, setUnreadCounts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch chat history when component mounts
    const fetchChatHistory = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/chats/friends/chat/${friendId}`);
        setMessages(response.data || []);
      } catch (error) {
        console.error("Error fetching chat history", error);
      } finally {
        setLoading(false);
      }
    };

    // Fetch unread message counts
    const fetchUnreadCounts = async () => {
      try {
        const response = await axios.get("http://localhost:8000/chats/friends/unread");
        setUnreadCounts(response.data || []);
      } catch (error) {
        console.error("Error fetching unread counts", error);
      }
    };

    fetchChatHistory();
    fetchUnreadCounts();

    // Poll for unread message counts every 10 seconds
    const intervalId = setInterval(fetchUnreadCounts, 10000);
    return () => clearInterval(intervalId);
  }, [friendId]);

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;
    try {
      await axios.post(`http://localhost:8000/chats/friends/send/${friendId}`, { message: newMessage });
      setMessages([...messages, { content: newMessage, sender_name: "You", timestamp: new Date() }]);
      setNewMessage("");
    } catch (error) {
      console.error("Error sending message", error);
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-header">
        <h2>Chat with {friendId}</h2>
        <span className="unread-count">
          {unreadCounts.find(count => count.friend_id === friendId)?.unread_count || 0} Unread Messages
        </span>
      </div>

      <div className="message-container">
        {loading ? (
          <div>Loading...</div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className="message">
              <div className="sender">{msg.sender_name}</div>
              <div className="content">{msg.content}</div>
              <div className="timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</div>
            </div>
          ))
        )}
      </div>

      <div className="message-input">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type a message..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
};

export default FriendChatPage;
