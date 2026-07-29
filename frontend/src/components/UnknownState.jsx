import React from 'react';
import { HelpCircle } from 'lucide-react';
import MicButton from './MicButton';

export default function UnknownState({ onTranscript }) {
  return (
    <div className="unknown-state">
      <HelpCircle size={64} color="var(--text-secondary)" />
      <h2>I didn't quite catch that.</h2>
      <p>
        Try saying something like "show me short videos" or "play mixed audio".
      </p>
      
      <div style={{ marginTop: '2rem' }}>
        <MicButton onTranscript={onTranscript} />
      </div>
    </div>
  );
}
