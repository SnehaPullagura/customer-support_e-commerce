"""
Conversation & Omnichannel Messaging endpoints.
"""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser, require_roles
from app.core.security import Role
from app.schemas.common import StandardResponse
from app.schemas.conversation import (
    ConversationResponse,
    ConversationDetailResponse,
    MessageCreate,
    InternalNoteCreate,
    MessageResponse,
)
from app.services.conversation_service import ConversationService
from app.services.ai_service import AIService

router = APIRouter()


@router.get("/case/{case_id}", response_model=StandardResponse[ConversationDetailResponse])
async def get_or_create_case_conversation(
    case_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    channel: str = "WEB_CHAT",
):
    conv = await ConversationService.get_or_create_conversation(db, case_id=case_id, channel=channel)
    detail = await ConversationService.get_conversation(db, conv.id)

    # Filter out internal notes if caller is a customer
    if current_user.is_customer():
        detail.messages = [m for m in detail.messages if not m.is_internal]

    return StandardResponse(data=ConversationDetailResponse.model_validate(detail))


@router.get("/{conversation_id}", response_model=StandardResponse[ConversationDetailResponse])
async def get_conversation(
    conversation_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    detail = await ConversationService.get_conversation(db, conversation_id)
    if current_user.is_customer():
        detail.messages = [m for m in detail.messages if not m.is_internal]
    return StandardResponse(data=ConversationDetailResponse.model_validate(detail))


@router.post("/{conversation_id}/messages", response_model=StandardResponse[MessageResponse], status_code=status.HTTP_201_CREATED)
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    sender_type = "CUSTOMER" if current_user.is_customer() else "AGENT"
    sender_name = current_user.email.split("@")[0].capitalize()

    msg = await ConversationService.send_message(
        db,
        conversation_id=conversation_id,
        sender_type=sender_type,
        sender_name=sender_name,
        content=data.content,
        sender_id=current_user.user_id,
        is_internal=data.is_internal if current_user.is_staff() else False,
        message_type=data.message_type,
        metadata_json=data.metadata_json,
    )
    return StandardResponse(
        message="Message sent successfully",
        data=MessageResponse.model_validate(msg),
    )


@router.post("/{conversation_id}/notes", response_model=StandardResponse[MessageResponse], status_code=status.HTTP_201_CREATED)
async def add_internal_note(
    conversation_id: str,
    data: InternalNoteCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    sender_name = current_user.email.split("@")[0].capitalize()
    msg = await ConversationService.send_message(
        db,
        conversation_id=conversation_id,
        sender_type="AGENT",
        sender_name=sender_name,
        content=data.content,
        sender_id=current_user.user_id,
        is_internal=True,
        message_type="INTERNAL_NOTE",
    )
    return StandardResponse(
        message="Internal note added",
        data=MessageResponse.model_validate(msg),
    )


@router.post("/{conversation_id}/read", response_model=StandardResponse[bool])
async def mark_as_read(
    conversation_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    await ConversationService.mark_as_read(
        db, conversation_id, user_id=current_user.user_id, is_agent=current_user.is_staff()
    )
    return StandardResponse(message="Conversation marked as read", data=True)
