import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './BlogsPage.css';
import axios from 'axios';
import NavAfterLogin from './NavAfterLogin';

const BlogsPage = () => {
    const [blogs, setBlogs] = useState([]);
    const navigate = useNavigate();
    const [likes,setLikes] = useState(2);
    const [dislikes,setDislikes] = useState(0);

    useEffect(() => {
        const fetchBlogs = async () => {
            try {
                const response = await axios.get("http://localhost:8000/blogs");
                console.log('API Response:', response.data); // Debug the response
                setBlogs(response.data || []); // Ensure blogs is always an array
            } catch (error) {
                console.error('Error fetching blogs:', error);
            }
        };

        fetchBlogs();
    }, []);

    const handleLike = async (blogId) => {
        try {
            const response = await axios.post(`http://localhost:8000/blogs/${blogId}/like`, { blogId });
            if (response.status === 200) {
                setBlogs(prevBlogs =>
                    prevBlogs.map(blog =>
                        blog.blog_id === blogId
                            ? { ...blog, likes: blog.likes + 1 }
                            : blog
                    )
                );
            }
            setLikes(likes+1);
        } catch (error) {
            console.error('Error liking the blog:', error);
        }
    };

    const handleDislike = async (blogId) => {
        try {
            const response = await axios.post(`http://localhost:8000/blogs/${blogId}/dislike`, { blogId });
            if (response.status === 200) {
                setBlogs(prevBlogs =>
                    prevBlogs.map(blog =>
                        blog.blog_id === blogId
                            ? { ...blog, dislikes: blog.dislikes + 1 }
                            : blog
                    )
                );
            }
            setDislikes(dislikes+1);
        } catch (error) {
            console.error('Error disliking the blog:', error);
        }
    };

    // Function to truncate content
    const truncateContent = (content, length = 100) => {
        if (content.length > length) {
            return content.substring(0, length) + '...';
        }
        return content;
    };

    return (
        <div className="Blogs-container">
            <NavAfterLogin />
            <div className='blogs-container'>
                <h2>Blogs</h2>
                <button className="add-blog-button" onClick={() => navigate('/add-blog')}>
                    +
                </button>
                {blogs.length === 0 ? (
                    <p className="no-blogs-message">No blogs available to display.</p>
                ) : (
                    blogs.map(blog => (
                        <div 
                            key={blog.blog_id} 
                            className="blog-card" 
                            onClick={() =>{
                                console.log("Navigating with blog:",blog); 
                                navigate(`/blogs/${blog.blog_id}`,{state: { blog }})} // Navigate to blog details page
                            }
                            style={{ cursor: "pointer" }}
                        >
                            <h3 className="user-community">
                                <a href={`/user/${blog.created_by}`} className="created-by-link" onClick={(e) => e.stopPropagation()}>
                                    {blog.author_name}
                                </a>
                            </h3>
                            <h2 className="blog-title">{blog.title}</h2>
                            <p className="blog-content">{truncateContent(blog.content)}</p>
                            <div className="blog-meta">
                                <span className="meta-item">
                                    Likes: <span onClick={(e) => { handleLike(blog.blog_id); e.stopPropagation(); }}>👍</span>
                                </span>
                                <span className="meta-item">
                                    Dislikes: <span onClick={() => handleDislike(blog.blog_id)}>👎</span>
                                </span>
                           </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default BlogsPage;
