import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

import './Schemes.css';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

function Schemes() {
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
        <div className="schemes-page">
            <Navbar
                theme={theme}
                toggleTheme={toggleTheme}
            />
            <motion.div
            className="schemes-content"
            initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
            >
            <h1>Government Schemes</h1>
                <p className="schemes-description">Explore various government schemes and initiatives designed to support citizens in different sectors. From financial assistance programs to social welfare schemes, find out how you can benefit from these initiatives.</p>
                <ul className="schemes-list">
                    <li><strong>Pradhan Mantri Jan Dhan Yojana:</strong> A financial inclusion program aimed at providing banking services to the unbanked population.</li>
                    <li><strong>Atal Pension Yojana:</strong> A pension scheme for workers in the unorganized sector to ensure financial security in old age.</li>
                    <li><strong>Swachh Bharat Abhiyan:</strong> A cleanliness campaign aimed at improving sanitation and hygiene across the country.</li>
                    <li><strong>Make in India:</strong> An initiative to encourage manufacturing in India and boost economic growth.</li>
                    <li><strong>Digital India:</strong> A campaign to transform India into a digitally empowered society and knowledge economy.</li>
                </ul>
            </motion.div>
            <Footer theme={theme}/>
        </div>
    );
}

export default Schemes;