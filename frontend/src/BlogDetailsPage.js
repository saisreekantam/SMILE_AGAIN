import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './BlogDetailsPage.css';

const BlogDetailsPage = () => {
    const { blogId } = useParams(); // Extract blog ID from the URL
    const [blog, setBlog] = useState(null);
    const [comments, setComments] = useState([]);
    const [likeCount, setLikeCount] = useState(0);
    const [dislikeCount, setDislikeCount] = useState(0);

    useEffect(() => {
        // Fetch blog details
        const fetchBlogDetails = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/blogs/${blogId}`);
                setBlog(response.data);
                setLikeCount(response.data.likes || 0);
                setDislikeCount(response.data.dislikes || 0);
            } catch (error) {
                console.error('Error fetching blog details:', error);
            }
        };

        // Fetch blog comments
        const fetchComments = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/blogs/${blogId}/comments`);
                setComments(response.data || []); // Ensure comments is always an array
            } catch (error) {
                console.error('Error fetching comments:', error);
            }
        };

        fetchBlogDetails();
        fetchComments();
    }, [blogId]);

    // Handle like button click
    const handleLike = async () => {
        try {
            await axios.post(`http://localhost:8000/blogs/${blogId}/like`);
            setLikeCount(prev => prev + 1);
        } catch (error) {
            console.error('Error liking blog:', error);
        }
    };

    // Handle dislike button click
    const handleDislike = async () => {
        try {
            await axios.post(`http://localhost:8000/blogs/${blogId}/dislike`);
            setDislikeCount(prev => prev + 1);
        } catch (error) {
            console.error('Error disliking blog:', error);
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
                <button className="like-button" onClick={handleLike}>👍 Like ({likeCount})</button>
                <button className="dislike-button" onClick={handleDislike}>👎 Dislike ({dislikeCount})</button>
            </div>
            <div className="comments-section">
                <h2>Comments</h2>
                {comments.length === 0 ? (
                    <p>No comments yet. Be the first to comment!</p>
                ) : (
                    comments.map(comment => (
                        <div key={comment.comment_id} className="comment-card">
                            <p><strong>{comment.author_name}:</strong> {comment.content}</p>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default BlogDetailsPage;
