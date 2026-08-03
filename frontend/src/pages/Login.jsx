import { motion } from 'framer-motion';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';

import './css/Login.css';
import MainLayout from '../layouts/MainLayout';

function Login() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

    // Email/Password login
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const response = await axios.post(
                `${API_URL}/account/login/`,
                { email, password }
            );

            if (response.data.success) {
                localStorage.setItem("token", response.data.token);
                localStorage.setItem("user", JSON.stringify(response.data.user));
                alert("Login Successful!");
                navigate("/");
            }
        } catch (error) {
            setError(
                error.response?.data?.message || 
                "Login Failed. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    // Google Login
    const googleLogin = useGoogleLogin({
        onSuccess: async (tokenResponse) => {
            setLoading(true);
            setError("");

            try {
                // Get user info from Google
                const userInfoResponse = await axios.get(
                    'https://www.googleapis.com/oauth2/v3/userinfo',
                    {
                        headers: {
                            Authorization: `Bearer ${tokenResponse.access_token}`
                        }
                    }
                );

                const userInfo = userInfoResponse.data;
                
                // Send to your backend
                const response = await axios.post(
                    `${API_URL}/account/google-login/`,
                    {
                        email: userInfo.email,
                        first_name: userInfo.given_name || userInfo.name?.split(' ')[0] || '',
                        last_name: userInfo.family_name || userInfo.name?.split(' ').slice(1).join(' ') || '',
                        google_id: userInfo.sub,
                        picture: userInfo.picture || ''
                    }
                );

                if (response.data.success) {
                    localStorage.setItem("token", response.data.token);
                    localStorage.setItem("user", JSON.stringify(response.data.user));
                    alert("Google Login Successful!");
                    navigate("/");
                } else {
                    setError(response.data.message || "Google login failed");
                }
            } catch (error) {
                console.error('Google Login Error:', error);
                setError(
                    error.response?.data?.message || 
                    "Google login failed. Please try again."
                );
            } finally {
                setLoading(false);
            }
        },
        onError: (error) => {
            console.error('Google Login Error:', error);
            setError("Google login failed. Please try again.");
            setLoading(false);
        }
    });

    return (
        <div className="login-page">
            <MainLayout>
                <motion.div
                    className="login-content"
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <h1>Login</h1>

                    <div className="login-form-container">
                        <form
                            className="login-form"
                            onSubmit={handleSubmit}
                        >
                            <input
                                type="email"
                                placeholder="Email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />

                            <input
                                type="password"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />

                            {error && (
                                <p className="login-error">{error}</p>
                            )}

                            <button type="submit" disabled={loading}>
                                {loading ? "Logging in..." : "Login"}
                            </button>
                        </form>

                        <div className="divider">
                            <span>or</span>
                        </div>

                        <button 
                            className="google-login-btn" 
                            onClick={() => googleLogin()}
                            disabled={loading}
                        >
                            <img
                                src="/google-icon.png"
                                alt="Google"
                            />
                            {loading ? "Processing..." : "Login with Google"}
                        </button>

                        <p className="register-link">
                            Don't have an account? <a href="/register">Register</a>
                        </p>
                    </div>
                </motion.div>
            </MainLayout>
        </div>
    );
}

export default Login;