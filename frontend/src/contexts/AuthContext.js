import React, { createContext, useState, useEffect, useContext } from "react";


const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    // useEffect(() => {
    //     const storedUser = localStorage.getItem("user");
    //     if (storedUser) {
    //         const parsedUser = JSON.parse(storedUser);
    //         setUser(parsedUser);
    //         setIsLoggedIn(true);
    //     }
    // }, []);

    const login = (userDetails) => {
        setUser(userDetails);
        setIsLoggedIn(true);
        localStorage.setItem("user", JSON.stringify(userDetails));
    };

    const logout = () => {
        setUser(null);
        setIsLoggedIn(false);
        localStorage.removeItem("user");
    };

    const username = user?.username || "Guest";

    return (
        <AuthContext.Provider value={{ user, isLoggedIn, login, logout, username }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
