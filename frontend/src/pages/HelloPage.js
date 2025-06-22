import React, { useState, useMemo, useEffect, useRef } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useVoiceAssistant,
} from '@livekit/components-react';
import '@livekit/components-styles';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { AudioLines, Send, Mic, MicOff, Phone, PhoneOff } from 'lucide-react';
import VoiceAssistant from '../components/VoiceAssistant';
import MicController from '../components/MicController';
import { API_URL, LIVEKIT_URL } from '../config';

const HelloPage = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isVoiceChatActive, setIsVoiceChatActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [liveKitToken, setLiveKitToken] = useState('');
  const [roomName, setRoomName] = useState('');
  const [isMicMuted, setIsMicMuted] = useState(false);
  const messagesEndRef = useRef(null);

  // A unique user ID for the session
  const userId = useMemo(() => 'user-' + Math.random().toString(36).substring(7), []);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    console.log('Sending message:', input);
    
    const currentInput = input; // Store input before clearing

    const userMessage = { sender: 'user', text: input, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const assistantMessage = { sender: 'assistant', text: '', timestamp: new Date() };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      const response = await fetch(`${API_URL}/agent/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: currentInput,
          session_id: userId, // Using userId as session_id for consistency
          user_id: 1 // TODO: Replace with actual user ID from authentication
        }),
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
              
              // Handle redirect event
              if (data.type === 'redirect' && data.redirect_to) {
                console.log('Redirect signal received:', data.redirect_to);
                navigate(data.redirect_to);
                return;
              }
              
              // Handle regular message
              if (data.content) {
                setMessages((prev) => {
                  const newMessages = [...prev];
                  // Replace the content instead of appending for complete messages
                  newMessages[newMessages.length - 1].text = data.content;
                  return newMessages;
                });
              }
            } catch (e) {
              console.error('Error parsing JSON:', part);
            }
          }
        }
      }
      
      // Process any remaining buffer
      if (buffer.trim() && buffer.startsWith('data: ')) {
        try {
          const data = JSON.parse(buffer.substring(6));
          
          // Handle redirect event
          if (data.type === 'redirect' && data.redirect_to) {
            console.log('Redirect signal received from final buffer:', data.redirect_to);
            navigate(data.redirect_to);
            return;
          }
          
          // Handle regular message
          if (data.content) {
            setMessages((prev) => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1].text = data.content;
              return newMessages;
            });
          }
        } catch (e) {
          console.error('Error parsing final buffer:', buffer);
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1].text = "Sorry, I'm having trouble connecting. Error: " + error.message;
        return newMessages;
      });
    } finally {
      console.log('Resetting loading state');
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startVoiceChat = async () => {
    setIsLoading(true);
    try {
      // Check if LiveKit URL is properly configured
      if (LIVEKIT_URL.includes('your-livekit-server') || !LIVEKIT_URL) {
        throw new Error('LiveKit server URL is not configured. Please update REACT_APP_LIVEKIT_URL in your .env file or the config.js file.');
      }

      const newRoomName = 'room-' + Math.random().toString(36).substring(7);
      setRoomName(newRoomName);

      console.log('Starting voice chat with room:', newRoomName);
      console.log('LiveKit URL:', LIVEKIT_URL);

      // Get token to join the room (agent will be automatically dispatched by LiveKit)
      const tokenRes = await axios.get(`${API_URL}/agent/livekit-token?user_id=${userId}&room_name=${newRoomName}`);
      console.log('Received token:', tokenRes.data.token);
      
      setLiveKitToken(tokenRes.data.token);
      setIsVoiceChatActive(true);
    } catch (error) {
      console.error('Failed to start voice chat:', error);
      alert(`Failed to start voice chat: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const stopVoiceChat = async () => {
    console.log('Stopping voice chat');
    // Simply disconnect from the room - no need to stop the agent
    setIsVoiceChatActive(false);
    setLiveKitToken('');
    setRoomName('');
  };

  const handleConnectionError = (error) => {
    console.error('LiveKit connection error:', error);
    alert(`Voice chat connection error: ${error?.message || 'Unknown error'}`);
    stopVoiceChat();
  };

  const toggleMic = () => {
    setIsMicMuted(prev => !prev);
    console.log('Mic muted:', !isMicMuted);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-start justify-center p-8">
      <div className="w-full max-w-2xl">
        <Card className="bg-white rounded-2xl shadow-xl h-[80vh] flex flex-col">
          <CardHeader className="border-b border-slate-100 flex flex-row items-center justify-between">
            <CardTitle className="font-serif text-slate-800">Financial Assistant</CardTitle>
            <div className="flex items-center gap-2">
              <button
                onClick={toggleMic}
                className={`p-2 rounded-full transition-colors ${
                  isMicMuted
                    ? 'bg-red-100 text-red-600 hover:bg-red-200'
                    : 'bg-green-100 text-green-600 hover:bg-green-200'
                }`}
                aria-label={isMicMuted ? 'Unmute microphone' : 'Mute microphone'}
                title={isMicMuted ? 'Click to unmute microphone' : 'Click to mute microphone'}
              >
                {isMicMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>
              <button
                onClick={isVoiceChatActive ? stopVoiceChat : startVoiceChat}
                disabled={isLoading}
                className={`p-2 rounded-full transition-colors ${
                  isVoiceChatActive
                    ? 'bg-red-100 text-red-600 hover:bg-red-200'
                    : 'bg-purple-100 text-purple-600 hover:bg-purple-200'
                } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                aria-label={isVoiceChatActive ? 'End voice chat' : 'Start voice chat'}
                title={isVoiceChatActive ? 'Click to end voice chat' : 'Click to start voice chat'}
              >
                {isVoiceChatActive ? <PhoneOff className="w-5 h-5" /> : <Phone className="w-5 h-5" />}
              </button>
            </div>
          </CardHeader>
          
          {/* Chat Messages Area */}
          <div className="flex-1 p-6 overflow-y-auto">
            {messages.length === 0 ? (
              <div className="text-center text-slate-500 mt-16">
                <AudioLines className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                <p className="text-lg font-medium">Welcome to FinBuddy!</p>
                <p className="text-sm mt-2">I'm here to help you with your financial planning and loan analysis.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg, index) => (
                  <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[70%] rounded-lg p-3 ${
                      msg.sender === 'user'
                        ? 'bg-purple-600 text-white'
                        : 'bg-slate-100 text-slate-800'
                    }`}>
                      <div className="text-sm font-medium mb-1">
                        {msg.sender === 'user' ? 'You' : 'FinBuddy'}
                      </div>
                      <div className="whitespace-pre-wrap">
                        {msg.text || (isLoading && msg.sender === 'assistant' ? (
                          <div className="flex space-x-1">
                            <span className="animate-bounce">●</span>
                            <span className="animate-bounce" style={{ animationDelay: '0.1s' }}>●</span>
                            <span className="animate-bounce" style={{ animationDelay: '0.2s' }}>●</span>
                          </div>
                        ) : '')}
                      </div>
                      {msg.timestamp && (
                        <div className="text-xs opacity-70 mt-1">
                          {new Date(msg.timestamp).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
          
          {/* Input Area */}
          <div className="p-4 border-t border-slate-100">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  disabled={isLoading || isVoiceChatActive}
                  className="w-full bg-white border border-slate-200 rounded-full py-3 pl-4 pr-12 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-slate-700 placeholder-slate-400 disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    backgroundColor: 'white',
                    color: '#1e293b',
                    borderColor: '#e2e8f0',
                    '--tw-ring-color': 'rgba(168, 85, 247, 0.5)'
                  }}
                />
                <button 
                  onClick={handleSend}
                  disabled={isLoading || !input.trim() || isVoiceChatActive}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 text-slate-400 hover:text-purple-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Send message"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
            {isVoiceChatActive && (
              <div className="mt-2 text-center text-sm text-slate-500">
                Voice chat is active. Speak to interact with FinBuddy.
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* LiveKit Room - Hidden but active when voice chat is on */}
      {isVoiceChatActive && liveKitToken && (
        <div style={{ display: 'none' }}>
          <LiveKitRoom
            serverUrl={LIVEKIT_URL}
            token={liveKitToken}
            connect={true}
            audio={true}
            onDisconnected={() => {
              console.log('LiveKit disconnected');
              stopVoiceChat();
            }}
            onError={handleConnectionError}
            options={{
              adaptiveStream: true,
              dynacast: true,
              publishDefaults: {
                audioPreset: {
                  maxBitrate: 32000,
                },
                stopMicTrackOnMute: false,
              },
              reconnectPolicy: {
                maxRetries: 3,
                nextRetryDelayInMs: (retryCount) => retryCount * 1000,
              },
            }}
          >
            <VoiceAssistant />
            <MicController isMuted={isMicMuted} />
            <RoomAudioRenderer />
          </LiveKitRoom>
        </div>
      )}
    </div>
  );
};

export default HelloPage;
