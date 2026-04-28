import React, { useState, useEffect, useRef } from 'react';

const Chatbot = ({ isOpen, onClose, initialQuery }) => {
    const [messages, setMessages] = useState([
        {
            type: 'bot',
            text: "Hello! I'm your trusted AI guide. Ask me about any government scheme — I'll provide accurate, verified details.",
            chips: ['Housing', 'Farmer', 'Health', 'Education']
        }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    useEffect(() => {
        if (initialQuery && isOpen) {
            handleSendMessage(initialQuery);
        }
    }, [initialQuery, isOpen]);

    const getBotResponse = (msg) => {
        const m = msg.toLowerCase();
        if (m.includes('housing') || m.includes('home') || m.includes('awas'))
            return { text: `<strong>PM Awas Yojana</strong>: Subsidy up to ₹2.67 lakh (Urban) or ₹1.20 lakh (Gramin). Eligibility based on income.`, chips: ['Check eligibility', 'How to apply', 'Documents'] };
        if (m.includes('farmer') || m.includes('kisan') || m.includes('crop'))
            return { text: `<strong>PM Kisan Samman Nidhi</strong>: ₹6,000/year. Other schemes: PM Fasal Bima, Kisan Credit Card.`, chips: ['PM Kisan details', 'Crop insurance', 'Farm loans'] };
        if (m.includes('health') || m.includes('medical') || m.includes('ayushman'))
            return { text: `<strong>Ayushman Bharat PM-JAY</strong>: ₹5 lakh cover, cashless, 1900+ procedures.`, chips: ['Check eligibility', 'Find hospitals', 'Coverage'] };
        if (m.includes('education') || m.includes('student') || m.includes('scholarship'))
            return { text: `Education schemes: National Scholarship, Vidya Lakshmi loan, PM Vidyalaxmi (up to ₹10 lakh).`, chips: ['School', 'College', 'Study abroad'] };
        if (m.includes('women') || m.includes('girl') || m.includes('ladies'))
            return { text: `Key schemes: Beti Bachao Beti Padhao, PM Ujjwala, Mahila Samman Savings.`, chips: ['LPG connection', 'Girl education', 'Savings'] };
        if (m.includes('business') || m.includes('startup') || m.includes('msme'))
            return { text: `Startup India, MUDRA loans (up to ₹10L), Stand-Up India for SC/ST & women.`, chips: ['Startup registration', 'MUDRA loan', 'Tax benefits'] };
        return { text: `I cover 200+ schemes. Tell me what you're looking for — housing, health, farming, education, business, or women's welfare?`, chips: ['Housing', 'Healthcare', 'Farming', 'Education', 'Business', 'Women'] };
    };

    const handleSendMessage = (text) => {
        const query = text || input.trim();
        if (!query) return;

        setMessages(prev => [...prev, { type: 'user', text: query }]);
        setInput('');
        setIsTyping(true);

        setTimeout(() => {
            setIsTyping(false);
            const resp = getBotResponse(query);
            setMessages(prev => [...prev, { type: 'bot', ...resp }]);
        }, 1000 + Math.random() * 500);
    };

    if (!isOpen) return (
        <div className="chatbot-widget">
            <button className="chatbot-toggle" onClick={() => onClose(false)}>
                <i className="fas fa-robot"></i>
                <span className="pulse-ring"></span>
            </button>
        </div>
    );

    return (
        <div className="chatbot-panel-container">
            <div className="chatbot-panel open">
                <div className="chatbot-header">
                    <div className="chatbot-header-left">
                        <div className="chatbot-avatar"><i className="fas fa-robot"></i></div>
                        <div>
                            <h3>Sahayak AI</h3>
                            <span className="status"><span className="status-dot"></span> Online · Verified Info</span>
                        </div>
                    </div>
                    <button className="chatbot-close" onClick={() => onClose(true)}><i className="fas fa-times"></i></button>
                </div>

                <div className="chatbot-messages">
                    {messages.map((msg, i) => (
                        <div key={i} className={`msg ${msg.type}`}>
                            {msg.type === 'bot' && <i className="fas fa-hand-sparkles" style={{ marginRight: '8px' }}></i>}
                            <span dangerouslySetInnerHTML={{ __html: msg.text }}></span>
                            {msg.chips && (
                                <div className="suggestion-chips">
                                    {msg.chips.map((chip, j) => (
                                        <span key={j} className="chip" onClick={() => handleSendMessage(chip)}>{chip}</span>
                                    ))}
                                </div>
                            )}
                        </div>
                    ))}
                    {isTyping && (
                        <div className="typing-indicator">
                            <span></span><span></span><span></span>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <div className="chatbot-input-area">
                    <input 
                        type="text" 
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your query..." 
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    />
                    <button onClick={() => handleSendMessage()}><i className="fas fa-paper-plane"></i></button>
                </div>
            </div>
        </div>
    );
};

export default Chatbot;
