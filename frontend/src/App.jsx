import React, { useEffect, useState } from 'react';
import Home from "./pages/Home";
import { userAPI } from './api/taskboard';
import Auth from "./pages/Auth";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const checkAuth = () => {
    setIsAuthenticated(userAPI.isAuthenticated());
  };

  useEffect(() => {
    checkAuth();
    const handler = () => checkAuth();
    window.addEventListener('auth:changed', handler);
    return () => window.removeEventListener('auth:changed', handler);
  }, []);

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
  };

  return isAuthenticated ? <Home /> : <Auth onAuthSuccess={handleAuthSuccess} />;
}

export default App;

