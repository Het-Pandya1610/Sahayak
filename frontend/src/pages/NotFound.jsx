import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

import './NotFound.css';

function NotFound() {
    return (
        <div className="notfound-page">

            <motion.div
                className="notfound-content"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
            >
                <img className='ills' src="..\public\404-illustration.png" alt="404 Illustration" />
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

        </div>
    );
}

export default NotFound;