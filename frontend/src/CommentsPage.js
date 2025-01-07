import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './CommentsPage.css';

const CommentsPage = () => {
    const { blogId } = useParams(); // Extract blog ID from URL
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    const [imageURL, setImageURL] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchComments = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/blogs/${blogId}/comments`);
                console.log(response.data)
                setComments(response.data || []);
            } catch (error) {
                console.error('Error fetching comments:', error);
                setComments([])
            } finally {
                setLoading(false);
            }
        };

        fetchComments();
    }, [blogId]);

    const handleAddComment = async (e) => {
        e.preventDefault();
        setError('');

        if (!newComment.trim()) {
            setError('Comment content cannot be empty.');
            return;
        }

        try {
            const response = await axios.post(`http://localhost:8000/blogs/${blogId}/comments`, {
                content: newComment,
                image_url: imageURL
            },{headers:{"Content-Type" : "application/json"},withCredentials:true});

            // Update the comments list with the new comment
            setComments(prevComments => [...prevComments, response.data.comment]);
            setNewComment('');
            setImageURL('');
        } catch (error) {
            console.error('Error adding comment:', error);
            setError('Failed to add comment. Please try again.');
        }
    };

    if (loading) {
        return <div className="loading">Loading comments...</div>;
    }

    return (
        <div className="comments-container">
            <h1>Comments for Blog {blogId}</h1>
            <form className="add-comment-form" onSubmit={handleAddComment}>
                <textarea
                    className="comment-input"
                    placeholder="Write your comment here..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                />
                <input
                    className="image-url-input"
                    type="text"
                    placeholder="Optional image URL"
                    value={imageURL}
                    onChange={(e) => setImageURL(e.target.value)}
                />
                <button type="submit" className="add-comment-button">Add Comment</button>
                {error && <p className="error-message">{error}</p>}
            </form>
            {comments.length === 0 ? (
                <p>No comments available.</p>
            ) : (
                comments.map(comment => (
                    <div key={comment.comment_id} className="comment-card">
                        <p className="comment-content">{comment.content}</p>
                        {comment.image_url && (
                            <img src={comment.image_url} alt="Comment visual" className="comment-image" />
                        )}
                        <p className="comment-author">- {comment.created_by}</p>
                    </div>
                ))
            )}
        </div>
    );
};

export default CommentsPage;
