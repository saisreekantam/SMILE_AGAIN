// AddBlog.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './AddBlog.css';

/**
 * AddBlog Component
 * Provides a form interface for creating new blog posts
 */
const AddBlog = () => {
    // State management for form data and UI states
    const [formData, setFormData] = useState({ 
        title: '', 
        content: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    /**
     * Handle form submission
     * @param {Event} e - Form submission event
     */
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // Validate inputs
            if (!formData.title.trim() || !formData.content.trim()) {
                setError('Title and content are required');
                setLoading(false);
                return;
            }

            const response = await axios.post(
                "http://localhost:8000/blogs", 
                formData,
                {
                    headers: { 
                        "Content-Type": "application/json"
                    },
                    withCredentials: true
                }
            );
            
            if (response.data.message === "Blog created successfully") {
                setFormData({ title: '', content: '' });
                navigate('/blogs');
            }
        } catch (error) {
            console.error('Error adding blog:', error);
            setError(error.response?.data?.error || 'Failed to create blog post');
        } finally {
            setLoading(false);
        }
    };

    /**
     * Handle input changes
     * @param {Event} e - Input change event
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    return (
        <div className="add-blog-container">
            <h2>Add a New Blog</h2>
            {error && <div className="error-message">{error}</div>}
            
            <form className="add-blog-form" onSubmit={handleSubmit}>
                <input
                    type="text"
                    name="title"
                    placeholder="Title"
                    value={formData.title}
                    onChange={handleChange}
                    required
                    disabled={loading}
                />
                
                <textarea
                    name="content"
                    placeholder="Content"
                    value={formData.content}
                    onChange={handleChange}
                    required
                    disabled={loading}
                />
                
                <button 
                    type="submit" 
                    disabled={loading}
                    className={loading ? 'loading' : ''}
                >
                    {loading ? 'Creating...' : 'Add Blog'}
                </button>
            </form>
        </div>
    );
};

export default AddBlog;