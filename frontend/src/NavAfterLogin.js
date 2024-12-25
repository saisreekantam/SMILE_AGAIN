import React from "react";
import "./NavAfterLogin.css"

const NavAfterLogin=() => {
    const userName=localStorage.getItem("username");
    return(
        <div className="navContainer">
            <nav className="TopNavBar">
                <div className="Logo">
                    <span className="Smile">Smile</span>
                    <span className="Again">Again</span>
                </div>
                <div className="Links">
                    <a href="/">Home</a>
                    <a href="">Blogs</a>
                    <a href="">Workshops</a>
                    <a href="">Chats</a>
                    <a href="">About us</a>
                    <a href="/profile">{userName}</a>
                </div>
            </nav>
        </div>
    );

}

export default NavAfterLogin;