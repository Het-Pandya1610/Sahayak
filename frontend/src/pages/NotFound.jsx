import { motion } from 'framer-motion';
import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

import './css/NotFound.css';

// Add navbar and footer with themes

import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function NotFound() {
    const [theme, setTheme] = useState(
        () => localStorage.getItem('theme') || 'light'
    );
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
    };

    return (
        <div className="notfound-page">
            <Navbar 
                theme={theme}
                toggleTheme={toggleTheme}
            />
            <motion.div
                className="notfound-content"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
            >
                <img className='ills' src="../../../../404-illustration.png" alt="404 Illustration" />
                <h1>404</h1>

                <h2>Page Not Found</h2>

                <p>
                    The page you are looking for does not exist
                    or may have been moved.
                </p>

                <Link to="/" className="home-btn">
                    Go Back Home
                </Link>

            </motion.div>
            <Footer theme={theme}/>
        </div>
    );
}

export default NotFound;