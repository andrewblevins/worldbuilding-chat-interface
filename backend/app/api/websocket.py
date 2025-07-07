"""
WebSocket endpoint for real-time communication.
"""

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from typing import List


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSockets."""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                # Remove broken connection
                self.disconnect(connection)


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint."""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            
            # Echo message back (placeholder)
            await manager.send_personal_message(f"Echo: {data}", websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket disconnected") 