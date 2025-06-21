import React, { useState, useMemo } from 'react';
import axios from 'axios';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  ControlBar,
  useVoiceAssistant,
} from '@livekit/components-react';
import '@livekit/components-styles';
import './App.css';

const API_URL = 'http://localhost:8000/api/v1/agent';
// IMPORTANT: Replace with your actual LiveKit URL
const LIVEKIT_URL = 'wss://test9981-isoxrd05.livekit.cloud'; 

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isVoiceChatActive, setIsVoiceChatActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [liveKitToken, setLiveKitToken] = useState('');
  const [roomName, setRoomName] = useState('');

  // A unique user ID for the session
  const userId = useMemo(() => 'user-' + Math.random().toString(36).substring(7), []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const assistantMessage = { sender: 'assistant', text: '' };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, session_id: 'your-session-id' }), // Use a consistent session ID
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split('\n\n');
        buffer = parts.pop();

        for (const part of parts) {
          if (part.startsWith('data: ')) {
            try {
              const data = JSON.parse(part.substring(6));
              setMessages((prev) => {
                const newMessages = [...prev];
                newMessages[newMessages.length - 1].text += data.content;
                return newMessages;
              });
            } catch (e) {
              console.error('Error parsing JSON:', part);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1].text = "Sorry, I'm having trouble connecting.";
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const startVoiceChat = async () => {
    setIsLoading(true);
    try {
      const newRoomName = 'room-' + Math.random().toString(36).substring(7);
      setRoomName(newRoomName);

      // Get token to join the room (agent will be automatically dispatched by LiveKit)
      const tokenRes = await axios.get(`${API_URL}/livekit-token?user_id=${userId}&room_name=${newRoomName}`);
      setLiveKitToken(tokenRes.data.token);

      setIsVoiceChatActive(true);
    } catch (error) {
      console.error('Failed to start voice chat:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const stopVoiceChat = async () => {
    // Simply disconnect from the room - no need to stop the agent
    setIsVoiceChatActive(false);
    setLiveKitToken('');
    setRoomName('');
  };

  return (
    <div className="App">
      <div className="chat-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        {isVoiceChatActive && liveKitToken && (
          <LiveKitRoom
            serverUrl={LIVEKIT_URL}
            token={liveKitToken}
            connect={true}
            audio={true}
            onDisconnected={stopVoiceChat}
          >
            <VoiceAssistant />
            <RoomAudioRenderer />
          </LiveKitRoom>
        )}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type a message..."
          disabled={isLoading || isVoiceChatActive}
        />
        <button onClick={handleSend} disabled={isLoading || isVoiceChatActive}>
          Send
        </button>
        <button onClick={isVoiceChatActive ? stopVoiceChat : startVoiceChat} disabled={isLoading}>
          {isVoiceChatActive ? 'Stop Voice Chat' : 'Start Voice Chat'}
        </button>
      </div>
    </div>
  );
}

// A new component to handle the voice assistant UI and state
function VoiceAssistant() {
  const { state, agent, transcript } = useVoiceAssistant();

  let message = '...';
  // FIX: Compare state against string literals instead of an enum
  if (state === 'listening') {
    message = 'Listening...';
  } else if (state === 'thinking') {
    message = 'Thinking...';
  } else if (state === 'speaking') {
    message = agent?.name ? `${agent.name} is speaking...` : 'Assistant is speaking...';
  }

  return (
    <div className="voice-assistant-container">
      <div className="voice-assistant-status">{message}</div>
      <div className="voice-assistant-transcript">{transcript}</div>
      <ControlBar
        variation="minimal"
        controls={{
          microphone: true,
          settings: false,
          camera: false,
          chat: false,
          screenShare: false,
          leave: true,
        }}
      />
    </div>
  );
}

export default App;