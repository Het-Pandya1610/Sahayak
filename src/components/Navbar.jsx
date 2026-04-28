import React, { useState, useEffect } from 'react';

const Navbar = () => {
    const [scrolled, setScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 10);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const toggleMobileMenu = () => setMobileMenuOpen(!mobileMenuOpen);

    return (
        <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
            <a href="#" className="nav-brand">
                <div className="logo-icon">
                    <img src="/emblem_logo.png" alt="Sahayak Logo" />
                </div>
                Sahayak
            </a>

            <ul className={`nav-links ${mobileMenuOpen ? 'open' : ''}`}>
                <li><a href="#schemes" onClick={() => setMobileMenuOpen(false)}>Schemes</a></li>
                <li><a href="#how-it-works" onClick={() => setMobileMenuOpen(false)}>How It Works</a></li>
                <li><a href="#about" onClick={() => setMobileMenuOpen(false)}>About</a></li>
                <li><a href="#contact" onClick={() => setMobileMenuOpen(false)}>Contact</a></li>
                <li>
                    <a href="#" className="nav-cta" onClick={() => setMobileMenuOpen(false)}>
                        <i className="fas fa-search"></i> Explore Schemes
                    </a>
                </li>
            </ul>

            <button 
                className={`hamburger ${mobileMenuOpen ? 'active' : ''}`} 
                onClick={toggleMobileMenu}
                aria-label="Menu"
            >
                <span></span><span></span><span></span>
            </button>
        </nav>
    );
};

export default Navbar;
