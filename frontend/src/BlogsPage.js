import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useNavigate for navigation
import './BlogsPage.css';
import axios from 'axios';

const BlogsPage = () => {
    const [blogs, setBlogs] = useState([]);
    const navigate = useNavigate(); // Hook for navigation

    useEffect(() => {
        const fetchBlogs = async () => {
            try {
                const response = await axios.get("http://localhost:8000/auth/blogs");
                setBlogs(response.data.blogs_data);
            } catch (error) {
                console.error('Error fetching blogs:', error);
            }
        };

        fetchBlogs();
    }, []);

    const handleViewComments = (blogId) => {
        navigate(`/blogs/${blogId}/comments`);
    };

    return (
        <div className="blogs-container">
            {blogs.map(blog => (
                <div key={blog.blog_id} className="blog-card">
                    <h3 className="user-community">{`${blog.created_by}/${blog.community_name}`}</h3>
                    <h2 className="blog-title">{blog.title}</h2>
                    <p className="blog-content">{blog.content}</p>
                    <div className="blog-meta">
                        <span>Likes: {blog.likes}</span>
                        <span>Dislikes: {blog.dislikes}</span>
                    </div>
                    <div className="comments-button">
                        <button onClick={() => handleViewComments(blog.blog_id)}>
                            View Comments
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default BlogsPage;
