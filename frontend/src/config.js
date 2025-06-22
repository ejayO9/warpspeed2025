// API Configuration
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// LiveKit URL - Update this with your actual LiveKit server URL
// For LiveKit Cloud: wss://your-app.livekit.cloud
// For local development: ws://localhost:7880 (if running LiveKit locally)
const LIVEKIT_URL = process.env.REACT_APP_LIVEKIT_URL || 'wss://test9981-isoxrd05.livekit.cloud';

export { API_URL, LIVEKIT_URL }; 