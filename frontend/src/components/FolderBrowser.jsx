import React, { useState, useEffect } from 'react';
import { ArrowLeft, Play, Image as ImageIcon, Video, Music } from 'lucide-react';

export default function FolderBrowser({ folderPath, smartFolder, selectedFolders = [], onBack, API_BASE }) {
  const [media, setMedia] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchMedia = async () => {
      setLoading(true);
      try {
        const queryParams = new URLSearchParams();
        
        if (folderPath) {
          queryParams.append('folders', folderPath);
        } else if (smartFolder) {
          if (smartFolder.type) queryParams.append('type', smartFolder.type);
          if (smartFolder.subtype) queryParams.append('subtype', smartFolder.subtype);
          selectedFolders.forEach(f => queryParams.append('folders', f));
        }

        const res = await fetch(`${API_BASE}/media?${queryParams.toString()}`);
        if (!res.ok) throw new Error('Failed to fetch media');
        const data = await res.json();
        setMedia(data);
      } catch (err) {
        console.error(err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    if (folderPath || smartFolder) fetchMedia();
  }, [folderPath, smartFolder, selectedFolders, API_BASE]);

  const getIcon = (type) => {
    switch (type) {
      case 'image': return <ImageIcon size={24} />;
      case 'video': return <Video size={24} />;
      case 'audio': return <Music size={24} />;
      default: return null;
    }
  };

  if (loading) {
    return (
      <div className="folder-browser">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={20} /> Back to Dashboard
        </button>
        <div className="unknown-state"><p>Loading media...</p></div>
      </div>
    );
  }

  if (error || media.length === 0) {
    return (
      <div className="folder-browser">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={20} /> Back to Dashboard
        </button>
        <div className="unknown-state">
          <h2>No Media Found</h2>
          <p>This folder doesn't contain any indexed media.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="folder-browser">
      <div className="browser-header">
        <button className="back-btn" onClick={onBack}>
          <ArrowLeft size={20} /> Back
        </button>
        <h2 className="browser-title">
          {folderPath || (smartFolder ? `${smartFolder.subtype ? smartFolder.subtype : ''} ${smartFolder.type}s`.trim() : 'Media Gallery')}
        </h2>
        <span className="media-count">{media.length} items</span>
      </div>

      <div className="gallery-grid">
        {media.map((item, idx) => (
          <div key={idx} className="gallery-card">
            <div className="gallery-preview">
              {item.type === 'image' ? (
                <img 
                  src={`${API_BASE}/media/file/${item.id}`} 
                  alt={item.filename} 
                  loading="lazy" 
                />
              ) : (
                <div className="placeholder-preview">
                  {getIcon(item.type)}
                </div>
              )}
            </div>
            <div className="gallery-info">
              <span className="gallery-filename" title={item.filename}>
                {item.filename}
              </span>
              <span className="gallery-meta">{item.subtype}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
