import React from 'react';
import { motion } from 'framer-motion';

const Hero = ({ onSearch, showContent }) => {
    const handleSearch = (e) => {
        if (e.key === 'Enter' || e.type === 'click') {
            const input = document.getElementById('heroSearchInput');
            if (input.value.trim()) {
                onSearch(input.value.trim());
            }
        }
    };

    return (
        <section className="hero">
            <div className="hero-container">
                <motion.div 
                    className="hero-text"
                    initial={{ opacity: 0, x: -100 }}
                    animate={showContent ? { opacity: 1, x: 0 } : { opacity: 0, x: -100 }}
                    transition={{ duration: 0.8, delay: 0.5 }}
                >
                    <div className="hero-badge">
                        <span className="dot"></span> Officially Verified Information
                    </div>
                    <h1>Find Every Government Scheme in One Place</h1>
                    <p>Stop misinformation. Our AI chatbot provides accurate, verified scheme details — in simple language.</p>
                    
                    <div className="hero-search">
                        <input 
                            type="text" 
                            placeholder="e.g., housing, farmer benefits..." 
                            id="heroSearchInput"
                            onKeyPress={handleSearch}
                        />
                        <button onClick={handleSearch} className="search-btn">
                            <i className="fas fa-search"></i> Search
                        </button>
                    </div>

                    <div className="hero-stats">
                        <div className="hero-stat">
                            <span className="stat-number"><i className="fas fa-check-circle"></i> 200+</span>
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
                    </div>
                </motion.div>

                <motion.div 
                    className="hero-illustration"
                    initial={{ opacity: 0, x: 100 }}
                    animate={showContent ? { opacity: 1, x: 0 } : { opacity: 0, x: 100 }}
                    transition={{ duration: 0.8, delay: 0.7 }}
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
                        <circle cx="380" cy="280" r="28" fill="#C2A56D" />
                        <path d="M368 280 L378 290 L395 270" stroke="white" strokeWidth="4.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </motion.div>
            </div>
        </section>
    );
};

export default Hero;
