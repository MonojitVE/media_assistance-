import React, { useState, useEffect } from 'react';
import { SkipBack, SkipForward, FileWarning } from 'lucide-react';

export default function Slideshow({ playlist }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [hasError, setHasError] = useState(false);
  const currentImage = playlist[currentIndex];

  useEffect(() => {
    setHasError(false);
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % playlist.length);
    }, 4000); // 4 seconds per slide

    return () => clearInterval(interval);
  }, [currentIndex, playlist.length]);

  const handleNext = () => {
    setCurrentIndex((prev) => (prev + 1) % playlist.length);
  };

  const handlePrev = () => {
    setCurrentIndex((prev) => (prev - 1 + playlist.length) % playlist.length);
  };

  const handleError = () => {
    setHasError(true);
  };

  if (!currentImage) return null;

  return (
    <div className="slideshow-container">
      <div className="slide-wrapper">
        {hasError ? (
           <div className="file-missing">
              <FileWarning size={48} className="file-missing-icon" />
              <p>Image cannot be loaded natively (Local Path)</p>
              <code>{currentImage.filename}</code>
           </div>
        ) : (
          <img 
            src={currentImage.filepath} 
            alt={currentImage.filename} 
            className="slide-image"
            onError={handleError}
          />
        )}
      </div>

      <div className="player-controls">
        <button className="btn-icon" onClick={handlePrev}>
          <SkipBack size={24} />
        </button>
        <span className="now-playing" style={{ margin: 0 }}>
          {currentIndex + 1} / {playlist.length}
        </span>
        <button className="btn-icon" onClick={handleNext}>
          <SkipForward size={24} />
        </button>
      </div>
      
      <div className="now-playing">
        <strong>{currentImage.filename}</strong>
      </div>
    </div>
  );
}
