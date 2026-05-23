import { motion } from 'framer-motion';
import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

import './css/NotFound.css';

// Add navbar and footer with themes
 
import MainLayout from '../layouts/MainLayout';

function NotFound() {

    return (
        <div className="notfound-page">
            <MainLayout>
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
            </MainLayout>
        </div>
    );
}

export default NotFound;