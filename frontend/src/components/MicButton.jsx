import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff } from 'lucide-react';

export default function MicButton({ onTranscript }) {
  const [isListening, setIsListening] = useState(false);
  const [status, setStatus] = useState('');
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Initialize Web Speech API
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setStatus('Listening...');
      };

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setStatus('');
        onTranscript(transcript);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
        setStatus('');
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        if (status === 'Listening...') {
            setStatus('');
        }
      };
    } else {
      setStatus('Speech recognition not supported in this browser.');
    }
  }, [onTranscript]);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      recognitionRef.current?.start();
    }
  };

  return (
    <div className="mic-container">
      <button 
        className={`mic-button ${isListening ? 'listening' : ''}`}
        onClick={toggleListening}
        aria-label={isListening ? "Stop listening" : "Start listening"}
      >
        {isListening ? (
          <Mic className="icon" size={40} />
        ) : (
          <MicOff className="icon" size={40} color="var(--text-secondary)" />
        )}
      </button>
      <div className={`mic-status ${isListening ? 'listening' : ''}`}>
        {status || 'Tap to speak'}
      </div>
    </div>
  );
}
