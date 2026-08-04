import { motion, AnimatePresence } from 'framer-motion';
import React, { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import { Link } from 'react-router-dom';
import axios from 'axios';
import ConfirmationModal from '../components/ConfirmationModal';
import RenameModal from '../components/RenameModal';
import './css/ChatbotPage.css';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatbotPage = () => {
    const navigate = useNavigate();
    const { sessionId } = useParams();
    const [sessions, setSessions] = useState([]);
    const [currentSessionId, setCurrentSessionId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [loading, setLoading] = useState(true);
    
    // Modal states
    const [deleteModalConfig, setDeleteModalConfig] = useState({
        isOpen: false,
        sessionId: null,
        sessionTitle: ''
    });
    const [renameModalConfig, setRenameModalConfig] = useState({
        isOpen: false,
        sessionId: null,
        currentTitle: ''
    });
    
    // Message editing states
    const [editingMessageIndex, setEditingMessageIndex] = useState(null);
    const [editText, setEditText] = useState('');
    
    const messagesEndRef = useRef(null);
    const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    // Get auth token
    const getToken = () => localStorage.getItem('token');

    // Format date for sidebar
    const formatDate = (dateStr) => {
        if (!dateStr) return 'Unknown';
        
        try {
            let date;
            
            if (dateStr instanceof Date) {
                date = dateStr;
            } else {
                date = new Date(dateStr);
                if (isNaN(date.getTime())) {
                    const cleaned = dateStr.replace('Z', '').replace('T', ' ');
                    date = new Date(cleaned + 'Z');
                }
            }
            
            if (isNaN(date.getTime())) {
                console.warn('Invalid date:', dateStr);
                return 'Unknown';
            }
            
            const now = new Date();
            const diffMs = now.getTime() - date.getTime();
            
            if (diffMs < 0) {
                return date.toLocaleDateString('en-IN', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric'
                });
            }
            
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);
            const diffWeeks = Math.floor(diffDays / 7);
            const diffMonths = Math.floor(diffDays / 30);
            const diffYears = Math.floor(diffDays / 365);

            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            if (diffDays < 7) return `${diffDays}d ago`;
            if (diffWeeks < 4) return `${diffWeeks}w ago`;
            if (diffMonths < 12) return `${diffMonths}mo ago`;
            return `${diffYears}y ago`;
            
        } catch (error) {
            console.error('Error formatting date:', dateStr, error);
            return 'Unknown';
        }
    };

    // Fetch sessions from backend
    const fetchSessions = async () => {
        try {
            const token = getToken();
            if (!token) {
                navigate('/login');
                return [];
            }

            const response = await axios.get(`${API_URL}/chatbot/sessions/`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            if (response.data.success) {
                setSessions(response.data.sessions);
                return response.data.sessions;
            }
            return [];
        } catch (error) {
            console.error('Error fetching sessions:', error);
            return [];
        }
    };

    // Load session messages - FIXED: ensure IDs are stored
    const loadSession = async (sessionId) => {
        try {
            const token = getToken();
            const response = await axios.get(`${API_URL}/chatbot/sessions/${sessionId}/`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            if (response.data.success) {
                const session = response.data.session;
                console.log("📋 Session data:", session);
                
                const formattedMessages = session.messages.map(msg => ({
                    id: msg.id,  // ✅ Store the ID
                    type: msg.role === 'user' ? 'user' : 'bot',
                    text: msg.content,
                    schemes: msg.schemes || [],
                    chips: msg.role === 'assistant' && msg.content.includes('Hello!') ? ['Housing', 'Farmer', 'Health', 'Education'] : undefined
                }));
                
                console.log("📋 Formatted messages with IDs:", formattedMessages);
                setMessages(formattedMessages);
                setCurrentSessionId(sessionId);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Error loading session:', error);
            return false;
        }
    };

    // Create new session
    const createNewSession = async () => {
        try {
            const token = getToken();
            const response = await axios.post(
                `${API_URL}/chatbot/sessions/create/`,
                { title: 'New Chat' },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (response.data.success) {
                const session = response.data.session;
                await fetchSessions();
                navigate(`/chatbot/session/${session.id}`);
                setCurrentSessionId(session.id);
                const formattedMessages = session.messages.map(msg => ({
                    id: msg.id,
                    type: msg.role === 'user' ? 'user' : 'bot',
                    text: msg.content,
                    schemes: msg.schemes || [],
                    chips: msg.role === 'assistant' ? ['Housing', 'Farmer', 'Health', 'Education'] : undefined
                }));
                setMessages(formattedMessages);
                setIsSidebarOpen(false);
                return session.id;
            }
            return null;
        } catch (error) {
            console.error('Error creating session:', error);
            alert('Failed to create new chat. Please try again.');
            return null;
        }
    };

    // ============================================================
    // DELETE SESSION FUNCTIONS
    // ============================================================
    const showDeleteModal = (sessionId, e) => {
        e.stopPropagation();
        const session = sessions.find(s => s.id === sessionId);
        setDeleteModalConfig({
            isOpen: true,
            sessionId: sessionId,
            sessionTitle: session?.title || 'Untitled Chat'
        });
    };

    const closeDeleteModal = () => {
        setDeleteModalConfig({
            isOpen: false,
            sessionId: null,
            sessionTitle: ''
        });
    };

    const handleConfirmDelete = async () => {
        const { sessionId } = deleteModalConfig;
        
        try {
            const token = getToken();
            const response = await axios.delete(
                `${API_URL}/chatbot/sessions/${sessionId}/delete/`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );

            if (response.data.success) {
                const remainingSessions = await fetchSessions();
                
                if (sessionId === currentSessionId) {
                    if (remainingSessions && remainingSessions.length > 0) {
                        navigate(`/chatbot/session/${remainingSessions[0].id}`);
                    } else {
                        const newId = await createNewSession();
                        if (newId) {
                            navigate(`/chatbot/session/${newId}`);
                        }
                    }
                }
            } else {
                alert(response.data.error || 'Failed to delete session');
            }
        } catch (error) {
            console.error('Error deleting session:', error);
            alert(error.response?.data?.error || 'Failed to delete session. Please try again.');
        }
    };

    // ============================================================
    // RENAME SESSION FUNCTIONS
    // ============================================================
    const showRenameModal = (sessionId, e) => {
        e.stopPropagation();
        const session = sessions.find(s => s.id === sessionId);
        setRenameModalConfig({
            isOpen: true,
            sessionId: sessionId,
            currentTitle: session?.title || 'New Chat'
        });
    };

    const closeRenameModal = () => {
        setRenameModalConfig({
            isOpen: false,
            sessionId: null,
            currentTitle: ''
        });
    };

    const handleConfirmRename = async (sessionId, newTitle) => {
        try {
            const token = getToken();
            const response = await axios.patch(
                `${API_URL}/chatbot/sessions/${sessionId}/rename/`,
                { title: newTitle },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (response.data.success) {
                await fetchSessions();
                if (sessionId === currentSessionId) {
                    setSessions(prev => prev.map(s => 
                        s.id === sessionId ? { ...s, title: newTitle } : s
                    ));
                }
            } else {
                alert(response.data.error || 'Failed to rename session');
            }
        } catch (error) {
            console.error('Error renaming session:', error);
            alert(error.response?.data?.error || 'Failed to rename session. Please try again.');
        }
    };

    // ============================================================
    // CLEAR CHAT - Delete all messages
    // ============================================================
    const handleClearChat = async () => {
        if (!window.confirm('Clear all messages in this chat? This cannot be undone.')) return;
        
        try {
            const token = getToken();
            const response = await axios.delete(
                `${API_URL}/chatbot/sessions/${currentSessionId}/clear/`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );
            
            if (response.data.success) {
                const welcomeMsg = {
                    type: 'bot',
                    text: "Hello! I'm your trusted AI guide. Ask me about any government scheme — I'll provide accurate, verified details.",
                    chips: ['Housing', 'Farmer', 'Health', 'Education']
                };
                setMessages([welcomeMsg]);
                await fetchSessions();
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
            alert('Failed to clear chat. Please try again.');
        }
    };

    // ============================================================
    // DELETE SINGLE MESSAGE
    // ============================================================
    const handleDeleteMessage = async (messageIndex) => {
        const msg = messages[messageIndex];
        if (!msg || msg.type === 'bot' || !msg.id) return;
        
        if (!window.confirm('Delete this message and its response?')) return;
        
        try {
            const token = getToken();
            const response = await axios.delete(
                `${API_URL}/chatbot/sessions/${currentSessionId}/messages/${msg.id}/delete/`,
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            );
            
            if (response.data.success) {
                // Remove the user message and its bot response (if any)
                const newMessages = [...messages];
                // Check if next message is bot response
                if (messageIndex + 1 < newMessages.length && newMessages[messageIndex + 1].type === 'bot') {
                    newMessages.splice(messageIndex, 2);
                } else {
                    newMessages.splice(messageIndex, 1);
                }
                setMessages(newMessages);
                await fetchSessions();
            }
        } catch (error) {
            console.error('Error deleting message:', error);
            alert('Failed to delete message. Please try again.');
        }
    };

    // ============================================================
    // EDIT MESSAGE & REGENERATE
    // ============================================================
    const startEditing = (index) => {
        const msg = messages[index];
        if (!msg || msg.type !== 'user') return;
        setEditingMessageIndex(index);
        setEditText(msg.text);
    };

    const cancelEditing = () => {
        setEditingMessageIndex(null);
        setEditText('');
    };

    const handleEditMessage = async (messageIndex, newText) => {
        if (!newText.trim()) return;
        
        const msg = messages[messageIndex];
        console.log("Editing message:", msg);
        console.log("Message ID:", msg.id);
        console.log("New text:", newText);
        
        if (!msg || msg.type !== 'user' || !msg.id) {
            console.log("Invalid message or missing ID");
            return;
        }
        
        try {
            const token = getToken();
            console.log("Sending PUT request to:", `${API_URL}/chatbot/sessions/${currentSessionId}/messages/${msg.id}/edit/`);
            
            const response = await axios.put(
                `${API_URL}/chatbot/sessions/${currentSessionId}/messages/${msg.id}/edit/`,
                { content: newText },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            console.log("Response:", response.data);
            
            if (response.data.success) {
                const newMessages = [...messages];
                // Update user message
                newMessages[messageIndex] = {
                    ...newMessages[messageIndex],
                    text: response.data.user_message.content
                };
                // Replace or add bot response
                if (messageIndex + 1 < newMessages.length && newMessages[messageIndex + 1].type === 'bot') {
                    newMessages[messageIndex + 1] = {
                        type: 'bot',
                        text: response.data.assistant_message.content,
                        schemes: response.data.assistant_message.schemes || []
                    };
                } else {
                    newMessages.splice(messageIndex + 1, 0, {
                        type: 'bot',
                        text: response.data.assistant_message.content,
                        schemes: response.data.assistant_message.schemes || []
                    });
                }
                setMessages(newMessages);
                setEditingMessageIndex(null);
                setEditText('');
                await fetchSessions();
            } else {
                alert(response.data.message || 'Failed to edit message');
            }
        } catch (error) {
            console.error('Error editing message:', error);
            console.error('Error response:', error.response?.data);
            alert(error.response?.data?.error || 'Failed to edit message. Please try again.');
        }
    };

    // Switch session
    const switchSession = (sessionId) => {
        if (sessionId !== currentSessionId) {
            setMessages([]);
            setIsTyping(false);
            setInput('');
            setEditingMessageIndex(null);
            navigate(`/chatbot/session/${sessionId}`);
        }
        setIsSidebarOpen(false);
    };

    // Send message
    const handleSendMessage = async (text = null) => {
        const query = text || input.trim();
        
        if (!query || isTyping || !currentSessionId) {
            return;
        }

        const userMessage = {
            type: 'user',
            text: query
        };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        try {
            const token = getToken();
            const response = await axios.post(
                `${API_URL}/chatbot/sessions/${currentSessionId}/send/`,
                { query },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (response.data.success) {
                const botMessage = {
                    type: 'bot',
                    text: response.data.message.content,
                    schemes: response.data.message.schemes || []
                };
                setMessages(prev => [...prev, botMessage]);
                await fetchSessions();
            } else {
                throw new Error(response.data.error || 'Failed to get response');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            const botMessage = {
                type: 'bot',
                text: error.response?.data?.error || 'Server error occurred. Please try again.'
            };
            setMessages(prev => [...prev, botMessage]);
        } finally {
            setIsTyping(false);
        }
    };

    // Initialize
    useEffect(() => {
        const init = async () => {
            setLoading(true);
            try {
                const sessionsList = await fetchSessions();
                
                if (sessionId) {
                    const loaded = await loadSession(sessionId);
                    if (!loaded) {
                        const newId = await createNewSession();
                        if (newId) {
                            navigate(`/chatbot/session/${newId}`);
                        }
                    }
                } else if (sessionsList && sessionsList.length > 0) {
                    navigate(`/chatbot/session/${sessionsList[0].id}`);
                } else {
                    const newId = await createNewSession();
                    if (newId) {
                        navigate(`/chatbot/session/${newId}`);
                    }
                }
            } catch (error) {
                console.error('Initialization error:', error);
            } finally {
                setLoading(false);
            }
        };

        init();
    }, [sessionId]);

    // Handle session switching from URL
    useEffect(() => {
        if (sessionId && sessionId !== currentSessionId) {
            const loadSessionData = async () => {
                const loaded = await loadSession(sessionId);
                if (!loaded) {
                    const newId = await createNewSession();
                    if (newId) {
                        navigate(`/chatbot/session/${newId}`);
                    }
                }
            };
            loadSessionData();
        }
    }, [sessionId]);

    if (loading) {
        return (
            <MainLayout>
                <div className="chatbot-loading">
                    <div className="spinner"></div>
                    <p>Loading chat...</p>
                </div>
            </MainLayout>
        );
    }

    return (
        <>
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
                                {/* Mobile Menu Toggle */}
                                <button 
                                    className="sidebar-toggle"
                                    onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                                    aria-label="Toggle sidebar"
                                >
                                    <i className={`fas ${isSidebarOpen ? 'fa-times' : 'fa-bars'}`}></i>
                                </button>

                                {/* Sidebar */}
                                <div className={`chat-sidebar ${isSidebarOpen ? 'open' : ''}`}>
                                    <div className="sidebar-header">
                                        <button 
                                            className="new-chat-btn"
                                            onClick={createNewSession}
                                        >
                                            <i className="fas fa-plus"></i>
                                            New Chat
                                        </button>
                                    </div>

                                    <div className="sessions-list">
                                        {sessions.length === 0 ? (
                                            <div className="no-sessions">
                                                <p>No chats yet</p>
                                                <span>Start a new conversation</span>
                                            </div>
                                        ) : (
                                            sessions.map((session) => (
                                                <div
                                                    key={session.id}
                                                    className={`session-item ${session.id === currentSessionId ? 'active' : ''}`}
                                                >
                                                    <div 
                                                        className="session-info"
                                                        onClick={() => switchSession(session.id)}
                                                    >
                                                        <div className="session-title">
                                                            {session.title || 'New Chat'}
                                                        </div>
                                                        <div className="session-meta">
                                                            <span className="session-time">
                                                                {formatDate(session.created_at)}
                                                            </span>
                                                            <span className="session-msg-count">
                                                                {session.message_count || 0} msgs
                                                            </span>
                                                        </div>
                                                    </div>
                                                    <div className="session-actions">
                                                        <button
                                                            className="rename-session"
                                                            onClick={(e) => showRenameModal(session.id, e)}
                                                            aria-label="Rename session"
                                                            title="Rename"
                                                        >
                                                            <i className="fas fa-pen"></i>
                                                        </button>
                                                        <button
                                                            className="delete-session"
                                                            onClick={(e) => showDeleteModal(session.id, e)}
                                                            aria-label="Delete session"
                                                            title="Delete"
                                                        >
                                                            <i className="fas fa-trash-alt"></i>
                                                        </button>
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>

                                {/* Main Chat Area */}
                                <div className="chat-main">
                                    <div className="chatbot-header-max">
                                        <div className="chatbot-avatar">
                                            <div className="chatbot-icon">
                                                <i className="fas fa-robot"></i>
                                            </div>
                                            <div>
                                                <h3>Sahayak AI</h3>
                                                <span className="chat-status">Online</span>
                                            </div>
                                        </div>
                                        <div className="chat-header-actions">
                                            <button 
                                                className="clear-chat-btn"
                                                onClick={handleClearChat}
                                                title="Clear all messages"
                                            >
                                                <i className="fas fa-eraser"></i>
                                            </button>
                                        </div>
                                    </div>

                                    <div className="chatbot-messages-max">
                                        {messages.length === 0 ? (
                                            <div className="empty-chat">
                                                <i className="fas fa-comment-dots"></i>
                                                <p>Start a conversation with Sahayak AI</p>
                                            </div>
                                        ) : (
                                            messages.map((msg, i) => (
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
                                                    
                                                    {editingMessageIndex === i && msg.type === 'user' ? (
                                                        <div className="edit-message-container">
                                                            <textarea
                                                                className="edit-textarea"
                                                                value={editText}
                                                                onChange={(e) => setEditText(e.target.value)}
                                                                rows={3}
                                                                autoFocus
                                                            />
                                                            <div className="edit-actions">
                                                                <button
                                                                    className="edit-save-btn"
                                                                    onClick={() => handleEditMessage(i, editText)}
                                                                >
                                                                    <i className="fas fa-check"></i> Save
                                                                </button>
                                                                <button
                                                                    className="edit-cancel-btn"
                                                                    onClick={cancelEditing}
                                                                >
                                                                    <i className="fas fa-times"></i> Cancel
                                                                </button>
                                                            </div>
                                                        </div>
                                                    ) : (
                                                        <>
                                                            <span>
                                                                {typeof msg.text === 'object' 
                                                                    ? JSON.stringify(msg.text.answer) 
                                                                    : <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                                                                }
                                                            </span>
                                                            {msg.type === 'user' && (
                                                                <div className="message-actions">
                                                                    <button
                                                                        className="msg-action-btn edit-btn"
                                                                        onClick={() => startEditing(i)}
                                                                        title="Edit message"
                                                                    >
                                                                        <i className="fas fa-pen"></i>
                                                                    </button>
                                                                    <button
                                                                        className="msg-action-btn delete-btn"
                                                                        onClick={() => handleDeleteMessage(i)}
                                                                        title="Delete message"
                                                                    >
                                                                        <i className="fas fa-trash"></i>
                                                                    </button>
                                                                </div>
                                                            )}
                                                        </>
                                                    )}
                                                    
                                                    {msg.chips && msg.chips.length > 0 && (
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
                                            ))
                                        )}
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
                                            placeholder={
                                                !currentSessionId 
                                                    ? "Select or create a chat to start..." 
                                                    : isTyping 
                                                        ? "Wait for response..." 
                                                        : "Type your query..."
                                            }
                                            disabled={isTyping || !currentSessionId}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter' && !e.shiftKey) {
                                                    e.preventDefault();
                                                    handleSendMessage();
                                                }
                                            }}
                                        />
                                        <button 
                                            onClick={() => handleSendMessage()} 
                                            aria-label="Send Message"
                                            disabled={isTyping || !input.trim() || !currentSessionId}
                                        >
                                            <i className="fas fa-paper-plane"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    </AnimatePresence>
                </MainLayout>
            </div>

            {/* Delete Confirmation Modal */}
            <ConfirmationModal
                isOpen={deleteModalConfig.isOpen}
                onClose={closeDeleteModal}
                onConfirm={handleConfirmDelete}
                title="Delete Chat Session?"
                message={`Are you sure you want to delete "${deleteModalConfig.sessionTitle}"? This action cannot be undone and all messages will be permanently removed.`}
                confirmText="Delete"
                cancelText="Cancel"
                type="danger"
            />

            {/* Rename Modal */}
            <RenameModal
                isOpen={renameModalConfig.isOpen}
                onClose={closeRenameModal}
                onConfirm={handleConfirmRename}
                currentTitle={renameModalConfig.currentTitle}
                sessionId={renameModalConfig.sessionId}
            />
        </>
    );
};

export default ChatbotPage;