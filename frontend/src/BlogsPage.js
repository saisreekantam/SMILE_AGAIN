import React, { useState, useEffect } from "react";
import "./BlogsPage.css";
import axios from "axios";

const BlogsPage = () => {
  const [blogs, setBlogs] = useState([]);

  useEffect(() => {
    const fetchBlogs = async () => {
      try {
        const response = await axios.get("http://localhost:8000/auth/blogs");
        setBlogs(response.data);
      } catch (error) {
        console.error("Error fetching blogs:", error);
      }
    };

    fetchBlogs();
  }, []);

  return (
    <div className="main-container">
      <div className="blogs-container">
        <h1 className="page-title">All Blogs</h1>
        <div className="blogs-grid">
          {blogs.map((blog) => (
            <div className="blog-card" key={blog.id}>
              <h2 className="blog-title">{blog.title}</h2>
              <p className="blog-author">By {blog.author}</p>
              <p className="blog-snippet">{blog.content.slice(0, 100)}...</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BlogsPage;
