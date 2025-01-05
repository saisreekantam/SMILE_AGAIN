import React, { useState } from "react";
import "./RegistrationPage.css";
import axios from 'axios';
import { useNavigate } from "react-router-dom";

function RegistrationPage() {
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        gender: "",
        password: "",
        confirmPassword: ""
    });
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        // Password validation
        if (formData.password !== formData.confirmPassword) {
            setError("Passwords do not match!");
            return;
        }

        try {
            const response = await axios.post(
                "http://localhost:8000/auth/register",
                {
                    name: formData.name,
                    email: formData.email,
                    gender: formData.gender,
                    password: formData.password
                },
                {
                    headers: { 
                        'Content-Type': 'application/json'
                    },
                    withCredentials: true
                }
            );

            if (response.status === 201) {
                localStorage.setItem("username", formData.name);
                navigate('/problem_page');
            }
        } catch (err) {
            console.error('Error Registering: ', err);
            setError(err.response?.data?.error || "Registration failed. Please try again.");
        }
    };

    return (
        <div className="registration-container">
            <h2>Registration Page</h2>
            {error && <div className="error-message">{error}</div>}
            <form onSubmit={handleSubmit}>
                <input 
                    type="text" 
                    name="name" 
                    placeholder="Full Name" 
                    value={formData.name}
                    onChange={handleChange}
                    required 
                />
                <input 
                    type="email" 
                    name="email" 
                    placeholder="Email" 
                    value={formData.email}
                    onChange={handleChange}
                    required 
                />
                <select 
                    name="gender" 
                    value={formData.gender}
                    onChange={handleChange}
                    required
                >
                    <option value="" disabled>Select Gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                </select>
                <input 
                    type="password" 
                    name="password" 
                    placeholder="Password" 
                    value={formData.password}
                    onChange={handleChange}
                    required 
                />
                <input 
                    type="password" 
                    name="confirmPassword" 
                    placeholder="Confirm Password" 
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    required 
                />
                <button type="submit">Register</button>
            </form>
            <div className="links">
                <a href="/login">Already have an account? Login here</a>
                <a href="/">Go back to homepage</a>
            </div>
        </div>
    );
}

export default RegistrationPage;