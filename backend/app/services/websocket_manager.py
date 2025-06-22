from typing import List, Dict
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user: {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user: {user_id}")

    async def send_personal_message(self, message: str, user_id: str):
        """Send a message to all connections for a specific user"""
        if user_id in self.active_connections:
            # Send to all connections for this user (they might have multiple tabs)
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    # Remove dead connections
                    self.disconnect(connection, user_id)

    async def send_redirect(self, user_id: str, redirect_to: str):
        """Send a redirect command to a specific user"""
        message = json.dumps({
            "type": "redirect",
            "redirect_to": redirect_to
        })
        await self.send_personal_message(message, user_id)
        logger.info(f"Sent redirect to {redirect_to} for user {user_id}")

    async def broadcast(self, message: str):
        """Send a message to all connected clients"""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id}: {e}")
                    self.disconnect(connection, user_id)

# Create a singleton instance
manager = ConnectionManager() 