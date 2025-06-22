# LiveKit Setup Guide

## Voice Chat Setup

The voice chat feature requires a LiveKit server. You have several options:

### Option 1: LiveKit Cloud (Recommended for production)
1. Sign up at https://livekit.io
2. Create a new project
3. Get your WebSocket URL (format: `wss://your-app.livekit.cloud`)
4. Update your `.env` file:
   ```
   REACT_APP_LIVEKIT_URL=wss://your-app.livekit.cloud
   ```

### Option 2: Local Development Server
1. Install LiveKit server:
   ```bash
   # macOS
   brew install livekit

   # Windows/Linux - Download from https://github.com/livekit/livekit/releases
   ```

2. Create a config file `livekit.yaml`:
   ```yaml
   port: 7880
   rtc:
     tcp_port: 7881
     port_range_start: 50000
     port_range_end: 60000
   keys:
     APIwhatever: secretkey
   ```

3. Run LiveKit server:
   ```bash
   livekit-server --config livekit.yaml --dev
   ```

4. Update your `.env` file:
   ```
   REACT_APP_LIVEKIT_URL=ws://localhost:7880
   ```

### Option 3: Docker
```bash
docker run --rm \
  -p 7880:7880 \
  -p 7881:7881 \
  -p 7882:7882/udp \
  livekit/livekit-server \
  --dev \
  --node-ip=127.0.0.1
```

## Backend Configuration

Make sure your backend `.env` file has the LiveKit credentials:
```
LIVEKIT_API_KEY=APIwhatever
LIVEKIT_API_SECRET=secretkey
LIVEKIT_URL=ws://localhost:7880  # or your cloud URL
```

## Troubleshooting

1. **Immediate disconnection**: Check if LiveKit server is running and accessible
2. **Token errors**: Verify API key and secret match between backend and LiveKit server
3. **Connection refused**: Check firewall settings and ensure ports are open
4. **Browser permissions**: Allow microphone access when prompted 