import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

router = APIRouter(prefix='/tasks/ws')
logger = logging.getLogger(__name__)


class ConnectionManager:

    def __init__(self):
        self.active_connections: set = set()

    async def add_connection(self, client):
        self.active_connections.add(client)

    async def close_connection(self, client):
        self.active_connections.discard(client)

    async def broadcast(self, data):
        for client in self.active_connections.copy():
            try:
                await client.send_json(data)
            except (WebSocketDisconnect, RuntimeError):
                if client in self.active_connections:
                    await self.close_connection(client)


manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    return manager


@router.websocket('/')
async def ws(
    websocket: WebSocket,
    manager: ConnectionManager = Depends(get_connection_manager),
):
    await websocket.accept()
    await manager.add_connection(websocket)

    try:
        while True:
            try:
                await websocket.receive_json()
            except WebSocketDisconnect:
                break
    finally:
        await manager.close_connection(websocket)
