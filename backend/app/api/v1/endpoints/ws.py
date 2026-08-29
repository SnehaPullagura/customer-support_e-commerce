"""
WebSocket live gateway for real-time conversation streaming and presence.
"""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.conversation_service import ws_manager

router = APIRouter()


@router.websocket("/chat/{conversation_id}")
async def websocket_chat_endpoint(websocket: WebSocket, conversation_id: str):
    await ws_manager.connect(conversation_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                # Broadcast typing or presence signals
                action = payload.get("action", "ECHO")
                await ws_manager.broadcast_json(conversation_id, payload)
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(conversation_id, websocket)
