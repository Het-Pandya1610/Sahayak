import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const Navbar = ({ theme, toggleTheme }) => {
    const [scrolled, setScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen);
    const closeMobileMenu = () => setMobileMenuOpen(false);

    return (
        <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
            <a href="/" className="nav-brand">
                <div className="logo-icon">
                    <img 
                        src={theme === 'dark' ? "/emblem_logo_dark.png" : "/emblem_logo.png"} 
                        alt="Sahayak Logo" 
                    />
                </div>
                <span>Sahayak</span>
            </a>

            {/* Desktop Links */}
            <ul className="nav-links desktop-only">
                <li><a href="/schemes">Schemes</a></li>
                <li><a href="/#how-it-works">How It Works</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/#contact">Contact</a></li>
                <li>
                    <a href="/schemes" className="nav-cta">
                        <i className="fas fa-search" style={{ marginRight: '8px' }}></i> Explore
                    </a>
                </li>
            </ul>

            <div className="nav-actions">
                <button className="tbtn" id="themeBtn" aria-label="Toggle theme" onClick={toggleTheme}>
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={theme}
                            initial={{ y: 10, opacity: 0, rotate: -45 }}
                            animate={{ y: 0, opacity: 1, rotate: 0 }}
                            exit={{ y: -10, opacity: 0, rotate: 45 }}
                            transition={{ duration: 0.2 }}
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

                <button 
                    className={`hamburger ${mobileMenuOpen ? 'active' : ''}`} 
                    onClick={toggleMobileMenu}
                    aria-label="Toggle Menu"
                >
                    <span></span><span></span><span></span>
                </button>
            </div>

            {/* Mobile Menu */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div 
                        className="mobile-menu"
                        initial={{ x: '100%' }}
                        animate={{ x: 0 }}
                        exit={{ x: '100%' }}
                        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                    >
                        <ul className="mobile-nav-links">
                            <li><a href="/schemes" onClick={closeMobileMenu}>Schemes</a></li>
                            <li><a href="/#how-it-works" onClick={closeMobileMenu}>How It Works</a></li>
                            <li><a href="/about" onClick={closeMobileMenu}>About</a></li>
                            <li><a href="/#contact" onClick={closeMobileMenu}>Contact</a></li>
                            <li>
                                <a href="/schemes" className="nav-cta" onClick={closeMobileMenu}>
                                    Explore Schemes
                                </a>
                            </li>
                        </ul>
                    </motion.div>
                )}
            </AnimatePresence>
        </nav>
    );
};

export default Navbar;
