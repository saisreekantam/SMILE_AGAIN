import React, { useEffect, useState } from 'react';
import axios from 'axios';
import NavAfterLogin from './NavAfterLogin';
import './CommunityPage.css';
import { FaHeart, FaComment, FaUser } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

const CommunityPage = () => {
  const [community, setCommunity] = useState(null);
  const [posts, setPosts] = useState([]);
  const [newPost, setNewPost] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [id,setId]  = useState(1);
  const navigate=useNavigate();

  useEffect(() => {
    fetchCommunity();
  }, []);

  useEffect(() => {
    if (community) {
      fetchPosts(currentPage);
    }
  }, [community, currentPage]);

  const fetchCommunity = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/community/communities', {
        withCredentials: true
      });
    //   console.log(response.data);
      setCommunity(response.data);
      setId(response.data.id);
      console.log("Community :",response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load community');
    } finally {
      setLoading(false);
    }
  };

  const fetchPosts = async (page) => {
    if (!community) return;
    
    try {
      setLoading(true);
      const response = await axios.get(
        `http://localhost:8000/community/communities/${community.id}/posts?page=${page}`,
        { withCredentials: true }
      );
      console.log(response.data);
      setPosts(response.data.posts);
      setTotalPages(response.data.total_pages);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load posts');
    } finally {
      setLoading(false);
    }
  };

  const handlePostSubmit = async (e) => {
    e.preventDefault();
    if (!newPost.trim() || !community) return;

    try {
      setLoading(true);
      await axios.post(
        `http://localhost:8000/community/communities/${community.id}/posts`,
        { content: newPost },
        { withCredentials: true }
      );
      setNewPost('');
      fetchPosts(1); // Refresh posts after submission
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create post');
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (postId) => {
    try {
      await axios.post(
        `http://localhost:8000/community/posts/${postId}/like`,
        {},
        { withCredentials: true }
      );
      // Update the post's like count in the local state
      setPosts(posts.map(post => 
        post.id === postId 
          ? { ...post, likes: post.likes + 1 }
          : post
      ));
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to like post');
    }
  };

  if (loading && !community) {
    return <div className="loading">Loading community...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="community-page">
      <button onClick={() => {
        navigate(`/your_smile_journey/${id}`)
      }}>View Your Journey</button>
      {community && (
        <div className="community-header">
          <h1>{community.name}</h1>
          <p className="community-description">{community.description}</p>
          <div className="community-stats">
            <span><FaUser /> {community.member_count} members</span>
          </div>
        </div>
      )}

      <div className="create-post">
        <form onSubmit={handlePostSubmit}>
          <textarea
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            placeholder="Share something with your community..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !newPost.trim()}>
            {loading ? 'Posting...' : 'Post'}
          </button>
        </form>
      </div>

      <div className="posts-container">
        {posts.map(post => (
          <div key={post.id} className="post-card" onClick={() => navigate(`/community/${post.id}`)}>
            <div className="post-header">
              <span className="post-author">{post.author}</span>
              <span className="post-date">
                {new Date(post.created_at).toLocaleDateString()}
              </span>
            </div>
            <div className="post-content" style={{color:'black'}}>{post.content}</div>
            <div className="post-actions">
              <button 
                className="like-button" 
                onClick={() => handleLike(post.id)}
              >
                <FaHeart /> {post.likes}
              </button>
              <button 
                className="comment-button"
                onClick={() => window.location.href = `/post/${post.id}`}
              >
                <FaComment /> {post.comment_count}
              </button>
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button 
            onClick={() => setCurrentPage(p => p - 1)}
            disabled={currentPage === 1 || loading}
          >
            Previous
          </button>
          <span>{currentPage} of {totalPages}</span>
          <button 
            onClick={() => setCurrentPage(p => p + 1)}
            disabled={currentPage === totalPages || loading}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default CommunityPage;