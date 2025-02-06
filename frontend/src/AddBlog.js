import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./AddBlog.css";

const AddBlog = () => {
  const [formData, setFormData] = useState({
    title: "",
    content: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (!formData.title.trim() || !formData.content.trim()) {
        setError("Title and content are required");
        setLoading(false);
        return;
      }

      const response = await axios.post("http://localhost:8000/blogs", formData, {
        headers: {
          "Content-Type": "application/json",
        },
        withCredentials: true,
      });

      if (response.data.message === "Blog created successfully") {
        setFormData({ title: "", content: "" });
        navigate("/blogs");
      }
    } catch (error) {
      console.error("Error adding blog:", error);
      setError(error.response?.data?.error || "Failed to create blog post");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <div className="add-blog-container">
      <div className="form-wrapper">
        <h2 style={{color:'white'}}>Add a New Blog</h2>
        {error && <div className="error-message">{error}</div>}

        <form className="add-blog-form" onSubmit={handleSubmit}>
          <input
            type="text"
            name="title"
            placeholder="Enter blog title"
            value={formData.title}
            onChange={handleChange}
            required
            disabled={loading}
          />

          <textarea
            name="content"
            placeholder="Write your blog content here..."
            value={formData.content}
            onChange={handleChange}
            required
            disabled={loading}
          ></textarea>

          <button type="submit" disabled={loading}>
            {loading ? "Creating..." : "Add Blog"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AddBlog;
