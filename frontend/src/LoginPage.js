import React from "react";
import "./LoginPage.css";

function LoginPage() {
    return (
        <div className="login-container">
            <h2>Login Page</h2>
            <form action="/login" method="POST">
                <input type="text" name="username" placeholder="Username" required />
                <input type="password" name="password" placeholder="Password" required />
                <button type="submit">Login</button>
            </form>
            <a href="/register">Not registered? Register here</a>
            <a href="/">Go back to homepage</a>
        </div>
    );
}

export default LoginPage;
