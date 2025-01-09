import React, { createContext, useState, useEffect, useContext } from "react";


const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [username,setuserName]=useState("User");
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
        setIsLoggedIn(true);
        setuserName(userDetails || "User");
        
    };

    const logout = () => {
        setUser(null);
        setIsLoggedIn(false);
        
    };

  

    return (
        <AuthContext.Provider value={{ user, isLoggedIn, login, logout, username }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);
