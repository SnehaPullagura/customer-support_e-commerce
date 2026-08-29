"""
Omnichannel Conversation, Messaging, and WebSocket Gateway Service.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.core.exceptions import EntityNotFoundError, AuthorizationError
from app.models.conversation import (
    Conversation,
    Message,
    MessageAttachment,
    MessageReadReceipt,
    ConversationParticipant,
)
from app.models.case import Case, CaseTimelineEvent
from app.schemas.conversation import MessageCreate


class ConnectionManager:
    """Manages active WebSocket connections per conversation."""

    def __init__(self) -> None:
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, conversation_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = set()
        self.active_connections[conversation_id].add(websocket)

    def disconnect(self, conversation_id: str, websocket: WebSocket) -> None:
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].discard(websocket)
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

    async def broadcast_json(self, conversation_id: str, data: dict) -> None:
        if conversation_id in self.active_connections:
            dead_sockets = []
            for connection in self.active_connections[conversation_id]:
                try:
                    await connection.send_json(data)
                except Exception:
                    dead_sockets.append(connection)
            for dead in dead_sockets:
                self.disconnect(conversation_id, dead)


ws_manager = ConnectionManager()


class ConversationService:
    @staticmethod
    async def get_or_create_conversation(
        session: AsyncSession, case_id: str, channel: str = "WEB_CHAT"
    ) -> Conversation:
        conv = await session.scalar(
            select(Conversation).where(Conversation.case_id == case_id, Conversation.channel == channel)
        )
        if not conv:
            conv = Conversation(
                case_id=case_id,
                channel=channel,
                status="OPEN",
            )
            session.add(conv)
            await session.commit()
            await session.refresh(conv)
        return conv

    @staticmethod
    async def get_conversation(session: AsyncSession, conversation_id: str) -> Conversation:
        conv = await session.scalar(
            select(Conversation)
            .options(
                selectinload(Conversation.messages).selectinload(Message.attachments),
                selectinload(Conversation.participants),
            )
            .where(Conversation.id == conversation_id)
        )
        if not conv:
            raise EntityNotFoundError("Conversation", conversation_id)
        return conv

    @staticmethod
    async def send_message(
        session: AsyncSession,
        conversation_id: str,
        sender_type: str,  # CUSTOMER, AGENT, BOT, SYSTEM
        sender_name: str,
        content: str,
        sender_id: Optional[str] = None,
        is_internal: bool = False,
        message_type: str = "TEXT",
        metadata_json: Optional[dict] = None,
        event_bus: Optional[EventBus] = None,
    ) -> Message:
        conv = await session.scalar(select(Conversation).where(Conversation.id == conversation_id))
        if not conv:
            raise EntityNotFoundError("Conversation", conversation_id)

        now = datetime.now(timezone.utc)
        message = Message(
            conversation_id=conv.id,
            sender_type=sender_type,
            sender_id=sender_id,
            sender_name=sender_name,
            content=content,
            is_internal=is_internal,
            message_type=message_type,
            metadata_json=metadata_json,
        )
        session.add(message)

        # Update conversation meta
        conv.last_message_at = now
        if sender_type == "CUSTOMER":
            conv.unread_agent_count += 1
        elif sender_type == "AGENT" and not is_internal:
            conv.unread_customer_count += 1

        # Check if case needs first_responded_at timestamp
        case = await session.scalar(select(Case).where(Case.id == conv.case_id))
        if case and sender_type == "AGENT" and not is_internal and not case.first_responded_at:
            case.first_responded_at = now
            t_event = CaseTimelineEvent(
                case_id=case.id,
                actor_id=sender_id,
                actor_type="AGENT",
                event_type="FIRST_RESPONSE_SENT",
                summary=f"First response sent by {sender_name}",
            )
            session.add(t_event)

        await session.commit()
        await session.refresh(message)

        # Broadcast via WebSocket
        ws_payload = {
            "action": "NEW_MESSAGE",
            "conversation_id": conv.id,
            "message": {
                "id": message.id,
                "sender_type": message.sender_type,
                "sender_id": message.sender_id,
                "sender_name": message.sender_name,
                "content": message.content,
                "is_internal": message.is_internal,
                "message_type": message.message_type,
                "created_at": message.created_at.isoformat(),
            },
        }
        await ws_manager.broadcast_json(conv.id, ws_payload)

        # Publish Event
        bus = event_bus or get_event_bus()
        topic = EventTopic.INTERNAL_NOTE_ADDED if is_internal else (
            EventTopic.MESSAGE_RECEIVED if sender_type == "CUSTOMER" else EventTopic.MESSAGE_SENT
        )
        await bus.publish(
            Event(
                topic=topic,
                actor={"user_id": sender_id, "name": sender_name, "type": sender_type},
                payload={
                    "conversation_id": conv.id,
                    "case_id": conv.case_id,
                    "message_id": message.id,
                    "content": message.content,
                    "sender_type": sender_type,
                    "is_internal": is_internal,
                },
            )
        )

        return message

    @staticmethod
    async def mark_as_read(session: AsyncSession, conversation_id: str, user_id: str, is_agent: bool = False) -> None:
        conv = await session.scalar(select(Conversation).where(Conversation.id == conversation_id))
        if not conv:
            return

        if is_agent:
            conv.unread_agent_count = 0
        else:
            conv.unread_customer_count = 0

        await session.commit()
