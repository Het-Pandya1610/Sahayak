// frontend/src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { GoogleOAuthProvider } from '@react-oauth/google';
import App from './App.jsx';
import './index.css';

// For Vite, use import.meta.env
const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

console.log('Google Client ID:', googleClientId); // Check if it's loading

if (!googleClientId) {
  console.error('Google Client ID is missing! Check your .env.local file');
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={googleClientId}>
      <App />
    </GoogleOAuthProvider>
  </React.StrictMode>
);