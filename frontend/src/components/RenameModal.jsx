import { motion, AnimatePresence } from 'framer-motion';
import React, { useState, useEffect } from 'react';
import '../pages/css/RenameModal.css';

const RenameModal = ({ 
    isOpen, 
    onClose, 
    onConfirm, 
    currentTitle = '',
    sessionId = null
}) => {
    const [newTitle, setNewTitle] = useState(currentTitle);

    useEffect(() => {
        if (isOpen) {
            setNewTitle(currentTitle);
        }
    }, [isOpen, currentTitle]);

    if (!isOpen) return null;

    const handleSubmit = (e) => {
        e.preventDefault();
        if (newTitle.trim() && newTitle.trim() !== currentTitle) {
            onConfirm(sessionId, newTitle.trim());
        }
        onClose();
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div 
                    className="modal-overlay"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                >
                    <motion.div 
                        className="rename-modal"
                        initial={{ scale: 0.9, y: 20, opacity: 0 }}
                        animate={{ scale: 1, y: 0, opacity: 1 }}
                        exit={{ scale: 0.9, y: 20, opacity: 0 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="modal-icon">
                            <i className="fas fa-pen"></i>
                        </div>

                        <h2 className="modal-title">Rename Chat</h2>
                        
                        <p className="modal-message">Enter a new name for this chat session.</p>

                        <form onSubmit={handleSubmit}>
                            <input
                                type="text"
                                className="rename-input"
                                value={newTitle}
                                onChange={(e) => setNewTitle(e.target.value)}
                                placeholder="Enter new chat name..."
                                autoFocus
                                maxLength={100}
                            />

                            <div className="modal-actions">
                                <button 
                                    type="button"
                                    className="modal-btn modal-btn-cancel"
                                    onClick={onClose}
                                >
                                    Cancel
                                </button>
                                <button 
                                    type="submit"
                                    className="modal-btn modal-btn-confirm"
                                    disabled={!newTitle.trim() || newTitle.trim() === currentTitle}
                                >
                                    <i className="fas fa-check"></i>
                                    Rename
                                </button>
                            </div>
                        </form>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default RenameModal;