import React from 'react';

const steps = [
    {
        title: "Ask Your Question",
        desc: "Type in simple language — like 'I need a housing scheme'.",
        icon: "fa-question-circle",
        delay: 0
    },
    {
        title: "Get Verified Info",
        desc: "AI fetches accurate details from official databases.",
        icon: "fa-database",
        delay: 150
    },
    {
        title: "Apply Confidently",
        desc: "Step-by-step guidance to official portals only.",
        icon: "fa-check-double",
        delay: 300
    }
];

const HowItWorks = () => {
    return (
        <section className="section how-it-works" id="how-it-works">
            <div className="section-header" data-aos="fade-up">
                <span className="tag">Simple Process</span>
                <h2>How Our Chatbot Helps You</h2>
                <p>No complex forms. No misinformation. Straightforward guidance.</p>
            </div>
            <div className="steps-container">
                {steps.map((step, idx) => (
                    <div key={idx} className="step" data-aos="fade-up" data-aos-delay={step.delay}>
                        <div className="step-icon"><i className={`fas ${step.icon}`}></i></div>
                        <h4>{step.title}</h4>
                        <p>{step.desc}</p>
                    </div>
                ))}
            </div>
        </section>
    );
};

export default HowItWorks;
