import React from 'react';

const CTABanner = ({ onOpenChatbot }) => {
    return (
        <section className="section" id="about">
            <div className="cta-banner" data-aos="fade-up">
                <h2>Don't Rely on Rumors. Get the Facts.</h2>
                <p>Our chatbot is trained on verified government data to protect you from fake news and fraud.</p>
                <button className="btn-white" onClick={onOpenChatbot}>
                    <i className="fas fa-comment-dots"></i> Start Chatting Now
                </button>
            </div>
        </section>
    );
};

export default CTABanner;
