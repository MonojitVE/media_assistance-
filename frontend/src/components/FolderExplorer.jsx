import React, { useState, useEffect } from 'react';
import { Folder, Image as ImageIcon, Video, Music, FileQuestion } from 'lucide-react';

export default function FolderExplorer({ selectedFolders = [], onFolderClick }) {
  const [stats, setStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const queryParams = new URLSearchParams();
        selectedFolders.forEach(f => queryParams.append('folders', f));
        const res = await fetch(`http://localhost:8000/media/stats?${queryParams.toString()}`);
        if (!res.ok) throw new Error('Failed to fetch stats');
        const data = await res.json();
        setStats(data);
      } catch (err) {
        console.error(err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [selectedFolders]);

  const getIcon = (type) => {
    switch (type) {
      case 'image': return <ImageIcon size={32} className="type-image" />;
      case 'video': return <Video size={32} className="type-video" />;
      case 'audio': return <Music size={32} className="type-audio" />;
      default: return <FileQuestion size={32} />;
    }
  };

  const formatTitle = (type, subtype) => {
    const s = subtype ? subtype.charAt(0).toUpperCase() + subtype.slice(1) : '';
    const t = type.charAt(0).toUpperCase() + type.slice(1);
    return s ? `${s} ${t}s` : `${t}s`;
  };

  if (loading) {
    return <div className="unknown-state"><p>Loading folders...</p></div>;
  }

  if (error || stats.length === 0) {
    return (
      <div className="unknown-state">
        <Folder size={64} color="var(--text-secondary)" />
        <h2>No Folders Found</h2>
        <p>Your library is empty or the backend is unreachable.</p>
      </div>
    );
  }

  return (
    <div className="folder-explorer">
      <h2 style={{ marginBottom: '2rem', textAlign: 'center' }}>Smart Folders</h2>
      <div className="folder-grid">
        {stats.map((stat, idx) => (
          <div key={idx} className="folder-card" onClick={() => onFolderClick && onFolderClick(stat.type, stat.subtype)}>
            <div className="folder-icon-wrap">
              {getIcon(stat.type)}
            </div>
            <div className="folder-details">
              <h3>{formatTitle(stat.type, stat.subtype)}</h3>
              <p>{stat.count} items</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
