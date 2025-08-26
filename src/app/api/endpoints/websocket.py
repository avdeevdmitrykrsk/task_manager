import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)

router = APIRouter(prefix='/tasks/ws')
logger = logging.getLogger(__name__)

VALID_ROOM_KEY = 'room_id'


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[str, set[WebSocket]] = dict()

    async def validate_query_params(self, params: dict) -> dict:
        errors = []
        valid_key = VALID_ROOM_KEY

        for key, value in params.items():
            if value not in self.active_connections.keys():
                errors.append(f'Комнаты с id "{value}" не существует.')

            if key != valid_key:
                errors.append(
                    f'Невалидный параметр "{key}",'
                    f' используйте "{valid_key}"'
                )

        if errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='; '.join(errors),
            )

        return params

    async def add_connection(self, client: WebSocket, rooms_id: list) -> None:
        for room_id in rooms_id:
            try:
                self.active_connections[room_id].add(client)
            except KeyError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f'Комната с id "{room_id}" уже закрыта.',
                )

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

    query_params: dict = await websocket.query_params.dict()
    if query_params:
        await manager.validate_query_params(query_params)

    await manager.add_connection(websocket, list(query_params.values()))

    try:
        while True:
            try:
                await websocket.receive_json()
            except WebSocketDisconnect:
                break
    finally:
        await manager.close_connection(websocket)
