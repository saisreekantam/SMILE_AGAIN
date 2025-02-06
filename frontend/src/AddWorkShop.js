import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './AddWorkshop.css';

const CreateWorkshop = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        banner_url: '',
        meet_link: '',
        price: 0,
        tag: ''
    });
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        try {
            const response = await axios.post(
                'http://localhost:8000/workshops/create',
                formData,
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    withCredentials: true
                }
            );

            if (response.data.workshop_id) {
                navigate('/workshops');  // Redirect to workshops list
            }
        } catch (err) {
            // Handle different types of errors
            if (err.response) {
                const { status, data } = err.response;
                
                if (status === 401) {
                    setError('Please log in to create workshops');
                    // Optional: Redirect to login page
                    // navigate('/login');
                }
                else if (status === 403) {
                    if (data.code === 'ADMIN_REQUIRED') {
                        setError('Only administrators can create workshops. Please contact support if you believe this is an error.');
                    } else {
                        setError('You do not have permission to create workshops');
                    }
                }
                else {
                    setError(data.message || 'Failed to create workshop');
                }
            } else {
                setError('Failed to connect to the server. Please try again later.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    return (
        <div className="create-workshop-container">
            <h2>Create New Workshop</h2>
            
            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}
            
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="title">Title:</label>
                    <input
                        type="text"
                        id="title"
                        name="title"
                        value={formData.title}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="description">Description:</label>
                    <textarea
                        id="description"
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="banner_url">Banner URL:</label>
                    <input
                        type="text"
                        id="banner_url"
                        name="banner_url"
                        value={formData.banner_url}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="meet_link">Meeting Link:</label>
                    <input
                        type="text"
                        id="meet_link"
                        name="meet_link"
                        value={formData.meet_link}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="price">Price:</label>
                    <input
                        type="number"
                        id="price"
                        name="price"
                        value={formData.price}
                        onChange={handleChange}
                        min="0"
                        step="0.01"
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="tag">Tag:</label>
                    <input
                        type="text"
                        id="tag"
                        name="tag"
                        value={formData.tag}
                        onChange={handleChange}
                        required
                    />
                </div>

                <button 
                    type="submit" 
                    disabled={loading}
                    className={loading ? 'loading' : ''}
                    style={{backgroundColor:'purple'}}
                >
                    {loading ? 'Creating...' : 'Create Workshop'}
                </button>
            </form>
        </div>
    );
};

export default CreateWorkshop;