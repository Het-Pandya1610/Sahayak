import { motion } from "framer-motion";
import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { getAvatarColors, getInitials, getCurrentTheme } from "../utils/avatarUtils";

import "./css/Profile.css";
import MainLayout from "../layouts/MainLayout";

// Helper function to parse IST date string to Date object
const parseISTDate = (dateStr) => {
    if (!dateStr) return null;
    
    // Try parsing as ISO format first
    let date = new Date(dateStr);
    if (!isNaN(date.getTime())) return date;
    
    // Parse custom format: "2026-08-02 05:10:44 PM IST"
    try {
        const cleanStr = dateStr.replace(' IST', '').trim();
        const parts = cleanStr.split(' ');
        
        if (parts.length < 3) {
            // Try simple date format
            const simpleDate = new Date(cleanStr);
            if (!isNaN(simpleDate.getTime())) return simpleDate;
            return null;
        }
        
        const [datePart, timePart, period] = parts;
        const [year, month, day] = datePart.split('-').map(Number);
        let [hours, minutes, seconds = 0] = timePart.split(':').map(Number);
        
        // Convert to 24-hour format
        if (period === 'PM' && hours !== 12) hours += 12;
        if (period === 'AM' && hours === 12) hours = 0;
        
        // IST is UTC+5:30, convert to UTC for proper display
        const dateObj = new Date(Date.UTC(year, month - 1, day, hours - 5, minutes - 30, seconds));
        return dateObj;
    } catch (error) {
        console.error('Error parsing date:', dateStr, error);
        return null;
    }
};

