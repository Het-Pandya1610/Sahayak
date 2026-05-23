import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

import './css/FAQ.css';
import MainLayout from '../layouts/MainLayout';

function FAQ() {
    const [activeIndex, setActiveIndex] = useState(null);

    const toggleFAQ = (index) => {
        setActiveIndex(activeIndex === index ? null : index);
    };

    const faqs = [
        {
            question: "What is Sahayak?",
            answer:
                "Sahayak is a platform that helps users navigate and understand various government schemes in India. We provide verified information to ensure you can access the benefits you deserve without any misinformation."
        },
        {
            question: "How do I use the chatbot?",
            answer:
                "Our chatbot is designed to answer your queries about government schemes. Simply click on the chatbot icon, type your question, and it will provide you with accurate information sourced from official portals."
        },
        {
            question: "Where do you get your information from?",
            answer:
                "We source our data from official government portals and trusted sources. We are committed to providing accurate and up-to-date information to our users."
        },
        {
            question: "Is Sahayak free to use?",
            answer:
                "Yes, Sahayak is completely free to use. Our mission is to empower citizens with information, and we do not charge any fees for accessing our platform."
        }
    ];

    return (
        <div className="faq-page">
            <MainLayout>
                <motion.div
                    className="faq-content"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                >
                    <h1>Frequently Asked Questions</h1>

                    <p className="faq-description">
                        Here are some common questions about Sahayak. 
                        If you have more, feel free to <a href="/contact">contact us</a>!
                    </p>

                    <div className="faq-container">
                        {faqs.map((faq, index) => (
                            <motion.div
                                key={index}
                                className={`faq-item ${activeIndex === index ? 'open' : ''}`}
                                layout
                                transition={{ duration: 0.3 }}
                            >
                                <div
                                    className="faq-question"
                                    onClick={() => toggleFAQ(index)}
                                >
                                    <h3>{faq.question}</h3>

                                    <motion.i
                                        className="fas fa-chevron-down"
                                        animate={{
                                            rotate: activeIndex === index ? 180 : 0
                                        }}
                                        transition={{ duration: 0.3 }}
                                    />
                                </div>

                                <AnimatePresence initial={false}>
                                    {activeIndex === index && (
                                        <motion.div
                                            className="faq-answer"
                                            initial={{ height: 0, opacity: 0 }}
                                            animate={{ height: 'auto', opacity: 1 }}
                                            exit={{ height: 0, opacity: 0 }}
                                            transition={{
                                                duration: 0.35,
                                                ease: 'easeInOut'
                                            }}
                                        >
                                            <p>{faq.answer}</p>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </motion.div>
                        ))}
                    </div>
                </motion.div>
            </MainLayout>
        </div>
    );
}

export default FAQ;