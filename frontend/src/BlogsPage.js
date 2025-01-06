import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './BlogsPage.css';
import axios from 'axios';

const BlogsPage = () => {
    const [blogs, setBlogs] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchBlogs = async () => {
            try {
                const response = await axios.get("http://localhost:8000/blogs");
                console.log('API Response:', response.data); // Debug the response
                setBlogs(response.data || []); // Ensure blogs is always an array
                // setBlogs(response.data.blogs_list);
            } catch (error) {
                console.error('Error fetching blogs:', error);
            }
        };

        fetchBlogs();
    }, []);

    return (
        <div className="blogs-container">
            <h2>Blogs</h2>
            <button className="add-blog-button" onClick={() => navigate('/add-blog')}>
                Add Blog
            </button>
            {blogs.length === 0 ? (
                <p className="no-blogs-message">No blogs available to display.</p>
            ) : (
                blogs.map(blog => (
                    <div key={blog.blog_id} className="blog-card">
                        <h3 className="user-community">
                            <a href={`/user/${blog.created_by}`} className="created-by-link">
                                {blog.created_by}
                            </a>
                            /
                            <a href={`/community/${blog.community_name}`} className="community-name-link">
                                {blog.community_name}
                            </a>
                        </h3>
                        <h2 className="blog-title">{blog.title}</h2>
                        <p className="blog-content">{blog.content}</p>
                        <div className="blog-meta">
                            <span>Likes: {blog.likes}</span>
                            <span>Dislikes: {blog.dislikes}</span>
                        </div>
                        <div className="comments-button">
                            <button onClick={() => navigate(`/blogs/${blog.blog_id}/comments`)}>
                                View Comments
                            </button>
                        </div>
                    </div>
                ))
            )}
        </div>
    );
};

export default BlogsPage;
