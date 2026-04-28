import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import AOS from 'aos';
import 'aos/dist/aos.css';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import SchemesGrid from './components/SchemesGrid';
import HowItWorks from './components/HowItWorks';
import CTABanner from './components/CTABanner';
import Footer from './components/Footer';
import Chatbot from './components/Chatbot';

function App() {
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const [chatbotQuery, setChatbotQuery] = useState('');
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowContent(true);
    }, 6000); // Wait for the lotus to bloom
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    AOS.init({
      once: true,
      duration: 700,
      offset: 80,
    });
  }, []);

  const openChatbot = (query = '') => {
    setChatbotQuery(query);
    setIsChatbotOpen(true);
  };

  const handleSchemeClick = (schemeTitle) => {
    openChatbot(`Tell me about ${schemeTitle}`);
  };

  const handleHeroSearch = (query) => {
    openChatbot(query);
  };

  return (
    <div className="app-container">
      {/* LOTUS VIDEO BACKGROUND */}
      <video
        id="lotusVideo"
        autoPlay
        muted
        playsInline
        onEnded={(e) => e.target.pause()}
      >
        <source src="/Lotus.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>


      <motion.div
        className="content-wrapper"
        initial={{ opacity: 0 }}
        animate={{ opacity: showContent ? 1 : 0 }}
        transition={{ duration: 2, ease: "easeInOut" }}
        style={{ pointerEvents: showContent ? 'all' : 'none' }}
      >
        <div id="videoOverlay"></div>
        <Navbar />

        <main>
          <Hero onSearch={handleHeroSearch} showContent={showContent} />
          <SchemesGrid onSchemeClick={handleSchemeClick} />
          <HowItWorks />
          <CTABanner onOpenChatbot={() => openChatbot()} />
        </main>

        <Footer />
      </motion.div>

      <Chatbot
        isOpen={isChatbotOpen}
        onClose={(shouldOpen) => setIsChatbotOpen(shouldOpen === undefined ? !isChatbotOpen : !shouldOpen)}
        initialQuery={chatbotQuery}
      />
    </div>
  );
}

export default App;
