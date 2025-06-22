import React, { useEffect } from 'react';
import { useVoiceAssistant } from '@livekit/components-react';

const VoiceAssistant = () => {
  const { state, audioTrack } = useVoiceAssistant();

  useEffect(() => {
    console.log('Voice Assistant State:', state);
  }, [state]);

  return null; // This component doesn't render anything visible
};

export default VoiceAssistant; 