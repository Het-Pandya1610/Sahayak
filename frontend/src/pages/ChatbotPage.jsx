import { motion, AnimatePresence } from 'framer-motion';
import React, { useEffect, useRef, useState } from 'react';
import MainLayout from '../layouts/MainLayout';
import './css/ChatbotPage.css';

const ChatbotPage = ({ initialQuery }) => {
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
  const handledQueryRef = useRef(null);
  const [chatHistory, setChatHistory] = useState([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    if (initialQuery && handledQueryRef.current !== initialQuery) {
      handleSendMessage(initialQuery);
      handledQueryRef.current = initialQuery;
    }
  }, [initialQuery]);

  const handleSendMessage = async (text = null) => {
    const query = text || input.trim()

    if (!query || isTyping) return


    const userMessage = {

        type: 'user',

        text: query
    }


    setMessages(prev => [

        ...prev,
        userMessage
    ])


    setInput('')

    setIsTyping(true)


    try {

        const response = await fetch(

          'http://127.0.0.1:8000/api/chatbot/ask/',

          {

              method: 'POST',

              headers: {

                  'Content-Type': 'application/json'
              },

              body: JSON.stringify({

                  query: query,

                  history: [

                      ...chatHistory,

                      {
                          role: 'user',
                          content: query
                      }
                  ]
              })
          }
        )


        const data = await response.json()


        if (data.success) {

          const botMessage = {

              type: 'bot',

              text: data.answer,

              schemes: data.schemes || []
          }


          setMessages(prev => [

              ...prev,
              botMessage
          ])


          setChatHistory(prev => [

              ...prev,

              {
                  role: 'user',
                  content: query
              },

              {
                  role: 'assistant',
                  content: data.answer
              }
          ])

        } else {

          setMessages(prev => [

              ...prev,

              {

                  type: 'bot',

                  text:
                      data.answer ||
                      'No relevant scheme found.'
              }
          ])
        }

    } catch (error) {

      console.error(error)

      setMessages(prev => [

          ...prev,

          {

              type: 'bot',

              text:
                  'Server error occurred.'
          }
      ])

    } finally {

        setIsTyping(false)
    }
  };

  return (
    <div className="chatbot-page">
        <MainLayout>
        <AnimatePresence mode="wait">
            <motion.div
            className="chatbot-content"
            initial={{ y: 100, opacity: 0, scale: 0.9 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 100, opacity: 0, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            >
            <div className="chatbot-container">
                <div className="chatbot-header">
                    <div className="chatbot-avatar">
                        <div className="chatbot-icon">
                            <i className="fas fa-robot"></i>
                        </div>
                        <div>
                            <h3>Sahayak AI</h3>
                        </div>
                    </div>
                </div>

                <div className="chatbot-messages-max">
                {messages.map((msg, i) => (
                    <motion.div
                    key={i}
                    className={`max-msg ${msg.type}`}
                    initial={{ opacity: 0, x: msg.type === 'bot' ? -10 : 10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    >
                    {msg.type === 'bot' && (
                        <i
                        className="fas fa-hand-sparkles"
                        style={{ marginRight: '8px', color: 'var(--secondary)' }}
                        ></i>
                    )}
                    <span dangerouslySetInnerHTML={{ __html: msg.text }}></span>
                    {msg.chips && (
                        <div className="suggestion-chips-max">
                        {msg.chips.map((chip, j) => (
                            <span
                            key={j}
                            className="chip-max"
                            onClick={() => handleSendMessage(chip)}
                            >
                            {chip}
                            </span>
                        ))}
                        </div>
                    )}
                    </motion.div>
                ))}
                {isTyping && (
                    <div className="typing-indicator-max">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                )}
                <div ref={messagesEndRef} />
                </div>

                <div className="chatbot-input-area-max">
                  <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Type your query..."
                      disabled={isTyping}
                      onKeyDown={(e) => {

                          if (e.key === 'Enter') {

                              handleSendMessage()
                          }
                      }}
                  />
                <button onClick={() => handleSendMessage()} aria-label="Send Message">
                    <i className="fas fa-paper-plane"></i>
                </button>
                </div>
            </div>
            </motion.div>
        </AnimatePresence>
        </MainLayout>
    </div>
  );
};

export default ChatbotPage;