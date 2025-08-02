// frontend/src/context/AuthContext.jsx

import React, { createContext, useState, useEffect } from 'react';
import jwt_decode from 'jwt-decode';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwt_decode(token);
        setUser({
          id: decoded.sub,
          role: decoded.role,
        });
      } catch (err) {
        console.error('Invalid token:', err);
        setUser(null);
      }
    } else {
      setUser(null);
    }
    setLoading(false);
  }, []);

  const login = (token) => {
    try {
      const decoded = jwt_decode(token);
      localStorage.setItem('token', token);
      setUser({
        id: decoded.sub,
        role: decoded.role,
      });
    } catch (err) {
      console.error('Failed to decode token on login:', err);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
