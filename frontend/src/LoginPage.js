import React, { useState, useEffect } from "react";
import "./LoginPage.css";
import { useAuth } from "./contexts/AuthContext";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";

function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const { login, isLoggedIn,username } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const data = {
            email: email,
            password: password,
        };

        try {
            const response = await axios.post(
                "http://localhost:8000/auth/login",
                data,
                { headers: { "Content-Type": "application/json" } }
            );

            if (response.data.success) {
                const Username=response.data.username;
                login(Username); 
                console.log("Login successful:", response.data);
                console.log("Username from authContext ",username);
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

    // Monitor `isLoggedIn` and navigate when it becomes `true`
    useEffect(() => {
        if (isLoggedIn) {
            console.log("Navigating to /problem_page...");
            console.log(isLoggedIn);
            navigate("/mood_entry");   
        }
    }, [isLoggedIn, navigate]);

    return (
        <div className="login-container">
            <h2>Login Page</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    name="username"
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
            <a href="/register">Not registered? Register here</a>
            <a href="/">Go back to homepage</a>
        </div>
    );
}

export default LoginPage;
