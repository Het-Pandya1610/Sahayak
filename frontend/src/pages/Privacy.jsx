import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

import './css/Privacy.css';

import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function Privacy() {
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
        <div className="privacy-page">
            <Navbar
                theme={theme}
                toggleTheme={toggleTheme}
            />
            <motion.div
                className="privacy-content"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
            >
                <h1>Privacy Policy</h1>
                <p style={{ textAlign: 'center', margin: 'auto' }}>
                    Your privacy is important to us. This privacy policy explains how we collect, use, and protect your personal information when you use our website.
                </p>
                <h2>1. Information We Collect</h2>
                <p>
                    We may collect personal information such as your name, email address, and any other information you voluntarily provide when you contact us or subscribe to our newsletter.
                </p>
                <h2>2. How We Use Your Information</h2>
                <p>
                    We use the information we collect to respond to your inquiries, send you updates and newsletters, and improve our website and services. We do not sell or share your personal information with third parties.
                </p>
                <h2>3. Data Security</h2>
                <p>
                    We take reasonable measures to protect your personal information from unauthorized access, disclosure, alteration, and destruction. However, no method of transmission over the internet or electronic storage is completely secure.
                </p>
                <h2>4. Changes to This Privacy Policy</h2>
                <p>
                    We may update this privacy policy from time to time. Any changes will be posted on this page, and we encourage you to review it periodically.
                </p>
                <h2>5. Contact Us</h2>
                <p>
                    If you have any questions about these terms and conditions, please contact us at
                    <a href="mailto:info@company.com" className='mailto'>info@company.com</a>.
                </p>
            </motion.div>
            <Footer theme={theme} />
        </div>
    );
}

export default Privacy;