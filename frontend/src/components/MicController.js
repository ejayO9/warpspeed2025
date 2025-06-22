import { useEffect } from 'react';
import { useLocalParticipant } from '@livekit/components-react';

const MicController = ({ isMuted }) => {
  const { localParticipant } = useLocalParticipant();

  useEffect(() => {
    if (localParticipant) {
      localParticipant.setMicrophoneEnabled(!isMuted);
    }
  }, [isMuted, localParticipant]);

  return null;
};

export default MicController; 