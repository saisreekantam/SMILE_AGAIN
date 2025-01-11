import React, { useState, useEffect } from "react";
import "./LoginPage.css";
import { useAuth } from "./contexts/AuthContext";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import login_bg from "./assets/Login_Bg.jpg"

function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const { login, isLoggedIn, username } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const data = { email, password };

        try {
            const response = await axios.post(
                "http://localhost:8000/auth/login",
                data,
                { headers: { "Content-Type": "application/json" } }
            );

            if (response.data.success) {
                const Username = response.data.username;
                login(Username);
                console.log("Login successful:", response.data);
                console.log("Username from authContext ", username);
            } else {
                alert("Login failed");
            }
        } catch (err) {
            if (err.response && err.response.status === 401) {
                alert("Invalid credentials");
            } else {
                console.error("Error logging in", err);
            }
        }
    };

    useEffect(() => {
        if (isLoggedIn) {
            console.log("Navigating to /mood_entry...");
            navigate("/mood_entry");
        }
    }, [isLoggedIn, navigate]);

    return (
        <div className="login-page">
            <div className="login-image">
                <img
                    src={login_bg}
                    alt="Login Illustration"
                />
            </div>
            <div className="login-form-container">
                <h2>Login Page</h2>
                <form onSubmit={handleSubmit} className="login-form">
                    <input
                        type="text"
                        name="email"
                        placeholder="Email"
                        required
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <input
                        type="password"
                        name="password"
                        placeholder="Password"
                        required
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <button type="submit">Login</button>
                </form>
                <div className="login-links">
                    <Link to="/register">Not registered? Register here</Link>
                    <Link to="/">Go back to homepage</Link>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;
