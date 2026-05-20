import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

import './About.css';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function About() {
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
        <div className="about-page">
            <Navbar 
                theme={theme}
                toggleTheme={toggleTheme}
            />
            <motion.div
            className="about-content"
            initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
            >
            <h1>About Sahayak</h1>
                <p className="about-description">Sahayak is a government scheme chatbot designed to help citizens easily access information about various government initiatives and schemes. Our mission is to empower individuals with accurate and up-to-date information, enabling them to take advantage of the benefits offered by the government.</p>
                <p className="about-description">With Sahayak, you can quickly find details about eligibility criteria, application processes, and benefits of different government schemes. Whether you're looking for financial assistance programs, social welfare initiatives, or educational schemes, Sahayak is here to assist you every step of the way.</p>
                <p className="about-description">Our chatbot is built using advanced natural language processing techniques, ensuring that you receive accurate and relevant information in a user-friendly manner. We are committed to making government schemes more accessible and understandable for everyone.</p>
                <p className="about-description">Sahayak Chatbot streamlines the complaint registration process by utilizing advanced AI-powered image detection technology to identify civic issues such as potholes, damaged infrastructure, waste accumulation, and other public concerns. The system automatically analyzes uploaded images, categorizes the issue, and generates professionally formatted complaint reports and emails that are directly forwarded to the appropriate nearby government department or responsible authority, enabling faster response times and more efficient issue resolution.</p>
                <p className="about-description">At Sahayak, we believe that informed citizens are empowered citizens. Our goal is to bridge the gap between the government and the public by providing a reliable and efficient platform for accessing information about government schemes. We are continuously working to improve our chatbot and expand our database to cover more schemes and initiatives.</p>
                <p className="about-description">Thank you for choosing Sahayak as your go-to resource for government scheme information. We are dedicated to helping you navigate the world of government initiatives and make the most of the opportunities available to you.</p>
            </motion.div>
            <Footer theme={theme}/>
        </div>
    );
};

export default About;