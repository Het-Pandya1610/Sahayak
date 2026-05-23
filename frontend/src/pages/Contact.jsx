import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

import './css/Contact.css';
import MainLayout from '../layouts/MainLayout';

function Contact() {

    return (
        <div className="contact-page">
            <MainLayout>
                <motion.div
                className="contact-content"
                initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                >
                <h1>Contact Us</h1>
                <p className="contact-description">
                    We would love to hear from you! Whether you have questions, feedback, or just want to say hello, feel free to reach out to us using the form below.
                </p>
                <form className="contact-form">
                    <label htmlFor="name">Name</label>
                    <input type="text" id="name" name="name" placeholder="Your name.." required />
                    <label htmlFor="email">Email</label>
                    <input type="email" id="email" name="email" placeholder="Your email.." required />
                        <label htmlFor="message">Message</label>
                        <textarea id="message" name="message" placeholder="Write something.." required></textarea>
                        <button type="submit">Submit</button>
                </form>
                <p className="contact-info">
                    You can also reach us at: <a href="mailto:info@sahayak.org">info@sahayak.org</a>
                </p>
                </motion.div>
            </MainLayout>
        </div>
    );
}

export default Contact;