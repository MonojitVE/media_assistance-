import React from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';

export default function DisplayPanel({ children, onClose }) {
  return (
    <motion.div 
      className="display-panel"
      initial={{ opacity: 0, y: 50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
    >
      <div className="display-header">
        <button className="btn-close" onClick={onClose} aria-label="Close">
          <X size={24} />
        </button>
      </div>
      <div className="display-content">
        {children}
      </div>
    </motion.div>
  );
}