// Format date for display with full details
const formatDisplayDate = (dateStr) => {
    const date = parseISTDate(dateStr);
    if (!date) return 'Invalid Date';
    
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// Format date for "Joined" text (without time)
const formatJoinedDate = (dateStr) => {
    const date = parseISTDate(dateStr);
    if (!date) return 'Invalid Date';
    
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
};

function Profile() {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [isEditing, setIsEditing] = useState(false);
    const [avatarColors, setAvatarColors] = useState({});
    const [userInitials, setUserInitials] = useState('');
    const [editForm, setEditForm] = useState({
        fname: "",
        lname: "",
        email: "",
    });

    const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';
    
    // Get current theme
    const currentTheme = getCurrentTheme();

    // Load user data
    useEffect(() => {
        const loadUser = async () => {
            const storedUser = localStorage.getItem("user");
            const token = localStorage.getItem("token");

            if (!storedUser || !token) {
                navigate("/login");
                return;
            }

            try {
                const parsedUser = JSON.parse(storedUser);
                setUser(parsedUser);
                
                // Set initials using shared utility
                setUserInitials(getInitials(parsedUser.fname, parsedUser.lname));
                
                // Set avatar colors using shared utility (same as Navbar)
                const seed = parsedUser.id || parsedUser.email || 'user';
                setAvatarColors(getAvatarColors(seed, currentTheme));
                
                setEditForm({
                    fname: parsedUser.fname || "",
                    lname: parsedUser.lname || "",
                    email: parsedUser.email || "",
                });
                
                // Fetch fresh user data from backend
                const response = await axios.get(`${API_URL}/account/profile/`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                
                if (response.data.success) {
                    const freshUser = response.data.user;
                    setUser(freshUser);
                    setEditForm({
                        fname: freshUser.fname || "",
                        lname: freshUser.lname || "",
                        email: freshUser.email || "",
                    });
                    localStorage.setItem("user", JSON.stringify(freshUser));
                }
            } catch (err) {
                console.error("Error loading user:", err);
                setError("Failed to load profile data");
            } finally {
                setLoading(false);
            }
        };

        loadUser();
    }, [navigate, API_URL, currentTheme]);

    // Listen for theme changes to update avatar colors
    useEffect(() => {
        const handleThemeChange = () => {
            if (user) {
                const theme = getCurrentTheme();
                const seed = user.id || user.email || 'user';
                setAvatarColors(getAvatarColors(seed, theme));
            }
        };

        // Create a MutationObserver to watch for data-theme attribute changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-theme') {
                    handleThemeChange();
                }
            });
        });

        observer.observe(document.documentElement, { attributes: true });

        return () => observer.disconnect();
    }, [user]);

    // Handle edit form changes
    const handleEditChange = (e) => {
        setEditForm({
            ...editForm,
            [e.target.name]: e.target.value,
        });
    };

    // Save profile changes
    const handleSaveProfile = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const token = localStorage.getItem("token");
            const response = await axios.put(
                `${API_URL}/account/profile/update/`,
                editForm,
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            if (response.data.success) {
                const updatedUser = response.data.user;
                setUser(updatedUser);
                localStorage.setItem("user", JSON.stringify(updatedUser));
                setIsEditing(false);
                alert("Profile updated successfully!");
            }
        } catch (err) {
            setError(err.response?.data?.message || "Failed to update profile");
        } finally {
            setLoading(false);
        }
    };

    // Handle logout
    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        navigate("/login");
    };

    if (loading) {
        return (
            <MainLayout>
                <div className="profile-container">
                    <div className="profile-loading">
                        <div className="spinner"></div>
                        <p>Loading profile...</p>
                    </div>
                </div>
            </MainLayout>
        );
    }

    if (!user) {
        return (
            <MainLayout>
                <div className="profile-container">
                    <div className="profile-error">
                        <p>User not found. Please login again.</p>
                        <Link to="/login" className="profile-btn profile-btn-primary">
                            Go to Login
                        </Link>
                    </div>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <motion.div 
                className="profile-container"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <div className="profile-card">
                    {/* Cover Image */}
                    <div className="profile-cover">
                        <div className="profile-cover-gradient"></div>
                    </div>

                    {/* Avatar Section - Same colors as Navbar */}
                    <div className="profile-avatar-section">
                        <div 
                            className="profile-avatar-large"
                            style={{
                                backgroundColor: avatarColors.background,
                                color: avatarColors.text,
                                borderColor: avatarColors.border || avatarColors.background
                            }}
                        >
                            {userInitials || '?'}
                        </div>
                        <h1 className="profile-name">
                            {user.fname} {user.lname}
                        </h1>
                        <p className="profile-email">{user.email}</p>
                        {user.created_at && (
                            <p className="profile-joined">
                                Joined {formatJoinedDate(user.created_at)}
                            </p>
                        )}
                    </div>

                    {/* Profile Details */}
                    <div className="profile-details">
                        {!isEditing ? (
                            <>
                                <div className="profile-info-grid">
                                    <div className="profile-info-item">
                                        <label>First Name</label>
                                        <p>{user.fname}</p>
                                    </div>
                                    <div className="profile-info-item">
                                        <label>Last Name</label>
                                        <p>{user.lname}</p>
                                    </div>
                                    <div className="profile-info-item full-width">
                                        <label>Email Address</label>
                                        <p>{user.email}</p>
                                    </div>
                                    {user.created_at && (
                                        <div className="profile-info-item full-width">
                                            <label>Account Created</label>
                                            <p>{formatDisplayDate(user.created_at)}</p>
                                        </div>
                                    )}
                                </div>

                                <div className="profile-actions">
                                    <button 
                                        className="profile-btn profile-btn-primary"
                                        onClick={() => setIsEditing(true)}
                                    >
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                                        </svg>
                                        Edit Profile
                                    </button>
                                    <button 
                                        className="profile-btn profile-btn-danger"
                                        onClick={handleLogout}
                                    >
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                                            <polyline points="16 17 21 12 16 7" />
                                            <line x1="21" y1="12" x2="9" y2="12" />
                                        </svg>
                                        Logout
                                    </button>
                                </div>
                            </>
                        ) : (
                            <form onSubmit={handleSaveProfile} className="profile-edit-form">
                                <div className="profile-info-grid">
                                    <div className="profile-info-item">
                                        <label>First Name</label>
                                        <input
                                            type="text"
                                            name="fname"
                                            value={editForm.fname}
                                            onChange={handleEditChange}
                                            required
                                        />
                                    </div>
                                    <div className="profile-info-item">
                                        <label>Last Name</label>
                                        <input
                                            type="text"
                                            name="lname"
                                            value={editForm.lname}
                                            onChange={handleEditChange}
                                            required
                                        />
                                    </div>
                                    <div className="profile-info-item full-width">
                                        <label>Email Address</label>
                                        <input
                                            type="email"
                                            name="email"
                                            value={editForm.email}
                                            onChange={handleEditChange}
                                            required
                                        />
                                    </div>
                                </div>

                                {error && (
                                    <div className="profile-error-message">{error}</div>
                                )}

                                <div className="profile-actions">
                                    <button 
                                        type="submit" 
                                        className="profile-btn profile-btn-primary"
                                        disabled={loading}
                                    >
                                        {loading ? "Saving..." : "Save Changes"}
                                    </button>
                                    <button 
                                        type="button" 
                                        className="profile-btn profile-btn-secondary"
                                        onClick={() => {
                                            setIsEditing(false);
                                            setEditForm({
                                                fname: user.fname || "",
                                                lname: user.lname || "",
                                                email: user.email || "",
                                            });
                                            setError("");
                                        }}
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        )}
                    </div>
                </div>
            </motion.div>
        </MainLayout>
    );
}

export default Profile;