import React from "react";
import "./NavAfterLogin.css"
import { useAuth } from "./contexts/AuthContext";

const NavAfterLogin=() => {
    const { username } = useAuth();
    const userName=username.username || "User";
    console.log(userName);
    return(
        <div className="navContainer">
            <nav className="TopNavBar">
                <div className="Logo">
                    <span className="Smile">Smile</span>
                    <span className="Again">Again</span>
                </div>
                <div className="Links">
                <a href="/home">Home</a>
                    <a href="/blogs">Blogs</a>
                    <a href="/workshops">Workshops</a>
                    <a href="/chats">Chats</a>
                    <a href="/about-us">About us</a>
                    <a href="/myProfile">{userName}</a>
                </div>
            </nav>
        </div>
    );

}

export default NavAfterLogin;