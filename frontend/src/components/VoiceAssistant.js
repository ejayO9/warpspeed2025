import React, { useEffect } from 'react';
import { useDataChannel, useConnectionState } from '@livekit/components-react';
import { useNavigate } from 'react-router-dom';
import { ConnectionState } from 'livekit-client';

const VoiceAssistant = () => {
  const navigate = useNavigate();
  const { message, send } = useDataChannel();
  const connectionState = useConnectionState();

  useEffect(() => {
    if (message) {
      try {
        const data = JSON.parse(message);
        console.log('LiveKit data message received:', data);
        
        // Handle redirect event
        if (data.type === 'redirect' && data.redirect_to) {
          console.log('Voice chat redirect signal received:', data.redirect_to);
          navigate(data.redirect_to);
        }
      } catch (e) {
        console.error('Error parsing LiveKit data message:', e);
      }
    }
  }, [message, navigate]);

  return (
    <div style={{ display: 'none' }}>
      {connectionState === ConnectionState.Connected && (
        <span>Voice Assistant Connected</span>
      )}
    </div>
  );
};

export default VoiceAssistant; 