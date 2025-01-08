import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import NavAfterLogin from './NavAfterLogin';
import './PostPage.css';
import { FaHeart, FaArrowLeft } from 'react-icons/fa';

const PostPage = () => {
  const { postId } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPostAndComments();
  }, [postId]);

  const fetchPostAndComments = async () => {
    try {
      setLoading(true);
      const commentsResponse = await axios.get(
        `http://localhost:8000/community/posts/${postId}/comments`,
        { withCredentials: true }
      );
      setComments(commentsResponse.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load post and comments');
    } finally {
      setLoading(false);
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      setLoading(true);
      await axios.post(
        `http://localhost:8000/community/posts/${postId}/comments`,
        { content: newComment },
        { withCredentials: true }
      );
      setNewComment('');
      fetchPostAndComments(); // Refresh comments
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to post comment');
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    try {
      const response = await axios.post(
        `http://localhost:8000/community/posts/${postId}/like`,
        {},
        { withCredentials: true }
      );
      setPost(prev => ({
        ...prev,
        likes: response.data.new_like_count
      }));
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to like post');
    }
  };

  if (loading && !post) {
    return <div className="loading">Loading post...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="post-page">
      <NavAfterLogin />
      
      <div className="post-container">
        <button 
          className="back-button"
          onClick={() => navigate(-1)}
        >
          <FaArrowLeft /> Back to Community
        </button>

        {post && (
          <div className="post-details">
            <div className="post-header">
              <span className="post-author">{post.author}</span>
              <span className="post-date">
                {new Date(post.created_at).toLocaleDateString()}
              </span>
            </div>
            <div className="post-content">{post.content}</div>
            <div className="post-actions">
              <button 
                className="like-button" 
                onClick={handleLike}
              >
                <FaHeart /> {post.likes}
              </button>
            </div>
          </div>
        )}

        <div className="comments-section">
          <h3>Comments</h3>
          
          <form className="comment-form" onSubmit={handleCommentSubmit}>
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !newComment.trim()}>
              {loading ? 'Posting...' : 'Post Comment'}
            </button>
          </form>

          <div className="comments-list">
            {comments.map(comment => (
              <div key={comment.id} className="comment-card">
                <div className="comment-header">
                  <span className="comment-author">{comment.author}</span>
                  <span className="comment-date">
                    {new Date(comment.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="comment-content">{comment.content}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PostPage;