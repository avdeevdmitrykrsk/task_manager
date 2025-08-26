import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

router = APIRouter(prefix='/tasks/ws')
logger = logging.getLogger(__name__)


class ConnectionManager:

    def __init__(self):
        self.active_connections: set[WebSocket] = set()

    def add_connection(self, client: WebSocket) -> None:
        self.active_connections.add(client)

    def close_connection(self, client):
        self.active_connections.discard(client)

    async def broadcast(self, data):
        for client in self.active_connections.copy():
            try:
                await client.send_json(data)
            except (WebSocketDisconnect, RuntimeError) as e:
                logger.warning(f'Не удалось отправить сообщение: {e}')
                self.close_connection(client)


manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    return manager


@router.websocket('/')
async def ws(
    websocket: WebSocket,
    connection_manager: ConnectionManager = Depends(get_connection_manager),
):
    await websocket.accept()

    client_addr = f'{websocket.client.host}:{websocket.client.port}'
    logger.info(f'Соединение установлено: {client_addr}')

    connection_manager.add_connection(websocket)
    logger.info(f'Клиент {client_addr} добавлен в менеджер.')

    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        logger.info(f'Клиент отключился: {client_addr}')
    finally:
        connection_manager.close_connection(websocket)
        logger.info(
            f'Соединение с {client_addr} закрыто и удалено из менеджера'
        )
