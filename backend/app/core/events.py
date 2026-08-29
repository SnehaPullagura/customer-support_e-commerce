"""
Event-driven messaging infrastructure, topics, and asynchronous event dispatcher.
"""

import asyncio
import inspect
import json
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field

logger = logging.getLogger("app.core.events")


class EventTopic(str, Enum):
    # Customer Events
    CUSTOMER_CREATED = "customer.created"
    CUSTOMER_UPDATED = "customer.updated"
    CUSTOMER_TAG_ADDED = "customer.tag_added"
    CUSTOMER_FRUSTRATION_SPIKE = "customer.frustration_spike"

    # Case Events
    CASE_CREATED = "case.created"
    CASE_UPDATED = "case.updated"
    CASE_ASSIGNED = "case.assigned"
    CASE_PRIORITY_CHANGED = "case.priority_changed"
    CASE_STATUS_CHANGED = "case.status_changed"
    CASE_ESCALATED = "case.escalated"
    CASE_RESOLVED = "case.resolved"
    CASE_CLOSED = "case.closed"
    CASE_REOPENED = "case.reopened"
    CASE_MERGED = "case.merged"
    CASE_SPLIT = "case.split"

    # Ticket Events
    TICKET_CREATED = "ticket.created"
    TICKET_UPDATED = "ticket.updated"
    TICKET_CLOSED = "ticket.closed"

    # Conversation & Message Events
    CONVERSATION_CREATED = "conversation.created"
    MESSAGE_RECEIVED = "conversation.message_received"
    MESSAGE_SENT = "conversation.message_sent"
    MESSAGE_READ = "conversation.message_read"
    INTERNAL_NOTE_ADDED = "conversation.internal_note_added"

    # SLA Events
    SLA_STARTED = "sla.started"
    SLA_PAUSED = "sla.paused"
    SLA_RESUMED = "sla.resumed"
    SLA_WARNING = "sla.warning"
    SLA_BREACHED = "sla.breached"

    # Routing Events
    ROUTING_REQUESTED = "routing.requested"
    ROUTING_COMPLETED = "routing.completed"
    ROUTING_FAILED = "routing.failed"

    # Resolution & Playbook Events
    PLAYBOOK_STARTED = "playbook.started"
    PLAYBOOK_STEP_EXECUTED = "playbook.step_executed"
    PLAYBOOK_COMPLETED = "playbook.completed"
    RESOLUTION_PROPOSED = "resolution.proposed"
    RESOLUTION_APPROVED = "resolution.approved"
    RESOLUTION_EXECUTED = "resolution.executed"

    # Return & Refund Events
    RETURN_REQUESTED = "return.requested"
    RETURN_APPROVED = "return.approved"
    RETURN_RECEIVED = "return.received"
    REFUND_REQUESTED = "refund.requested"
    REFUND_APPROVED = "refund.approved"
    REFUND_COMPLETED = "refund.completed"
    REFUND_FAILED = "refund.failed"

    # Notification Events
    NOTIFICATION_REQUESTED = "notification.requested"
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_FAILED = "notification.failed"

    # Commerce External Ingestion Events
    ORDER_DELAYED = "commerce.order_delayed"
    ORDER_DELIVERED = "commerce.order_delivered"
    ORDER_CANCELLED = "commerce.order_cancelled"
    PAYMENT_FAILED = "commerce.payment_failed"
    SHIPMENT_DELAYED = "commerce.shipment_delayed"


class Event(BaseModel):
    """Envelope for all asynchronous domain events."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor: Optional[Dict[str, Any]] = None  # e.g., {"user_id": "...", "role": "..."}
    correlation_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    payload: Dict[str, Any] = Field(default_factory=dict)
    version: str = "1.0"

    def to_json(self) -> str:
        return json.dumps(
            {
                "event_id": self.event_id,
                "topic": self.topic,
                "timestamp": self.timestamp.isoformat(),
                "actor": self.actor,
                "correlation_id": self.correlation_id,
                "payload": self.payload,
                "version": self.version,
            }
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    """
    Publish/Subscribe Event Bus handling local asynchronous dispatch
    with extensible bindings to Redis Streams or Kafka.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._wildcard_handlers: List[EventHandler] = []
        self._history: List[Event] = []
        self._max_history: int = 1000

    def subscribe(self, topic: Union[str, EventTopic], handler: EventHandler) -> None:
        """Register a handler for a specific event topic."""
        topic_key = topic.value if isinstance(topic, EventTopic) else str(topic)
        if topic_key == "*":
            if handler not in self._wildcard_handlers:
                self._wildcard_handlers.append(handler)
        else:
            if topic_key not in self._handlers:
                self._handlers[topic_key] = []
            if handler not in self._handlers[topic_key]:
                self._handlers[topic_key].append(handler)
        logger.debug("Subscribed %s to topic %s", handler.__name__, topic_key)

    def unsubscribe(self, topic: Union[str, EventTopic], handler: EventHandler) -> None:
        """Unregister a handler."""
        topic_key = topic.value if isinstance(topic, EventTopic) else str(topic)
        if topic_key == "*" and handler in self._wildcard_handlers:
            self._wildcard_handlers.remove(handler)
        elif topic_key in self._handlers and handler in self._handlers[topic_key]:
            self._handlers[topic_key].remove(handler)

    async def publish(self, event: Event) -> None:
        """
        Publish an event to all registered topic and wildcard subscribers
        asynchronously without blocking the caller.
        """
        self._record_history(event)
        topic = event.topic

        handlers = list(self._handlers.get(topic, [])) + self._wildcard_handlers
        if not handlers:
            logger.debug("No active subscribers for event topic: %s", topic)
            return

        logger.info(
            "Publishing event [%s] topic=%s correlation_id=%s to %d handlers",
            event.event_id,
            topic,
            event.correlation_id,
            len(handlers),
        )

        # Dispatch handlers concurrently in the background
        tasks = []
        for handler in handlers:
            tasks.append(self._safe_execute_handler(handler, event))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_execute_handler(self, handler: EventHandler, event: Event) -> None:
        try:
            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(
                "Error executing event handler %s for event %s (topic %s): %s",
                handler.__name__,
                event.event_id,
                event.topic,
                str(e),
                exc_info=True,
            )

    def _record_history(self, event: Event) -> None:
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)

    def get_history(self, topic: Optional[str] = None, limit: int = 50) -> List[Event]:
        """Retrieve recent published events."""
        events = self._history
        if topic:
            events = [e for e in events if e.topic == topic]
        return list(reversed(events[-limit:]))


# Global singleton instance
_global_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Dependency injection helper for obtaining the global event bus."""
    return _global_event_bus
