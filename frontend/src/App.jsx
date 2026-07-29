import React, { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { FolderOpen, Cloud } from 'lucide-react';
import MicButton from './components/MicButton';
import DisplayPanel from './components/DisplayPanel';
import VideoPlayer from './components/VideoPlayer';
import Slideshow from './components/Slideshow';
import UnknownState from './components/UnknownState';
import FolderExplorer from './components/FolderExplorer';
import FolderBrowser from './components/FolderBrowser';

const API_BASE = 'http://localhost:8000';

function App() {
  const [uiState, setUiState] = useState('idle'); // 'idle' | 'display' | 'browser'
  const [intent, setIntent] = useState(null);
  const [playlist, setPlaylist] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  
  const [availableFolders, setAvailableFolders] = useState([]);
  const [selectedFolders, setSelectedFolders] = useState([]);
  const [scanPath, setScanPath] = useState('');
  const [browsingFolder, setBrowsingFolder] = useState(null); // String (physical folder)
  const [browsingSmartFolder, setBrowsingSmartFolder] = useState(null); // Object { type, subtype }
  const [isDriveConnecting, setIsDriveConnecting] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    if (code) {
      window.history.replaceState({}, document.title, window.location.pathname);
      handleDriveCallback(code);
    }
  }, []);

  const handleDriveCallback = async (code) => {
    setIsDriveConnecting(true);
    try {
      // 1. exchange token
      const res = await fetch(`${API_BASE}/drive/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
      });
      if (!res.ok) throw new Error('Failed to exchange token');
      const tokenData = await res.json();
      
      // 2. start scan
      alert('Google Drive connected! Scanning files... This may take a moment.');
      const scanRes = await fetch(`${API_BASE}/drive/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          access_token: tokenData.access_token,
          refresh_token: tokenData.refresh_token,
          client_id: tokenData.client_id,
          client_secret: tokenData.client_secret,
          token_uri: tokenData.token_uri
        })
      });
      if (!scanRes.ok) throw new Error('Drive scan failed');
      const scanData = await scanRes.json();
      alert(`Drive Scan complete.\nAdded/Updated: ${scanData.stats.added}\nErrors: ${scanData.stats.errors}`);
      fetchFolders();
    } catch (err) {
      console.error(err);
      alert('Error during Google Drive integration');
    } finally {
      setIsDriveConnecting(false);
    }
  };

  const handleConnectDrive = async () => {
    try {
      const res = await fetch(`${API_BASE}/drive/auth/url`);
      const data = await res.json();
      window.location.href = data.auth_url;
    } catch (err) {
      console.error(err);
      alert('Failed to connect to Google Drive');
    }
  };

  const fetchFolders = async () => {
    try {
      const res = await fetch(`${API_BASE}/media/folders`);
      if (res.ok) {
        const data = await res.json();
        setAvailableFolders(data);
        // Default to all selected
        setSelectedFolders(data);
      }
    } catch (e) {
      console.error('Failed to fetch folders', e);
    }
  };

  useEffect(() => {
    fetchFolders();
  }, []);

  const handleTranscript = async (text) => {
    if (!text.trim()) return;
    
    setIsProcessing(true);
    try {
      const bodyPayload = { text };
      if (selectedFolders.length > 0) {
        bodyPayload.folders = selectedFolders;
      }

      const res = await fetch(`${API_BASE}/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyPayload)
      });
      
      if (!res.ok) throw new Error('API Request failed');
      
      const data = await res.json();
      setIntent(data.intent);
      setPlaylist(data.playlist || []);
      setUiState('display');
      
    } catch (err) {
      console.error(err);
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
    setBrowsingFolder(null);
    setBrowsingSmartFolder(null);
  };

  const handleScan = async () => {
    setIsScanning(true);
    try {
      let url = `${API_BASE}/scan`;
      if (scanPath.trim()) {
        url += `?root=${encodeURIComponent(scanPath.trim())}`;
      }
      const res = await fetch(url, {
        method: 'POST'
      });
      if (!res.ok) throw new Error('Scan failed');
      const data = await res.json();
      alert(`Scan complete.\nAdded: ${data.added}\nSkipped: ${data.skipped}\nErrored: ${data.errored}`);
      fetchFolders();
    } catch (err) {
      console.error(err);
      alert('Failed to scan media folder');
    } finally {
      setIsScanning(false);
      setScanPath('');
    }
  };

  const toggleFolder = (folder) => {
    setSelectedFolders(prev => 
      prev.includes(folder) 
        ? prev.filter(f => f !== folder)
        : [...prev, folder]
    );
  };

  const openFolderBrowser = (folder) => {
    setBrowsingFolder(folder);
    setBrowsingSmartFolder(null);
    setUiState('browser');
  };

  const openSmartFolderBrowser = (type, subtype) => {
    setBrowsingSmartFolder({ type, subtype });
    setBrowsingFolder(null);
    setUiState('browser');
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
      return <FolderExplorer selectedFolders={selectedFolders} onFolderClick={openSmartFolderBrowser} />;
    }

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
            
            <div className="dashboard-grid">
              {/* Left: Folder Management */}
              <div className="folder-management-panel">
                <div className="panel-header">
                  <h3>Media Settings</h3>
                  <p>Manage and filter your media folders</p>
                </div>
                
                <div className="scan-section">
                  <input 
                    type="text" 
                    placeholder="Custom folder path (optional)" 
                    value={scanPath}
                    onChange={(e) => setScanPath(e.target.value)}
                    className="folder-input"
                  />
                  <button onClick={handleScan} disabled={isScanning} className="scan-button">
                    {isScanning ? 'Scanning...' : 'Scan Folder'}
                  </button>
                </div>

                <div className="scan-section" style={{ marginTop: '1rem' }}>
                  <button onClick={handleConnectDrive} disabled={isDriveConnecting} className="scan-button" style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', backgroundColor: 'var(--primary)' }}>
                    <Cloud size={18} />
                    {isDriveConnecting ? 'Connecting...' : 'Connect Google Drive'}
                  </button>
                </div>

                <div className="folder-list-section">
                  <h4>Indexed Folders</h4>
                  <p className="text-secondary" style={{fontSize: '0.8rem', marginBottom: '0.5rem'}}>Check to restrict voice commands and stats to specific folders.</p>
                  {availableFolders.length === 0 ? (
                    <p className="no-folders">No folders indexed yet.</p>
                  ) : (
                    <ul className="folder-list">
                      {availableFolders.map((folder, idx) => (
                        <li key={idx} className="folder-list-item">
                          <label className="folder-checkbox-label">
                            <input 
                              type="checkbox" 
                              checked={selectedFolders.includes(folder)}
                              onChange={() => toggleFolder(folder)}
                              className="folder-checkbox"
                            />
                            <span className="folder-name" title={folder}>{folder.split(/[\\/]/).pop() || folder}</span>
                          </label>
                          <button 
                            className="browse-btn" 
                            title="Browse folder contents"
                            onClick={() => openFolderBrowser(folder)}
                          >
                            <FolderOpen size={18} />
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>

              {/* Right: Folder Explorer */}
              <div className="stats-panel">
                <FolderExplorer selectedFolders={selectedFolders} onFolderClick={openSmartFolderBrowser} />
              </div>
            </div>
          </motion.div>
        )}
        
        {uiState === 'browser' && (browsingFolder || browsingSmartFolder) && (
          <motion.div 
            key="browser" 
            className="browser-container"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            style={{ width: '100%', height: '100%', padding: '2rem', boxSizing: 'border-box' }}
          >
            <FolderBrowser 
              folderPath={browsingFolder} 
              smartFolder={browsingSmartFolder}
              selectedFolders={selectedFolders}
              onBack={handleClose} 
              API_BASE={API_BASE} 
            />
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
