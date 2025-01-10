import React from "react";
import "./NavAfterLogin.css"
import { useAuth } from "./contexts/AuthContext";

const NavAfterLogin=React.memo(() => {
    // let username=localStorage.getItem("user");
    // const data = JSON.parse(username);
    // username=data.username || "User";
    // console.log(username);
    return(
        <div className="navContainer">
            <nav className="TopNavBar">
                <div className="Logo">
                    <span className="Smile">Smile</span>
                    <span className="Again">Again</span>
                </div>
                <div className="Links">
                    <a href="/home">Home</a>
                    <a href="/activities">Activities</a>
                    <a href="/blogs">Blogs</a>
                    <a href="/workshops">Workshops</a>
                    <a href="/chats">Chats</a>
                    <a href="/about-us">About us</a>
                    <a href="/myProfile">User</a>
                </div>
            </nav>
        </div>
    );

});

export default NavAfterLogin;