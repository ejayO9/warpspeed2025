import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Room } from 'livekit-client';
import './App.css';

const API_URL = 'http://localhost:8000/api/v1/agent';
const LIVEKIT_URL = 'wss://test9981-isoxrd05.livekit.cloud';

// A unique user ID and room name for the session
const USER_ID = 'user-' + Math.random().toString(36).substring(7);
const ROOM_NAME = 'room-' + Math.random().toString(36).substring(7);
const SESSION_ID = 'session-' + Math.random().toString(36).substring(7);

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isVoiceChatActive, setIsVoiceChatActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const roomRef = useRef(null);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    // Scroll to the bottom of the chat on new messages
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    let assistantMessage = { sender: 'assistant', text: '' };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, session_id: SESSION_ID }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        const parts = buffer.split('\\n\\n');
        buffer = parts.pop(); 

        for (const part of parts) {
          if (part.startsWith('data: ')) {
            const data = JSON.parse(part.substring(6));
            setMessages(prev => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1].text += data.content;
              return newMessages;
            });
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
       setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1].text = "Sorry, I'm having trouble connecting.";
          return newMessages;
        });
    } finally {
      setIsLoading(false);
    }
  };
  
  const toggleVoiceChat = async () => {
    if (isVoiceChatActive) {
      // Stop voice chat
      await axios.post(`${API_URL}/stop-agent`, { room_name: ROOM_NAME });
      if (roomRef.current) {
        await roomRef.current.disconnect();
        roomRef.current = null;
      }
      setIsVoiceChatActive(false);
    } else {
      // Start voice chat
      setIsLoading(true);
      try {
        // Start the agent on the backend
        await axios.post(`${API_URL}/start-agent`, { room_name: ROOM_NAME });

        // Get token to join the room
        const tokenRes = await axios.get(`${API_URL}/livekit-token?user_id=${USER_ID}&room_name=${ROOM_NAME}`);
        const token = tokenRes.data.token;

        const room = new Room();
        roomRef.current = room;
        
        await room.connect(LIVEKIT_URL, token);
        await room.localParticipant.setMicrophoneEnabled(true);
        
        setIsVoiceChatActive(true);
      } catch (error) {
        console.error('Failed to start voice chat:', error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="App">
      <div className="chat-container" ref={chatContainerRef}>
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
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
        <button onClick={toggleVoiceChat} disabled={isLoading}>
          {isVoiceChatActive ? 'Stop Voice Chat' : 'Start Voice Chat'}
        </button>
      </div>
    </div>
  );
}

export default App;
