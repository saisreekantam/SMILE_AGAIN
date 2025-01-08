import React, { useEffect, useState } from 'react';
import './NotificationsPage.css';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const FriendRequestsPage = () => {
  const [friendRequestCount, setFriendRequestCount] = useState(0);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate=useNavigate();

  // Fetch friend request count and pending requests
  useEffect(() => {
    const fetchFriendRequestData = async () => {
      try {
        // Fetch the count of pending friend requests
        

        // Fetch pending friend requests
        const requestsResponse = await axios.get('http://localhost:8000/profile/pending-friend-requests', {
          withCredentials: true,
        });
        console.log(requestsResponse.data);
        setPendingRequests(requestsResponse.data);
      } catch (err) {
        console.error('Error fetching friend requests:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchFriendRequestData();
  }, []);

  // Handle friend request response (accept or reject)
  const handleRequestResponse = async (id, action) => {
    try {
      await axios.post(
        `http://localhost:8000/profile/respond-friend-request/${id}`,
        { action },
        { withCredentials: true }
      );

      // Update the UI after response
      setPendingRequests((prev) =>
        prev.filter((request) => request.id !== id)
      );
      setFriendRequestCount((prevCount) => prevCount - 1);
    } catch (err) {
      console.error('Error responding to friend request:', err);
    }
  };

  if (loading) {
    return <div className="loading">Loading friend requests...</div>;
  }

  return (
    <div className="friend-requests-page">
      <h1>Friend Requests</h1>

      <div className="friend-requests-count">
        <p>You have <strong>{friendRequestCount}</strong> pending friend requests.</p>
      </div>

      <div className="friend-requests-list">
        {pendingRequests.length === 0 ? (
          <p>No pending friend requests.</p>
        ) : (
          pendingRequests.map((request) => (
            <div key={request.id} className="friend-request-item">
              <p>
                <strong onClick={() => navigate(`/user/${request.user_id}`)} style={{cursor:'pointer'}}>{request.user_name}</strong> sent you a friend request.
              </p>
              <div className="request-actions">
                <button
                  className="accept-button"
                  onClick={() => handleRequestResponse(request.id, 'accept')}
                >
                  Accept
                </button>
                <button
                  className="reject-button"
                  onClick={() => handleRequestResponse(request.id, 'reject')}
                >
                  Reject
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default FriendRequestsPage;
