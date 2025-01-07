import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './AuthorProfilePage.css';

const UserProfileView = () => {
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/profile/profile/${userId}`, {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true
        });
        setProfile(response.data);
      } catch (err) {
        console.error('Error fetching profile:', err);
        setError(err.response?.data?.error || 'Error loading profile');
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchProfile();
    }
  }, [userId]);

  const handleSendFriendRequest = async () => {
    try {
      const response = await axios.post(
        `http://localhost:8000/profile/send-friend-request/${userId}`,
        {},
        {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true
        }
      );
      setProfile(prev => ({
        ...prev,
        friendship_status: 'pending'
      }));
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to send friend request');
    }
  };

  if (loading) {
    return <div className="loading-spinner">Loading profile...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!profile) {
    return <div className="not-found-message">Profile not found</div>;
  }

  return (
    <div className="container">
      <div className="profile-card">
        <div className="profile-header">
          <h2 className="profile-title">{profile.name}'s Profile</h2>
        </div>
        <div className="profile-content">
          <div className="profile-sections">
            <div className="profile-image-container">
              <img 
                src={profile.profile_pic} 
                alt={`${profile.name}'s profile`} 
                className="profile-image"
              />
            </div>

            <div className="info-section">
              <h3 className="section-title">About</h3>
              <p>{profile.description || 'No description provided'}</p>
            </div>

            <div className="info-section">
              <h3 className="section-title">Smile Journey</h3>
              <p><strong>Last Smiled:</strong> {profile.smile_last_time || 'Not shared'}</p>
              <p><strong>Reason:</strong> {profile.smile_reason || 'Not shared'}</p>
            </div>

            {profile.recent_blogs?.length > 0 && (
              <div className="info-section">
                <h3 className="section-title">Recent Blogs</h3>
                <ul className="blog-list">
                  {profile.recent_blogs.map(blog => (
                    <li 
                      key={blog.id} 
                      className="blog-item"
                      onClick={() => navigate(`/blogs/${blog.id}`)}
                    >
                      {blog.title}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="friend-request-section">
              {profile.friendship_status === 'none' && (
                <button
                  onClick={handleSendFriendRequest}
                  className="friend-request-button"
                >
                  Send Friend Request
                </button>
              )}
              {profile.friendship_status === 'pending' && (
                <div className="friend-status status-pending">
                  Friend Request Pending
                </div>
              )}
              {profile.friendship_status === 'accepted' && (
                <div className="friend-status status-accepted">
                  Already Friends
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfileView;