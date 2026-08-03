import { motion, AnimatePresence } from 'framer-motion';
import React from 'react';
import '../pages/css/ConfirmationModal.css';

const ConfirmationModal = ({ 
    isOpen, 
    onClose, 
    onConfirm, 
    title = 'Confirm Action',
    message = 'Are you sure you want to proceed?',
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    type = 'danger' // 'danger', 'warning', 'info'
}) => {
    if (!isOpen) return null;

    const getIcon = () => {
        switch(type) {
            case 'danger':
                return <i className="fas fa-exclamation-triangle"></i>;
            case 'warning':
                return <i className="fas fa-exclamation-circle"></i>;
            default:
                return <i className="fas fa-info-circle"></i>;
        }
    };

    const getTypeClass = () => {
        switch(type) {
            case 'danger':
                return 'modal-danger';
            case 'warning':
                return 'modal-warning';
            default:
                return 'modal-info';
        }
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
                        className={`confirmation-modal ${getTypeClass()}`}
                        initial={{ scale: 0.9, y: 20, opacity: 0 }}
                        animate={{ scale: 1, y: 0, opacity: 1 }}
                        exit={{ scale: 0.9, y: 20, opacity: 0 }}
                        transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="modal-icon">
                            {getIcon()}
                        </div>

                        <h2 className="modal-title">{title}</h2>
                        
                        <p className="modal-message">{message}</p>

                        <div className="modal-actions">
                            <button 
                                className="modal-btn modal-btn-cancel"
                                onClick={onClose}
                            >
                                {cancelText}
                            </button>
                            <button 
                                className="modal-btn modal-btn-confirm"
                                onClick={() => {
                                    onConfirm();
                                    onClose();
                                }}
                            >
                                {confirmText}
                            </button>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default ConfirmationModal;