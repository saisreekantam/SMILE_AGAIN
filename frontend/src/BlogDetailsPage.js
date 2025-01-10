import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types'; // For type-checking props
import axios from 'axios';
import './BlogDetailsPage.css';
import { useLocation } from 'react-router-dom';

const BlogDetailsPage = () => {
    const location=useLocation();
    const { blog } = location.state || {}
    const [comments, setComments] = useState([]);
    const [likeCount, setLikeCount] = useState(0);
    const [dislikeCount, setDislikeCount] = useState(0);
    console.log(blog);

    useEffect(() => {
        // If there is logic to update the comments or actions dynamically, it can be handled here.
        fetchComments();
    }, [blog]);

    const handleLike = async () => {
        try {
            await axios.post(`http://localhost:8000/blogs/${blog.blog_id}/like`);
            setLikeCount(prev => prev + 1);
        } catch (error) {
            console.error('Error liking blog:', error);
        }
    };

    // Handle dislike button click
    const handleDislike = async () => {
        try {
            await axios.post(`http://localhost:8000/blogs/${blog.blog_id}/dislike`);
            setDislikeCount(prev => prev + 1);
        } catch (error) {
            console.error('Error disliking blog:', error);
        }
    };
    const fetchComments = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/blogs/${blog.blog_id}/comments`);
            setComments(response.data || []); // Ensure comments is always an array
        } catch (error) {
            console.error('Error fetching comments:', error);
        }
    };

    if (!blog) {
        return <p>Loading blog details...</p>;
    }

    return (
        <div className="blog-details-container">
            <h1 className="blog-title">{blog.title}</h1>
            <p className="blog-content">{blog.content}</p>
            <div className="blog-actions">
                <button className="like-button" onClick={handleLike}>
                    👍 Like ({likeCount})
                </button>
                <button className="dislike-button" onClick={handleDislike}>
                    👎 Dislike ({dislikeCount})
                </button>
            </div>
            <div className="comments-section">
                <h2>Comments</h2>
                {comments.length === 0 ? (
                    <p>No comments yet. Be the first to comment!</p>
                ) : (
                    comments.map((comment) => (
                        <div key={comment.comment_id} className="comment-card">
                            <p>
                                <strong>{comment.author_name}:</strong> {comment.content}
                            </p>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};


export default BlogDetailsPage;
