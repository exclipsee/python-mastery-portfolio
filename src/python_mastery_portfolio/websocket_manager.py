from __future__ import annotations

import asyncio
import logging

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
        self._broadcast_lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("websocket_connected", extra={"total_connections": len(self.active_connections)})

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("websocket_disconnected", extra={"total_connections": len(self.active_connections)})

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.warning("websocket_send_failed", extra={"error": str(e)})
            self.disconnect(websocket)

    async def broadcast(self, message: str) -> None:
        if not self.active_connections:
            return
        async with self._broadcast_lock:
            conns = self.active_connections.copy()
            tasks = [asyncio.create_task(self._safe_send(c, message)) for c in conns]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_send(self, websocket: WebSocket, message: str) -> None:
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            self.disconnect(websocket)
        except Exception as e:
            logger.warning("websocket_broadcast_failed", extra={"error": str(e)})
            self.disconnect(websocket)

    def get_connection_count(self) -> int:
        return len(self.active_connections)
