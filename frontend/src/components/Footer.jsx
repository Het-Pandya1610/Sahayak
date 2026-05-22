import React from 'react';

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
                        <li><a href="/schemes">All Schemes</a></li>
                        <li><a href="#">Chatbot Guide</a></li>
                        <li><a href="/faq">FAQ</a></li>
                        <li><a href="/resources">Official Sources</a></li>
                    </ul>
                </div>
                <div className="footer-col">
                    <h4>Support</h4>
                    <ul>
                        <li><a href="/contact">Contact Us</a></li>
                        <li><a href="#">Report Misinformation</a></li>
                        <li><a href="#">Feedback</a></li>
                        <li><a href="#">Privacy Policy</a></li>
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
                <a href="/terms" style={{ color: 'var(--white)', textDecoration: 'none' }}>Terms of Service</a> | <a href="/privacy" style={{ color: 'var(--white)', textDecoration: 'none' }}>Privacy Policy</a>
            </div>
        </footer>
    );
};

export default Footer;
