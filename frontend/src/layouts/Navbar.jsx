import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { NavLink } from 'react-router-dom';
import { getAvatarColors, getInitials, getCurrentTheme } from '../utils/avatarUtils';

const Navbar = ({ theme, toggleTheme }) => {
    const navigate = useNavigate();
    const [scrolled, setScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState(null);
    const [userInitials, setUserInitials] = useState('');
    const [avatarColors, setAvatarColors] = useState({});

    // Check authentication status on mount and when localStorage changes
    useEffect(() => {
        const checkAuth = () => {
            const token = localStorage.getItem('token');
            const userData = localStorage.getItem('user');
            
            if (token && userData) {
                try {
                    const parsedUser = JSON.parse(userData);
                    setUser(parsedUser);
                    setIsAuthenticated(true);
                    
                    // Generate initials using shared utility
                    const initials = getInitials(parsedUser.fname, parsedUser.lname);
                    setUserInitials(initials);
                    
                    // Generate theme-aware colors using shared utility
                    const seed = parsedUser.id || parsedUser.email || 'user';
                    setAvatarColors(getAvatarColors(seed, theme));
                } catch (error) {
                    console.error('Error parsing user data:', error);
                    setIsAuthenticated(false);
                }
            } else {
                setIsAuthenticated(false);
                setUser(null);
            }
        };

        checkAuth();
    }, [theme]); // Re-run when theme changes

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setIsAuthenticated(false);
        setUser(null);
        navigate('/');
    };

    const handleScroll = () => {
        setScrolled(window.scrollY > 20);
    };

    useEffect(() => {
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen);
    const closeMobileMenu = () => setMobileMenuOpen(false);

    return (
        <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
            <NavLink to="/" className="nav-brand">
                <div className="logo-icon">
                    <img 
                        src={theme === 'dark' ? "/emblem_logo_dark.png" : "/emblem_logo.png"} 
                        alt="Sahayak Logo" 
                    />
                </div>
                <span>Sahayak</span>
            </NavLink>

            {/* Desktop Links */}
            <ul className="nav-links desktop-only">
                <li><NavLink to="/schemes" className={({ isActive }) => isActive ? 'active' : ''}>Schemes</NavLink></li>
                <li><NavLink to="/chatbot" className={({ isActive }) => isActive ? 'active' : ''}>Chatbot</NavLink></li>
                <li><NavLink to="/about" className={({ isActive }) => isActive ? 'active' : ''}>About</NavLink></li>
                <li><NavLink to="/contact" className={({ isActive }) => isActive ? 'active' : ''}>Contact</NavLink></li>
                <li>
                    <Link to="/schemes" className="nav-cta">
                        <i className="fas fa-search" style={{ marginRight: '8px' }}></i> Explore
                    </Link>
                </li>
            </ul>

            <div className="nav-actions">
                <button className="tbtn" id="themeBtn" aria-label="Toggle theme" onClick={toggleTheme}>
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={theme}
                            initial={{ y: 0, opacity: 1, rotate: 0 }}
                            animate={{ y: 0, opacity: 1, rotate: 0 }}
                            exit={{ y: -10, opacity: 0, rotate: 45 }}
                            transition={{ duration: 0.5 }}
                        >
                            {theme === 'dark' ? (
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                                </svg>
                            ) : (
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                    <circle cx="12" cy="12" r="5" />
                                    <line x1="12" y1="1" x2="12" y2="3" />
                                    <line x1="12" y1="21" x2="12" y2="23" />
                                    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                                    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                                    <line x1="1" y1="12" x2="3" y2="12" />
                                    <line x1="21" y1="12" x2="23" y2="12" />
                                    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                                    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                                </svg>
                            )}
                        </motion.div>
                    </AnimatePresence>
                </button>
                
                {!isAuthenticated ? (
                    <>
                        <Link
                            to="/register"
                            className="register-btn"
                        >
                            Register
                        </Link>
                        <Link
                            to="/login"
                            className="login-btn"
                        >
                            Log In
                        </Link>
                    </>
                ) : (
                    <div className="authenticated-actions">
                        <Link to="/profile" className="profile-link">
                            <div 
                                className="profile-avatar"
                                style={{
                                    backgroundColor: avatarColors.background,
                                    color: avatarColors.text,
                                    borderColor: avatarColors.border || avatarColors.background
                                }}
                                data-fullname={`${user?.fname || ''} ${user?.lname || ''}`.trim() || 'User'}
                            >
                                {userInitials || 'U'}
                            </div>
                        </Link>
                        <button
                            className="logout-btn"
                            onClick={handleLogout}
                        >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                                <polyline points="16 17 21 12 16 7" />
                                <line x1="21" y1="12" x2="9" y2="12" />
                            </svg>
                            Logout
                        </button>
                    </div>
                )}
                
                <button 
                    className={`hamburger ${mobileMenuOpen ? 'active' : ''}`} 
                    onClick={toggleMobileMenu}
                    aria-label="Toggle Menu"
                >
                    <span></span><span></span><span></span>
                </button>
            </div>

            {/* Mobile Menu Overlay */}
            <div 
                className={`mobile-overlay ${mobileMenuOpen ? 'open' : ''}`} 
                onClick={closeMobileMenu}
            ></div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div 
                        className="mobile-menu open"
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
                    >
                        <ul className="mobile-nav-links">
                            <li><Link to="/schemes" onClick={closeMobileMenu}>Schemes</Link></li>
                            <li><Link to="/chatbot" onClick={closeMobileMenu}>Chatbot</Link></li>
                            <li><Link to="/about" onClick={closeMobileMenu}>About</Link></li>
                            <li><Link to="/contact" onClick={closeMobileMenu}>Contact</Link></li>
                            <li>
                                <Link to="/schemes" className="nav-cta" onClick={closeMobileMenu}>
                                    Explore Schemes
                                </Link>
                            </li>
                        </ul>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
};

export default Navbar;