import { motion } from "framer-motion";
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useGoogleLogin } from '@react-oauth/google';
import axios from "axios";

import "./css/Register.css";
import MainLayout from "../layouts/MainLayout";

function Register_account() {
    const navigate = useNavigate();
    
    const [form, setForm] = useState({
        fname: "",
        lname: "",
        email: "",
        password: "",
    });

    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [messageType, setMessageType] = useState("");

    // ✅ FIX: Use import.meta.env for Vite
    const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setLoading(true);
        setMessage("");
        setMessageType("");

        try {
            const res = await axios.post(
                `${API_URL}/account/register/`,
                form
            );

            if (res.data.success) {
                localStorage.setItem("token", res.data.token);
                localStorage.setItem("user", JSON.stringify(res.data.user));
                
                setMessage(res.data.message || "Registration successful!");
                setMessageType("success");
                
                setTimeout(() => {
                    navigate("/");
                }, 1500);
            } else {
                setMessage(res.data.message || "Registration failed");
                setMessageType("error");
            }

            setForm({
                fname: "",
                lname: "",
                email: "",
                password: "",
            });

        } catch (err) {
            if (err.response) {
                setMessage(
                    err.response.data.message || 
                    err.response.data.error || 
                    "Registration failed"
                );
            } else {
                setMessage("Server Error. Please try again later.");
            }
            setMessageType("error");
        }

        setLoading(false);
    };

    // Google Registration
    const googleRegister = useGoogleLogin({
        onSuccess: async (tokenResponse) => {
            setLoading(true);
            setMessage("");
            setMessageType("");

            try {
                const userInfoResponse = await axios.get(
                    'https://www.googleapis.com/oauth2/v3/userinfo',
                    {
                        headers: {
                            Authorization: `Bearer ${tokenResponse.access_token}`
                        }
                    }
                );

                const userInfo = userInfoResponse.data;
                
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
                    setMessage("Registration with Google successful!");
                    setMessageType("success");
                    setTimeout(() => navigate("/"), 1500);
                } else {
                    setMessage(response.data.message || "Google registration failed");
                    setMessageType("error");
                }
            } catch (error) {
                console.error('Google Registration Error:', error);
                setMessage(
                    error.response?.data?.message || 
                    "Google registration failed. Please try again."
                );
                setMessageType("error");
            } finally {
                setLoading(false);
            }
        },
        onError: (error) => {
            console.error('Google Registration Error:', error);
            setMessage("Google registration failed. Please try again.");
            setMessageType("error");
            setLoading(false);
        }
    });

    return (
        <div className="register-page">
            <MainLayout>
                <motion.div
                    className="register-content"
                    initial={{ opacity: 0, y: 40 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <h1>Create Account</h1>

                    <div className="register-form-container">
                        <form
                            className="register-form"
                            onSubmit={handleSubmit}
                        >
                            <input
                                type="text"
                                name="fname"
                                placeholder="First Name"
                                value={form.fname}
                                onChange={handleChange}
                                required
                            />

                            <input
                                type="text"
                                name="lname"
                                placeholder="Last Name"
                                value={form.lname}
                                onChange={handleChange}
                                required
                            />

                            <input
                                type="email"
                                name="email"
                                placeholder="Email"
                                value={form.email}
                                onChange={handleChange}
                                required
                            />

                            <input
                                type="password"
                                name="password"
                                placeholder="Password"
                                value={form.password}
                                onChange={handleChange}
                                required
                            />

                            <button
                                type="submit"
                                disabled={loading}
                            >
                                {loading ? "Creating..." : "Register"}
                            </button>
                        </form>

                        <div className="divider">
                            <span>or</span>
                        </div>

                        <button 
                            className="google-register-btn" 
                            onClick={() => googleRegister()}
                            disabled={loading}
                        >
                            <img src="/google-icon.png" alt="Google" />
                            {loading ? "Processing..." : "Register with Google"}
                        </button>
                        
                        {message && (
                            <p className={`register-message ${messageType}`}>
                                {message}
                            </p>
                        )}

                        <p className="login-link">
                            Already have an account? <a href="/login">Login</a>
                        </p>
                    </div>
                </motion.div>
            </MainLayout>
        </div>
    );
}

export default Register_account;