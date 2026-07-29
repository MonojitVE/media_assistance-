import React, { useState, useRef, useEffect } from 'react';
import { SkipBack, SkipForward, Play, Pause, FileWarning } from 'lucide-react';

export default function VideoPlayer({ playlist }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [hasError, setHasError] = useState(false);
  const mediaRef = useRef(null);

  const currentMedia = playlist[currentIndex];
  
  // Reset error state when media changes
  useEffect(() => {
    setHasError(false);
    if (mediaRef.current) {
      mediaRef.current.load();
      if (isPlaying) {
        mediaRef.current.play().catch(err => {
            console.error("Autoplay prevented or error:", err);
            setIsPlaying(false);
        });
      }
    }
  }, [currentIndex]);

  const handleNext = () => {
    if (currentIndex < playlist.length - 1) {
      setCurrentIndex(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  };

  const togglePlay = () => {
    if (!mediaRef.current) return;
    
    if (isPlaying) {
      mediaRef.current.pause();
    } else {
      mediaRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleError = () => {
    setHasError(true);
  };

  if (!currentMedia) return null;

  // Construct a URL for the media. Since filepath is likely local (e.g. C:/...), 
  // browsers won't load it directly. In demo mode, we just show a placeholder if it fails.
  // Assuming the backend doesn't serve these as static files yet, it will error.
  const srcUrl = currentMedia.filepath;

  return (
    <div className="media-player-container">
      <div className="video-wrapper">
        {hasError ? (
           <div className="file-missing">
              <FileWarning size={48} className="file-missing-icon" />
              <p>Media cannot be loaded natively (Local Path)</p>
              <code>{currentMedia.filename}</code>
           </div>
        ) : (
          currentMedia.type === 'audio' ? (
            <audio 
              ref={mediaRef}
              src={srcUrl}
              className="audio-element"
              onEnded={handleNext}
              onError={handleError}
              autoPlay
            />
          ) : (
            <video 
              ref={mediaRef}
              src={srcUrl}
              className="video-element"
              onEnded={handleNext}
              onError={handleError}
              autoPlay
              playsInline
            />
          )
        )}
      </div>

      <div className="player-controls">
        <button className="btn-icon" onClick={handlePrev} disabled={currentIndex === 0}>
          <SkipBack size={24} />
        </button>
        
        <button className="btn-icon" onClick={togglePlay} disabled={hasError}>
          {isPlaying ? <Pause size={32} /> : <Play size={32} />}
        </button>
        
        <button className="btn-icon" onClick={handleNext} disabled={currentIndex === playlist.length - 1}>
          <SkipForward size={24} />
        </button>
      </div>

      <div className="now-playing">
        Playing {currentIndex + 1} of {playlist.length} <br/>
        <strong>{currentMedia.filename}</strong>
      </div>
    </div>
  );
}
