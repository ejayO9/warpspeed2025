
import React, { useState, useMemo, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  ControlBar,
  useVoiceAssistant,
} from '@livekit/components-react';
import '@livekit/components-styles';


import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import RecommendationPage from './pages/RecommendationPage';
import HelloPage from './pages/HelloPage';
import AnalysingPage from './pages/AnalysingPage';

import './App.css';

function App() {

  //previous code 

  // const [messages, setMessages] = useState([]);
  // const [input, setInput] = useState('');
  // const [isVoiceChatActive, setIsVoiceChatActive] = useState(false);
  // const [isLoading, setIsLoading] = useState(false);
  // const [liveKitToken, setLiveKitToken] = useState('');
  // const [roomName, setRoomName] = useState('');
  // const messagesEndRef = useRef(null);

  // // A unique user ID for the session
  // const userId = useMemo(() => 'user-' + Math.random().toString(36).substring(7), []);

  // // Auto-scroll to bottom when new messages arrive
  // const scrollToBottom = () => {
  //   messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  // };

  // useEffect(() => {
  //   scrollToBottom();
  // }, [messages]);

  // const handleSend = async () => {
  //   if (!input.trim() || isLoading) return;
    
  //   console.log('Sending message:', input);
    
  //   const currentInput = input; // Store input before clearing

  //   const userMessage = { sender: 'user', text: input, timestamp: new Date() };
  //   setMessages((prev) => [...prev, userMessage]);
  //   setInput('');
  //   setIsLoading(true);

  //   const assistantMessage = { sender: 'assistant', text: '', timestamp: new Date() };
  //   setMessages((prev) => [...prev, assistantMessage]);

  //   try {
  //     const response = await fetch(`${API_URL}/chat`, {
  //       method: 'POST',
  //       headers: { 'Content-Type': 'application/json' },
  //       body: JSON.stringify({ 
  //         message: currentInput, // Use stored input
  //         session_id: userId, // Using userId as session_id for consistency
  //         user_id: 1 // TODO: Replace with actual user ID from authentication
  //       }),
  //     });

  //     const reader = response.body.getReader();
  //     const decoder = new TextDecoder();
  //     let buffer = '';

  //     while (true) {
  //       const { value, done } = await reader.read();
  //       if (done) break;

  //       buffer += decoder.decode(value, { stream: true });

  //       const parts = buffer.split('\n\n');
  //       buffer = parts.pop();

  //       for (const part of parts) {
  //         if (part.startsWith('data: ')) {
  //           try {
  //             const data = JSON.parse(part.substring(6));
  //             setMessages((prev) => {
  //               const newMessages = [...prev];
  //               // Replace the content instead of appending for complete messages
  //               newMessages[newMessages.length - 1].text = data.content;
  //               return newMessages;
  //             });
  //           } catch (e) {
  //             console.error('Error parsing JSON:', part);
  //           }
  //         }
  //       }
  //     }
      
  //     // Process any remaining buffer
  //     if (buffer.trim() && buffer.startsWith('data: ')) {
  //       try {
  //         const data = JSON.parse(buffer.substring(6));
  //         setMessages((prev) => {
  //           const newMessages = [...prev];
  //           newMessages[newMessages.length - 1].text = data.content;
  //           return newMessages;
  //         });
  //       } catch (e) {
  //         console.error('Error parsing final buffer:', buffer);
  //       }
  //     }
  //   } catch (error) {
  //     console.error('Error sending message:', error);
  //     setMessages((prev) => {
  //       const newMessages = [...prev];
  //       newMessages[newMessages.length - 1].text = "Sorry, I'm having trouble connecting. Error: " + error.message;
  //       return newMessages;
  //     });
  //   } finally {
  //     console.log('Resetting loading state');
  //     setIsLoading(false);
  //   }
  // };

  // const startVoiceChat = async () => {
  //   setIsLoading(true);
  //   try {
  //     const newRoomName = 'room-' + Math.random().toString(36).substring(7);
  //     setRoomName(newRoomName);

  //     // Get token to join the room (agent will be automatically dispatched by LiveKit)
  //     const tokenRes = await axios.get(`${API_URL}/livekit-token?user_id=${userId}&room_name=${newRoomName}`);
  //     setLiveKitToken(tokenRes.data.token);

  //     setIsVoiceChatActive(true);
  //   } catch (error) {
  //     console.error('Failed to start voice chat:', error);
  //   } finally {
  //     setIsLoading(false);
  //   }
  // };

  // const stopVoiceChat = async () => {
  //   // Simply disconnect from the room - no need to stop the agent
  //   setIsVoiceChatActive(false);
  //   setLiveKitToken('');
  //   setRoomName('');
  // };

  // return (
  //   <div className="App">
  //     <div className="chat-container">
  //       <div className="messages-wrapper">
  //         {messages.length === 0 && (
  //           <div className="welcome-message">
  //             <h2>Welcome to FinBuddy!</h2>
  //             <p>I'm here to help you with your financial planning and loan analysis.</p>
  //           </div>
  //         )}
  //         {messages.map((msg, index) => (
  //           <div key={index} className={`message-row ${msg.sender}`}>
  //             <div className="message-avatar">
  //               {msg.sender === 'user' ? '👤' : '🤖'}
  //             </div>
  //             <div className="message-content">
  //               <div className="message-header">
  //                 <span className="message-sender">
  //                   {msg.sender === 'user' ? 'You' : 'FinBuddy'}
  //                 </span>
  //                 {msg.timestamp && (
  //                   <span className="message-time">
  //                     {new Date(msg.timestamp).toLocaleTimeString([], { 
  //                       hour: '2-digit', 
  //                       minute: '2-digit' 
  //                     })}
  //                   </span>
  //                 )}
  //               </div>
  //               <div className={`message-text ${msg.sender}`}>
  //                 {msg.text || (isLoading && msg.sender === 'assistant' ? (
  //                   <div className="typing-indicator">
  //                     <span></span>
  //                     <span></span>
  //                     <span></span>
  //                   </div>
  //                 ) : '')}
  //               </div>
  //             </div>
  //           </div>
  //         ))}
  //         <div ref={messagesEndRef} />
  //       </div>
  //       {isVoiceChatActive && liveKitToken && (
  //         <LiveKitRoom
  //           serverUrl={LIVEKIT_URL}
  //           token={liveKitToken}
  //           connect={true}
  //           audio={true}
  //           onDisconnected={stopVoiceChat}
  //         >
  //           <VoiceAssistant />
  //           <RoomAudioRenderer />
  //         </LiveKitRoom>
  //       )}

  return (
    <Router>
      <div className="App">
        <nav className="bg-white shadow-sm p-4">
          <div className="max-w-7xl mx-auto flex justify-center items-center gap-12">
            <Link to="/" className="text-slate-700 hover:text-purple-600 transition-colors">
              Recommendation
            </Link>
            <Link to="/hello" className="text-slate-700 hover:text-purple-600 transition-colors">
              Chat
            </Link>
            <Link to="/analysis" className="text-slate-700 hover:text-purple-600 transition-colors">
              Analysis
            </Link>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<RecommendationPage />} />
          <Route path="/hello" element={<HelloPage />} />
          <Route path="/analysis" element={<AnalysingPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;