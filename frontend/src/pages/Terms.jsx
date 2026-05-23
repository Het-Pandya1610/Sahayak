import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

import './css/Terms.css';

import MainLayout from '../layouts/MainLayout';

function Terms() {

    return (
        <div className="terms-page">
            <MainLayout>
            <motion.div
                    className="terms-content"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
            >
                <h1>Terms and Conditions</h1>
                <p style={{ textAlign: 'center', margin: 'auto' }}>
                    Welcome to our website. By accessing or using our services, you agree to be bound by the following terms and conditions. Please read them carefully before using our website.
                </p>
                <h2>1. Acceptance of Terms</h2>
                <p>
                    By using our website, you agree to comply with and be bound by these terms and conditions. If you do not agree to these terms, please do not use our website.
                </p>
                <h2>2. Use of the Website</h2>
                <p>
                    You agree to use our website only for lawful purposes and in a way that does not infringe the rights of others or restrict their use and enjoyment of the website.
                </p>
                <h2>3. Intellectual Property</h2>
                <p>
                    All content on our website, including text, graphics, logos, and images, is the property of our company and is protected by intellectual property laws. You may not use any content from our website without our express written permission.
                </p>
                <h2>4. Limitation of Liability</h2>
                <p>
                    We are not liable for any damages arising out of or in connection with your use of our website. This includes, but is not limited to, direct, indirect, incidental, punitive, and consequential damages.
                </p>
                <h2>5. Changes to Terms</h2>
                <p>
                    We reserve the right to modify these terms and conditions at any time. Any changes will be effective immediately upon posting on our website. Your continued use of the website after any changes constitutes your acceptance of the new terms.
                </p>
                <h2>6. Contact Us</h2>
                <p>
                    If you have any questions about these terms and conditions, please contact us at
                    <a href="mailto:info@company.com" className='mailto'>info@company.com</a>.
                </p>
            </motion.div>
            </MainLayout>
        </div>
    );
}

export default Terms;