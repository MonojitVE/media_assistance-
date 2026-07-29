import React, { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import MicButton from './components/MicButton';
import DisplayPanel from './components/DisplayPanel';
import VideoPlayer from './components/VideoPlayer';
import Slideshow from './components/Slideshow';
import UnknownState from './components/UnknownState';
import FolderExplorer from './components/FolderExplorer';

const API_BASE = 'http://localhost:8000';

function App() {
  const [uiState, setUiState] = useState('idle'); // 'idle' | 'display'
  const [intent, setIntent] = useState(null);
  const [playlist, setPlaylist] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleTranscript = async (text) => {
    if (!text.trim()) return;
    
    setIsProcessing(true);
    try {
      const res = await fetch(`${API_BASE}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      
      if (!res.ok) throw new Error('API Request failed');
      
      const data = await res.json();
      setIntent(data.intent);
      setPlaylist(data.playlist || []);
      setUiState('display');
      
    } catch (err) {
      console.error(err);
      // Fallback to unknown state gracefully
      setIntent({ action: 'unknown' });
      setUiState('display');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClose = () => {
    setUiState('idle');
    setIntent(null);
    setPlaylist([]);
  };

  const renderDisplayContent = () => {
    if (!intent) return null;

    if (intent.action === 'play') {
      if (playlist.length === 0) {
        return (
          <div className="unknown-state">
            <h2>No media found</h2>
            <p>We couldn't find any media matching that request.</p>
          </div>
        );
      }
      return <VideoPlayer playlist={playlist} />;
    }
    
    if (intent.action === 'slideshow') {
      if (playlist.length === 0) {
        return (
          <div className="unknown-state">
            <h2>No media found</h2>
            <p>We couldn't find any images matching that request.</p>
          </div>
        );
      }
      return <Slideshow playlist={playlist} />;
    }
    
    if (intent.action === 'explore') {
      return <FolderExplorer />;
    }

    // Default to unknown state
    return <UnknownState onTranscript={handleTranscript} />;
  };

  return (
    <div className="app-container">
      <AnimatePresence mode="wait">
        {uiState === 'idle' && (
          <motion.div 
            key="idle" 
            className="idle-container"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
              <div style={{ textAlign: 'center' }}>
                {isProcessing ? (
                  <p style={{ color: 'var(--text-secondary)' }}>Processing command...</p>
                ) : (
                  <p style={{ color: 'var(--text-secondary)' }}>Speak a command</p>
                )}
              </div>
              <MicButton onTranscript={handleTranscript} />
            </div>
            
            <div style={{ width: '100%', maxWidth: '1200px' }}>
               <FolderExplorer />
            </div>
          </motion.div>
        )}
        
        {uiState === 'display' && (
          <DisplayPanel key="display" onClose={handleClose}>
            {renderDisplayContent()}
          </DisplayPanel>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
