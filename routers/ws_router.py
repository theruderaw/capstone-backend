from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from services.info_service import status_of_worker
import asyncio

router = APIRouter(prefix="/ws",tags=["ws"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket)

    try:
        print("WS CONNECTED:", user_id)

        # ✅ run sync DB call safely
        data = await asyncio.to_thread(status_of_worker, user_id)

        working = data[0]["working"] if data else None

        await websocket.send_json({
            "type": "working_update",
            "user_id": user_id,
            "working": working
        })

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        print("WS DISCONNECTED")
        manager.disconnect(websocket)

    except Exception as e:
        print("WS ERROR:", e)
        await websocket.close()
