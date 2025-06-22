import React, { useState, useEffect, useRef } from 'react';
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
import useWebSocket from './hooks/useWebSocket';

import './App.css';

// Wrapper component that uses WebSocket inside Router context
function AppContent({ userId }) {
  // Establish WebSocket connection inside Router context
  useWebSocket(userId);
  
  return (
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
        <Route path="/hello" element={<HelloPage userId={userId} />} />
        <Route path="/analysis" element={<AnalysingPage />} />
      </Routes>
    </div>
  );
}

function App() {
  // Use consistent user_id: 1 for all connections
  const userId = 1;

  return (
    <Router>
      <AppContent userId={userId} />
    </Router>
  );
}

export default App;