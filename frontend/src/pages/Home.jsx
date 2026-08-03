import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import AOS from 'aos';
import 'aos/dist/aos.css';

import Hero from '../components/Hero';
import SchemesGrid from '../components/SchemesGrid';
import HowItWorks from '../components/HowItWorks';
import CTABanner from '../components/CTABanner';
import Chatbot from '../components/Chatbot';
import Navbar from '../layouts/Navbar';
import Footer from '../layouts/Footer';
import './css/Home.css';

function Home() {
  const introOffsetSeconds = 0.28;
  const introPlaybackRate = 1.04;

  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const [chatbotQuery, setChatbotQuery] = useState('');
  const [showContent, setShowContent] = useState(false);
  const [isIntroActive, setIsIntroActive] = useState(true);
  const [isBackgroundMode, setIsBackgroundMode] = useState(false);
  const [isVideoReady, setIsVideoReady] = useState(false);
  const [isVideoSwitching, setIsVideoSwitching] = useState(false);

  const videoRef = useRef(null);
  const videoContainerRef = useRef(null);

  // Theme state
  const [theme, setTheme] = useState(
    () => localStorage.getItem('theme') || 'light'
  );

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  // --- Intro logic ---
  useEffect(() => {
    const video = videoRef.current;
    if (!video) {
      setShowContent(true);
      setIsIntroActive(false);
      return;
    }

    // Check if the intro has already been played in this session
    const introPlayedSession = sessionStorage.getItem('introPlayedInSession');

    // If already played, skip intro and go directly to background mode
    if (introPlayedSession === 'true') {
      // Ensure video is at the end and paused
      const setToEndAndPause = () => {
        if (Number.isFinite(video.duration)) {
          video.currentTime = video.duration;
        }
        video.pause();
        setShowContent(true);
        setIsIntroActive(false);
        setIsBackgroundMode(true);
        setIsVideoReady(true);
      };

      // If video metadata is already loaded, apply immediately
      if (video.readyState >= 1) {
        setToEndAndPause();
      } else {
        video.addEventListener('loadedmetadata', setToEndAndPause);
        return () => video.removeEventListener('loadedmetadata', setToEndAndPause);
      }
      return;
    }

    // --- Intro not yet played in this session ---
    let revealTimer, finishTimer, fallbackTimer;
    let isIntroFinished = false;

    const clearTimers = () => {
      clearTimeout(revealTimer);
      clearTimeout(finishTimer);
      clearTimeout(fallbackTimer);
    };

    const finishIntro = () => {
      if (isIntroFinished) return;
      isIntroFinished = true;

      video.pause();
      if (Number.isFinite(video.duration)) {
        video.currentTime = video.duration;
      }

      setShowContent(true);
      setIsIntroActive(false);
      setIsBackgroundMode(true);
      sessionStorage.setItem('introPlayedInSession', 'true');
      clearTimers();
    };

    const syncIntroToVideo = () => {
      if (Number.isFinite(video.duration) && video.duration > introOffsetSeconds) {
        video.currentTime = introOffsetSeconds;
      }

      const duration = Number.isFinite(video.duration) ? video.duration : 5;
      const remainingMs = Math.max(
        ((duration - introOffsetSeconds) * 1000) / introPlaybackRate,
        0
      );

      clearTimers();
      revealTimer = setTimeout(
        () => setShowContent(true),
        Math.max(remainingMs - 1100, 1200)
      );
      finishTimer = setTimeout(finishIntro, Math.max(remainingMs - 120, 1800));
      fallbackTimer = setTimeout(finishIntro, remainingMs + 1000);
    };

    const handleCanPlay = () => {
      setIsVideoReady(true);
      video.playbackRate = introPlaybackRate;
      if (!isIntroFinished) {
        video.play().catch(finishIntro);
      }
    };

    const handleEnded = () => {
      finishIntro();
    };

    video.addEventListener('loadedmetadata', syncIntroToVideo);
    video.addEventListener('canplay', handleCanPlay);
    video.addEventListener('ended', handleEnded);

    if (video.readyState >= 1) syncIntroToVideo();
    if (video.readyState >= 3) handleCanPlay();

    fallbackTimer = setTimeout(finishIntro, 4000);

    return () => {
      clearTimers();
      video.removeEventListener('loadedmetadata', syncIntroToVideo);
      video.removeEventListener('canplay', handleCanPlay);
      video.removeEventListener('ended', handleEnded);
    };
  }, []); // runs only on mount

  // --- Smooth theme switch (unchanged) ---
  useEffect(() => {
    const video = videoRef.current;
    const container = videoContainerRef.current;
    if (!video || isIntroActive || !container) return;

    const newSrc = theme === 'dark' ? '/Lotus_Dark_PC.mp4' : '/Lotus_Light_PC.mp4';
    if (video.src === newSrc) return;

    setIsVideoSwitching(true);
    container.style.opacity = '0';

    const loadNewVideo = () => {
      video.src = newSrc;
      video.load();

      const onLoaded = () => {
        if (Number.isFinite(video.duration)) {
          video.currentTime = video.duration;
        }
        video.pause();
        container.style.opacity = '1';
        setIsVideoSwitching(false);
        video.removeEventListener('loadedmetadata', onLoaded);
      };

      video.addEventListener('loadedmetadata', onLoaded);
    };

    const timer = setTimeout(loadNewVideo, 500);
    return () => clearTimeout(timer);
  }, [theme, isIntroActive]);

  // --- AOS init (unchanged) ---
  useEffect(() => {
    AOS.init({
      once: true,
      duration: 800,
      offset: 100,
      easing: 'ease-out-cubic',
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
      <Navbar theme={theme} toggleTheme={toggleTheme} />
      <div
        className={`intro-layer ${
          isIntroActive ? 'is-active' : 'is-finished'
        } ${isBackgroundMode ? 'is-background' : ''}`}
        ref={videoContainerRef}
        style={{ transition: 'opacity 0.5s ease' }}
      >
        <video
          ref={videoRef}
          className={`lotus-video ${
            isVideoReady ? 'is-ready' : ''
          } ${isBackgroundMode ? 'is-background' : ''}`}
          muted
          playsInline
          preload="auto"
          aria-hidden="true"
          style={{ opacity: isVideoSwitching ? 0 : 1, transition: 'opacity 0.5s ease' }}
        >
          <source
            src={theme === 'dark' ? '/Lotus_Dark_PC.mp4' : '/Lotus_Light_PC.mp4'}
            type="video/mp4"
          />
          Your browser does not support the video tag.
        </video>
        <div className={`video-overlay ${isBackgroundMode ? 'is-background' : ''}`}></div>
      </div>
      <motion.div
        className={`content-wrapper ${showContent ? 'is-visible' : ''}`}
        initial={{ opacity: 0 }}
        animate={{ opacity: showContent ? 1 : 0 }}
        transition={{ duration: 1.5, ease: 'easeOut' }}
        style={{ pointerEvents: showContent ? 'all' : 'none' }}
      >
        <main>
          <Hero onSearch={openChatbot} showContent={showContent} />
          <SchemesGrid onSchemeClick={(title) => openChatbot(`Tell me about ${title}`)} />
          <HowItWorks />
          <CTABanner onOpenChatbot={() => openChatbot()} />
        </main>
      </motion.div>
      <Chatbot
        isOpen={isChatbotOpen}
        onOpen={openChatbot}
        onClose={closeChatbot}
        initialQuery={chatbotQuery}
      />
      <Footer theme={theme} />
    </div>
  );
}

export default Home;