from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
from collections import defaultdict
from schemas import WSMessage, WSSubscription, WSPublish
import json
import logging

# Use the same logger name as in main.py
logger = logging.getLogger("myapp")

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Dictionary to store active connections: {user_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[int, List[WebSocket]] = defaultdict(list)
        # Subscription registry: {topic_id: {subscriber_user_ids}}
        self.subscriptions: Dict[int, Set[int]] = defaultdict(set)

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if websocket not in self.active_connections[user_id]:
            self.active_connections[user_id].append(websocket)
        logger.info(f"User {user_id} connected via WebSocket. Connection count: {len(self.active_connections[user_id])}")

    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections and websocket in self.active_connections[user_id]:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        # Remove user from all subscriptions
        for topic_id in list(self.subscriptions.keys()):
            if user_id in self.subscriptions[topic_id]:
                self.subscriptions[topic_id].remove(user_id)
        logger.info(f"User {user_id} disconnected. Remaining tracked users: {list(self.active_connections.keys())}")

    async def subscribe(self, subscriber_id: int, topic_id: int):
        self.subscriptions[topic_id].add(subscriber_id)
        logger.info(f"User {subscriber_id} subscribed to topic {topic_id}. Current subscribers for {topic_id}: {self.subscriptions[topic_id]}")
        return True

    async def unsubscribe(self, subscriber_id: int, topic_id: int):
        if topic_id in self.subscriptions and subscriber_id in self.subscriptions[topic_id]:
            self.subscriptions[topic_id].remove(subscriber_id)
            logger.info(f"User {subscriber_id} unsubscribed from topic {topic_id}")
            return True
        return False

    async def publish(self, topic_id: int, data: dict):
        subscriber_ids = self.subscriptions.get(topic_id, set())
        logger.info(f"Publishing to topic {topic_id} for subscribers: {subscriber_ids}")
        for sub_id in subscriber_ids:
            connections = self.active_connections.get(sub_id, [])
            if not connections:
                logger.warning(f"Subscriber {sub_id} is in registry but has no active connections")
                continue
            for conn in connections:
                logger.info(f"Sending message to subscriber {sub_id} on topic {topic_id}")
                await conn.send_json({
                    "topic": topic_id,
                    "data": data
                })
        return True

    async def send_to_user(self, user_id: int, data: dict):
        connections = self.active_connections.get(user_id, [])
        if connections:
            for conn in connections:
                await conn.send_json(data)
            return True
        return False

    async def broadcast_global(self, data: dict):
        logger.info(f"Broadcasting globally to all active users: {list(self.active_connections.keys())}")
        for user_id, connections in self.active_connections.items():
            for conn in connections:
                try:
                    await conn.send_json({
                        "topic": "global",
                        "data": data
                    })
                except Exception as e:
                    logger.error(f"Error broadcasting globally to user {user_id}: {e}")
        return True

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Wait for any incoming text
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id, websocket)

@router.post("/ws/subscribe")
async def ws_subscribe(payload: WSSubscription):
    await manager.subscribe(payload.subscriber_id, payload.topic_id)
    return {"status": "OK", "message": f"User {payload.subscriber_id} is now watching {payload.topic_id}"}

@router.post("/ws/unsubscribe")
async def ws_unsubscribe(payload: WSSubscription):
    success = await manager.unsubscribe(payload.subscriber_id, payload.topic_id)
    if success:
        return {"status": "OK", "message": f"User {payload.subscriber_id} stopped watching {payload.topic_id}"}
    return {"status": "Error", "message": "Subscription not found"}

@router.post("/ws/publish")
async def ws_publish(payload: WSPublish):
    await manager.publish(payload.topic_id, payload.data)
    return {"status": "OK", "message": f"Data published to topic {payload.topic_id}"}

@router.post("/ws/send")
async def send_ws_message(payload: WSMessage):
    success = await manager.send_to_user(payload.user_id, payload.data)
    if success:
        return {"status": "OK", "message": f"Message sent to user {payload.user_id}"}
    return {"status": "Error", "message": f"User {payload.user_id} not connected"}

# Helper for other modules
async def broadcast_status_change(user_id: int, data: dict):
    return await manager.publish(user_id, data)

async def broadcast_alert(data: dict):
    return await manager.broadcast_global(data)
