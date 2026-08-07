import React, { useState } from 'react';
import { motion } from 'framer-motion';

const Hero = ({ onSearch, showContent }) => {
    const [inputValue, setInputValue] = useState('');

    const handleSearch = (e) => {
        if (e.key === 'Enter' || e.type === 'click') {
            if (inputValue.trim()) {
                // Navigate to schemes page with search query
                navigate(`/schemes?search=${encodeURIComponent(inputValue.trim())}`);
                
                // Also call the onSearch callback if provided
                if (onSearch) {
                    onSearch(inputValue.trim());
                }
            }
        }
    };

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.15,
                delayChildren: 0.4
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 30 },
        visible: { 
            opacity: 1, 
            y: 0,
            transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] }
        }
    };

    return (
        <section className="hero">
            <div className="hero-container">
                <motion.div 
                    className="hero-text"
                    variants={containerVariants}
                    initial="hidden"
                    animate={showContent ? "visible" : "hidden"}
                >
                    
                    <motion.h1 variants={itemVariants}>
                        Find Every Government <span className="highlight">Scheme</span> in One Place
                    </motion.h1>
                    
                    <motion.p variants={itemVariants}>
                        Stop misinformation. Our AI chatbot provides accurate, verified scheme details — in simple language.
                    </motion.p>
                    
                    {/* <motion.div className="hero-search" variants={itemVariants}>
                        <input 
                            type="text" 
                            placeholder="e.g., housing, farmer benefits..." 
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleSearch}
                        />
                        <button onClick={handleSearch} className="search-btn">
                            <i className="fas fa-search"></i> Search
                        </button>
                    </motion.div> */}

                    <motion.div className="hero-stats" variants={itemVariants}>
                        <div className="hero-stat">
                            <span className="stat-number"><i className="fas fa-check-circle"></i> 3000+</span>
                            <span className="stat-label">Active Schemes</span>
                        </div>
                        <div className="hero-stat">
                            <span className="stat-number"><i className="fas fa-users"></i> 50M+</span>
                            <span className="stat-label">Beneficiaries</span>
                        </div>
                        <div className="hero-stat">
                            <span className="stat-number"><i className="fas fa-headset"></i> 24/7</span>
                            <span className="stat-label">AI Assistance</span>
                        </div>
                    </motion.div>
                </motion.div>

                <motion.div 
                    className="hero-illustration"
                    initial={{ opacity: 0, x: 40, scale: 0.9 }}
                    animate={showContent ? { opacity: 1, x: 0, scale: 1 } : { opacity: 0, x: 40, scale: 0.9 }}
                    transition={{ duration: 1, delay: 0.8, ease: [0.16, 1, 0.3, 1] }}
                >
                    <svg viewBox="0 0 520 400" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <defs>
                            <filter id="shadow" x="0" y="0" width="520" height="400">
                                <feDropShadow dx="0" dy="8" stdDeviation="10" floodColor="#000" floodOpacity="0.08" />
                            </filter>
                        </defs>
                        <rect x="150" y="70" width="300" height="260" rx="16" fill="white" stroke="#E2E8F0" filter="url(#shadow)" />
                        <rect x="170" y="95" width="140" height="14" rx="7" fill="#CBD5E1" />
                        <rect x="170" y="120" width="90" height="10" rx="5" fill="#E2E8F0" />
                        <rect x="170" y="150" width="240" height="10" rx="5" fill="#E2E8F0" />
                        <rect x="170" y="168" width="220" height="10" rx="5" fill="#E2E8F0" />
                        <rect x="170" y="186" width="250" height="10" rx="5" fill="#E2E8F0" />
                        <rect x="170" y="204" width="200" height="10" rx="5" fill="#E2E8F0" />
                        <rect x="170" y="235" width="120" height="12" rx="6" fill="#CBD5E1" />
                        <circle cx="380" cy="280" r="28" fill="var(--secondary)" />
                        <path d="M368 280 L378 290 L395 270" stroke="white" strokeWidth="4.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </motion.div>
            </div>
        </section>
    );
};

export default Hero;
