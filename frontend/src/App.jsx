import React, { useEffect, useRef, useState } from 'react';
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
  const introOffsetSeconds = 0.28;
  const introPlaybackRate = 1.04;
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const [chatbotQuery, setChatbotQuery] = useState('');
  const [showContent, setShowContent] = useState(false);
  const [isIntroActive, setIsIntroActive] = useState(true);
  const [isBackgroundMode, setIsBackgroundMode] = useState(false);
  const [isVideoReady, setIsVideoReady] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');
  const videoRef = useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  useEffect(() => {
    const video = videoRef.current;
    if (!video) {
      setShowContent(true);
      setIsIntroActive(false);
      return;
    }

    let revealTimer;
    let finishTimer;
    let fallbackTimer;

    const clearTimers = () => {
      [revealTimer, finishTimer, fallbackTimer].forEach(clearTimeout);
    };

    const finishIntro = () => {
      setShowContent(true);
      setIsIntroActive(false);
      setIsBackgroundMode(true);
      clearTimers();
    };

    const syncIntroToVideo = () => {
      if (Number.isFinite(video.duration) && video.duration > introOffsetSeconds) {
        video.currentTime = introOffsetSeconds;
      }

      const duration = Number.isFinite(video.duration) ? video.duration : 5;
      const remainingMs = Math.max((duration - introOffsetSeconds) * 1000 / introPlaybackRate, 0);
      
      clearTimers();
      revealTimer = setTimeout(() => setShowContent(true), Math.max(remainingMs - 1100, 1200));
      finishTimer = setTimeout(finishIntro, Math.max(remainingMs - 120, 1800));
      fallbackTimer = setTimeout(finishIntro, remainingMs + 1000);
    };

    const handleCanPlay = () => {
      setIsVideoReady(true);
      video.playbackRate = introPlaybackRate;
      video.play().catch(finishIntro);
    };

    video.addEventListener('loadedmetadata', syncIntroToVideo);
    video.addEventListener('canplay', handleCanPlay);
    video.addEventListener('ended', finishIntro);

    if (video.readyState >= 1) syncIntroToVideo();
    if (video.readyState >= 3) handleCanPlay();

    // Safety fallback
    fallbackTimer = setTimeout(finishIntro, 8000);

    return () => {
      clearTimers();
      video.removeEventListener('loadedmetadata', syncIntroToVideo);
      video.removeEventListener('canplay', handleCanPlay);
      video.removeEventListener('ended', finishIntro);
    };
  }, []);

  useEffect(() => {
    AOS.init({
      once: true,
      duration: 800,
      offset: 100,
      easing: 'ease-out-cubic'
    });
  }, []);

  const openChatbot = (query = '') => {
    setChatbotQuery(query);
    setIsChatbotOpen(true);
  };

  const closeChatbot = () => {
    setIsChatbotOpen(false);
    setChatbotQuery('');
  };

  return (
    <div className="app-container">
      <div className={`intro-layer ${isIntroActive ? 'is-active' : 'is-finished'} ${isBackgroundMode ? 'is-background' : ''}`}>
        <video
          ref={videoRef}
          className={`lotus-video ${isVideoReady ? 'is-ready' : ''} ${isBackgroundMode ? 'is-background' : ''}`}
          autoPlay
          muted
          playsInline
          preload="auto"
          aria-hidden="true"
        >
          <source src="/Lotus.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
        <div className={`video-overlay ${isBackgroundMode ? 'is-background' : ''}`}></div>
      </div>


      <motion.div
        className={`content-wrapper ${showContent ? 'is-visible' : ''}`}
        initial={{ opacity: 0 }}
        animate={{ opacity: showContent ? 1 : 0 }}
        transition={{ duration: 1.5, ease: "easeOut" }}
        style={{ pointerEvents: showContent ? 'all' : 'none' }}
      >
        <Navbar theme={theme} toggleTheme={toggleTheme} />

        <main>
          <Hero onSearch={openChatbot} showContent={showContent} />
          <SchemesGrid onSchemeClick={(title) => openChatbot(`Tell me about ${title}`)} />
          <HowItWorks />
          <CTABanner onOpenChatbot={() => openChatbot()} />
        </main>

        <Footer theme={theme} />
      </motion.div>

      <Chatbot
        isOpen={isChatbotOpen}
        onOpen={openChatbot}
        onClose={closeChatbot}
        initialQuery={chatbotQuery}
      />
    </div>
  );
}

export default App;
