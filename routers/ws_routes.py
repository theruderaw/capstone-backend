# routers/ws_routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from connections import manager

router = APIRouter(prefix="/ws", tags=["WebSocket"])

@router.websocket("/profile/{worker_id}")
async def profile_ws(websocket: WebSocket, worker_id: int):
    """
    WebSocket endpoint clients connect to in order to receive updates
    for a specific worker_id.
    """
    await websocket.accept()
    manager.add(worker_id, websocket)

    try:
        while True:
            # keep the connection alive; we don't expect specific messages from clients here
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.remove(worker_id, websocket)
    except Exception:
        # any other error: ensure cleanup
        manager.remove(worker_id, websocket)