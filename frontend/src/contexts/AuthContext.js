import React, { createContext, useState, useContext } from 'react';


const AuthContext = createContext();


export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null); // User details
  const [isLoggedIn, setIsLoggedIn] = useState(false); // Login status

  const login = (userDetails) => {
    setUser(userDetails);
    setIsLoggedIn(true);
  };


  const logout = () => {
    setUser(null);
    setIsLoggedIn(false);
  };

  return (
    <AuthContext.Provider value={{ user, isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};
