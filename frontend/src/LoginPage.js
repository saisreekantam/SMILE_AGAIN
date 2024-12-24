import React, { useState } from "react";
import "./LoginPage.css";
import axios from "axios";


function LoginPage() {
    const [email,setEmail]=useState("");
    const [password,setPassword]=useState("");
    const handleSubmit=async (e) => {
        e.preventDefault();
        const data={
            email:email,
            password:password
        };
        try{
            const response=await axios.post("http://localhost:8000/auth/login",data,{headers: { 'Content-Type' : 'application/json'}});
            console.log(response.data);
        }
        catch(err){
            if (err.response && err.response.status === 401) {
                alert("Invalid credentials");
            } else {
                console.error("Error logging in", err);
            }
        }
    }
    return (
        <div className="login-container">
            <h2>Login Page</h2>
            <form onSubmit={handleSubmit}>
                <input type="text" name="username" placeholder="Email" required onChange={(e) => setEmail(e.target.value)}/>
                <input type="password" name="password" placeholder="Password" required onChange={(e) => setPassword(e.target.value)}/>
                <button type="submit">Login</button>
            </form>
            <a href="/register">Not registered? Register here</a>
            <a href="/">Go back to homepage</a>
        </div>
    );
}

export default LoginPage;
