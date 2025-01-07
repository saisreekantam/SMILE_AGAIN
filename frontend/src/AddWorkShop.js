import React, { useState } from "react";
import "./AddWorkshop.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const AddWorkshop = () => {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    banner_url: "",
    meet_link: "",
    price: "",
    sponsored: false,
    tag: "",
  });

  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const { title, description, banner_url, meet_link, tag } = formData;
    if (!title || !description || !banner_url || !meet_link || !tag) {
      setError("All fields are required.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/workshops/create", formData, {
        headers: { "Content-Type": "application/json" },
        withCredentials: true,
      });
      setSuccess("Workshop created successfully!");
      setTimeout(() => navigate("/workshops"), 2000);
    } catch (err) {
      setError(err.response?.data?.error || "Failed to create workshop. Please try again.");
    }
  };

  return (
    <div className="add-workshop-container">
      <h1 className="header">Add Workshop</h1>
      <form className="add-workshop-form" onSubmit={handleSubmit}>
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <div className="form-group">
          <label htmlFor="title">Title</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="Enter workshop title"
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Enter workshop description"
          ></textarea>
        </div>

        <div className="form-group">
          <label htmlFor="banner_url">Banner URL</label>
          <input
            type="text"
            id="banner_url"
            name="banner_url"
            value={formData.banner_url}
            onChange={handleChange}
            placeholder="Enter banner URL"
          />
        </div>

        <div className="form-group">
          <label htmlFor="meet_link">Meet Link</label>
          <input
            type="text"
            id="meet_link"
            name="meet_link"
            value={formData.meet_link}
            onChange={handleChange}
            placeholder="Enter meet link"
          />
        </div>

        <div className="form-group">
          <label htmlFor="price">Price</label>
          <input
            type="number"
            id="price"
            name="price"
            value={formData.price}
            onChange={handleChange}
            placeholder="Enter price (0 for free)"
          />
        </div>

        <div className="form-group">
          <label htmlFor="sponsored">Sponsored</label>
          <input
            type="checkbox"
            id="sponsored"
            name="sponsored"
            checked={formData.sponsored}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="tag">Tag</label>
          <input
            type="text"
            id="tag"
            name="tag"
            value={formData.tag}
            onChange={handleChange}
            placeholder="Enter workshop tag"
          />
        </div>

        <button type="submit" className="submit-btn">Create Workshop</button>
      </form>
    </div>
  );
};

export default AddWorkshop;
