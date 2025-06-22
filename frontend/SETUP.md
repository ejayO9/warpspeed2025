# Frontend Setup Guide

## Environment Variables

Create a `.env` file in the frontend directory with the following variables:

```bash
# Backend API URL
REACT_APP_API_URL=http://localhost:8000/api/v1

# LiveKit WebSocket URL
REACT_APP_LIVEKIT_URL=wss://your-livekit-server.com
```

## Installation

1. Install dependencies:
```bash
npm install
```

2. Make sure the backend is running on port 8000

3. Start the development server:
```bash
npm start
```

## Features

- **Text Chat**: Type messages to interact with FinBuddy
- **Voice Chat**: Click the microphone button to start voice interaction
- **Persistent Conversations**: Chat history is maintained across sessions using the same session ID
- **Real-time Streaming**: Responses stream in real-time as the agent processes your queries

## Notes

- The chat uses LangGraph's memory system to maintain conversation context
- Voice chat requires a properly configured LiveKit server
- Make sure to update the `user_id` in the code when implementing authentication 