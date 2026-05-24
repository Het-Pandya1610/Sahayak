import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

import './css/Report_Mis.css';

import MainLayout from '../layouts/MainLayout';

function Report_Mis() {

    return (
        <div className="report-miss-page">
            <MainLayout>
                <motion.div
                    className="report-miss-content"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
            >
                <h1>Report Missinformation</h1>
                <p style={{ textAlign: 'center', margin: 'auto' }}>
                    If you come across any misinformation on our website, please report it to us using the form below. We take all reports seriously and will investigate them promptly.
                </p>
                <form className="report-form">
                    <label htmlFor="url">URL of the Misinformation:</label>
                    <input type="text" id="url" name="url" placeholder="Enter the URL where you found the misinformation" required />
                    <label htmlFor="description">Description of the Misinformation:</label>
                    <textarea id="description" name="description" placeholder="Provide a detailed description of the misinformation you found" required></textarea>
                    <button type="submit">Submit Report</button>
                </form>
            </motion.div>
            </MainLayout>
        </div>
    );
}

export default Report_Mis;