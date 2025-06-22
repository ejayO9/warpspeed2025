import { useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_URL } from '../config';

const useWebSocket = (userId) => {
  const ws = useRef(null);
  const navigate = useNavigate();
  const reconnectTimeout = useRef(null);
  const isConnecting = useRef(false);

  const connect = useCallback(() => {
    if (!userId || isConnecting.current) return;

    // Clean up existing connection
    if (ws.current && ws.current.readyState !== WebSocket.CLOSED) {
      ws.current.close();
    }

    isConnecting.current = true;

    // Create WebSocket URL (remove http:// and add ws://)
    const wsUrl = API_URL.replace('http://', 'ws://').replace('https://', 'wss://');
    const url = `${wsUrl}/agent/ws/${userId}`;
    
    console.log('Connecting to WebSocket:', url);
    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
      isConnecting.current = false;
      // Clear any pending reconnect attempts
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        // Handle redirect messages
        if (data.type === 'redirect' && data.redirect_to) {
          console.log('🔄 Redirect signal received:', data.redirect_to);
          navigate(data.redirect_to);
        }
        // Silently handle connection confirmations and heartbeats
      } catch (error) {
        // Non-JSON message, ignore
      }
    };

    ws.current.onclose = (event) => {
      console.log('WebSocket disconnected', event.code, event.reason);
      isConnecting.current = false;
      
      // Only attempt to reconnect if it wasn't a normal closure and we don't already have a reconnect scheduled
      if (event.code !== 1000 && !reconnectTimeout.current) {
        console.log('Scheduling reconnect in 5 seconds...');
        reconnectTimeout.current = setTimeout(() => {
          reconnectTimeout.current = null;
          connect();
        }, 5000);
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      isConnecting.current = false;
    };
  }, [userId]); // Removed navigate from dependencies

  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
      if (ws.current) {
        ws.current.close(1000, 'Component unmounting');
      }
      isConnecting.current = false;
    };
  }, [userId]); // Only depend on userId, not connect function

  // Return send function if needed
  const sendMessage = useCallback((message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  }, []);

  return { sendMessage };
};

export default useWebSocket; 