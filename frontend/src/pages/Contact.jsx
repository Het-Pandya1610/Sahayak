import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

import './Contact.css';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function Contact() {
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
        <div className="contact-page">
            <Navbar
                theme={theme}
                toggleTheme={toggleTheme}
            />
            <motion.div
            className="contact-content"
            initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
            >
            <h1>Contact Us</h1>
                <p className="contact-description">If you have any questions, feedback, or inquiries about Sahayak, please feel free to reach out to us. We value your input and are here to assist you in any way we can.</p>
                <p className="contact-description">You can contact us through the following channels:</p>
                <ul className="contact-list">
                    <li><strong>Email:</strong> <a href="mailto:info@sahayak.org">info@sahayak.org</a></li>
                    <li><strong>Phone:</strong> <a href="tel:+91-11-23456789">+91-11-23456789</a></li>
                    <li><strong>Address:</strong> 123 Main Street, Anytown, USA</li>
                </ul>
                <p className="contact-description">We also encourage you to connect with us on our social media platforms for updates, news, and more information about Sahayak:</p>
                <ul className="social-media-list">
                    <li><a href="https://www.facebook.com/sahayak" target="_blank" rel="noopener noreferrer"><i class="fab fa-facebook-f"></i></a></li>
                    <li><a href="https://www.twitter.com/sahayak" target="_blank" rel="noopener noreferrer"><i class="fab fa-twitter"></i></a></li>
                    <li><a href="https://www.linkedin.com/company/sahayak" target="_blank" rel="noopener noreferrer"><i class="fab fa-linkedin-in"></i></a></li>
                    <li><a href="https://www.instagram.com/sahayak" target="_blank" rel="noopener noreferrer"><i class="fab fa-instagram"></i></a></li>
                </ul>
                <p className="contact-description">For media inquiries, partnership opportunities, or any other specific requests, please use the contact information provided above, and we will get back to you as soon as possible.</p>
                <p className="contact-description">Thank you for your interest in Sahayak. We look forward to hearing from you and assisting you with any questions or concerns you may have about our services.</p>
                <p className="contact-description">Your feedback is invaluable to us as we strive to improve our chatbot and provide the best experience for our users. Please don't hesitate to reach out to us with your thoughts and suggestions.</p>
                <p className="contact-description">We are committed to providing excellent customer support and ensuring that your experience with Sahayak is positive and helpful. Whether you have a question about how to use the chatbot, need assistance with a specific issue, or simply want to share your thoughts, we are here to listen and assist you.</p>
                <p className="contact-description">We look forward to hearing from you and assisting you with any questions or concerns you may have about Sahayak. Your feedback is invaluable to us as we strive to improve our services and provide the best experience for our users.</p>
            </motion.div>
            <Footer theme={theme}/>
        </div>
    );
}

export default Contact;