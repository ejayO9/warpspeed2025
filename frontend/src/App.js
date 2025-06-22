import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import RecommendationPage from './pages/RecommendationPage';
import HelloPage from './pages/HelloPage';
import AnalysingPage from './pages/AnalysingPage';
import './App.css';

function App() {
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