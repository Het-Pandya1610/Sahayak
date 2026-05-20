import React from 'react';

const schemes = [
    {
        title: "PM Kisan Samman Nidhi",
        desc: "₹6,000/year direct income support for eligible farmer families.",
        badge: "Farmers",
        icon: "fa-seedling",
        color: "green"
    },
    {
        title: "Ayushman Bharat PM-JAY",
        desc: "₹5 lakh health cover per family per year for vulnerable groups.",
        badge: "Healthcare",
        icon: "fa-hospital",
        color: "blue"
    },
    {
        title: "PM Awas Yojana",
        desc: "Subsidy up to ₹2.67 lakh on home loans for affordable housing.",
        badge: "Housing",
        icon: "fa-home",
        color: "orange"
    },
    {
        title: "PM Ujjwala Yojana",
        desc: "Free LPG connections for women from BPL households.",
        badge: "Women Empowerment",
        icon: "fa-fire",
        color: "purple"
    },
    {
        title: "Skill India Mission",
        desc: "Free skill training to boost youth employability.",
        badge: "Education",
        icon: "fa-graduation-cap",
        color: "teal"
    },
    {
        title: "Startup India",
        desc: "Tax benefits, funding & mentorship for entrepreneurs.",
        badge: "Business",
        icon: "fa-rocket",
        color: "rose"
    }
];

const SchemesGrid = ({ onSchemeClick }) => {
    return (
        <section className="section" id="schemes">
            <div className="section-header" data-aos="fade-up">
                <span className="tag">Popular Schemes</span>
                <h2>Explore Key Government Initiatives</h2>
            </div>
            
            <div className="schemes-grid">
                {schemes.map((scheme) => (
                    <div 
                        key={scheme.title}
                        className="scheme-card pop-in" 
                        data-aos="zoom-in-up" 
                        onClick={() => onSchemeClick(scheme.title)}
                    >
                        <div className={`card-icon ${scheme.color}`}>
                            <i className={`fas ${scheme.icon}`}></i>
                        </div>
                        <h3>{scheme.title}</h3>
                        <p>{scheme.desc}</p>
                        <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                            <span className="card-badge">{scheme.badge}</span>
                            <span className="card-link">Learn More <i className="fas fa-arrow-right"></i></span>
                        </div>
                    </div>
                ))}
            </div>
        </section>
    );
};

export default SchemesGrid;
