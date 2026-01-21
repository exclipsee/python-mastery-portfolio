"""WebSocket connection manager for real-time broadcasting."""

from __future__ import annotations

import asyncio
import logging

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasting."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
        self._broadcast_lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(
            "websocket_connected", extra={"total_connections": len(self.active_connections)}
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(
            "websocket_disconnected", extra={"total_connections": len(self.active_connections)}
        )

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.warning("websocket_send_failed", extra={"error": str(e)})
            self.disconnect(websocket)

    async def broadcast(self, message: str) -> None:
        """Broadcast a message to all connected WebSockets."""
        if not self.active_connections:
            return

        async with self._broadcast_lock:
            # Copy the list to avoid modification during iteration
            connections = self.active_connections.copy()

            # Send to all connections concurrently
            tasks = []
            for connection in connections:
                task = asyncio.create_task(self._safe_send(connection, message))
                tasks.append(task)

            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_send(self, websocket: WebSocket, message: str) -> None:
        """Safely send a message, handling disconnections."""
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            self.disconnect(websocket)
        except Exception as e:
            logger.warning("websocket_broadcast_failed", extra={"error": str(e)})
            self.disconnect(websocket)

    def get_connection_count(self) -> int:
        """Get the current number of active connections."""
        return len(self.active_connections)
