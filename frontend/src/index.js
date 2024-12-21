import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';  // Global CSS file for styling
import App from './App';  // Main App component
import { BrowserRouter as Router } from 'react-router-dom';  // Router for managing routing

const root = ReactDOM.createRoot(document.getElementById('root')); // Get the root DOM element

root.render(
  <React.StrictMode> {/* Ensures your app runs in development mode with extra checks */}
    <Router> {/* Router to manage all routing */}
      <App />
    </Router>
  </React.StrictMode>
);
