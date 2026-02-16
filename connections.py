from typing import Dict,Set
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str,Set[WebSocket]] = {}

    def add(self,key:str,websocket: WebSocket):
        if key not in self.active_connections:
            self.active_connections[key] = set()
        self.active_connections[key].add(websocket)

    def remove(self,key:str,websocket: WebSocket):
        if key in self.active_connections:
            self.active_connections[key].discard(websocket)
            if not self.active_connections[key]:
                del self.active_connections[key]

    async def broadcast(self,key: int,message:dict):
        if key in self.active_connections:
            for ws in list(self.active_connections[key]):
                try:
                    await ws.send_json(message)
                except:
                    self.remove(key,ws)

manager = ConnectionManager()