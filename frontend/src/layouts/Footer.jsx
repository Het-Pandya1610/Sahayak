import React from 'react';
import {Link} from 'react-router-dom';

const Footer = ({ theme }) => {
    return (
        <footer className="footer" id="contact">
            <div className="footer-grid">
                <div className="footer-col">
                    <a className="footer-brand" href="/">
                        <img 
                            src={theme === 'dark' ? "/emblem_logo_dark.png" : "/emblem_logo.png"} 
                            alt="Sahayak Logo" 
                        />
                        <span>Sahayak</span>
                    </a>
                    <p style={{ fontSize: '0.85rem', color: 'var(--white)' }}>
                        Your trusted companion for navigating government schemes. Verified info, zero misinformation.
                    </p>
                </div>
                <div className="footer-col">
                    <h4>Quick Links</h4>
                    <ul>
                        <li><Link to="/schemes">All Schemes</Link></li>
                        <li><Link to="#">Chatbot Guide</Link></li>
                        <li><Link to="/faq">FAQ</Link></li>
                        <li><Link to="/resources">Official Sources</Link></li>
                    </ul>
                </div>
                <div className="footer-col">
                    <h4>Support</h4>
                    <ul>
                        <li><Link to="/contact">Contact Us</Link></li>
                        <li><Link to="/report-misinformation">Report Misinformation</Link></li>
                        <li><Link to="#">Feedback</Link></li>
                    </ul>
                </div>
                <div className="footer-col">
                    <h4>Disclaimer</h4>
                    <p style={{ fontSize: '0.8rem', color: 'var(--white)' }}>
                        We source data from official portals. Always verify before applying.
                    </p>
                </div>
            </div>
            <div className="footer-bottom">
                &copy; {new Date().getFullYear()} Sahayak. All rights reserved.<br />
                Developed by Team Sahayak.<br />
                <Link to="/terms" style={{ color: 'var(--white)', textDecoration: 'none' }}>Terms of Service</Link> | <Link to="/privacy" style={{ color: 'var(--white)', textDecoration: 'none' }}>Privacy Policy</Link>
            </div>
        </footer>
    );
};

export default Footer;
