"""
AI NLP, Copilot, Suggested Replies, and Vector RAG endpoints.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser, require_roles
from app.core.security import Role
from app.schemas.ai import (
    AIClassificationRequest,
    AIClassificationResponse,
    AISuggestedReplyResponse,
    VectorQueryRequest,
    VectorSearchResponse,
)
from app.schemas.common import StandardResponse
from app.services.ai_service import AIService

router = APIRouter()


@router.post("/classify", response_model=StandardResponse[AIClassificationResponse])
async def classify_text(
    data: AIClassificationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
):
    classification = await AIService.classify_ticket_or_case(db, data, actor_id=current_user.user_id)
    return StandardResponse(message="AI classification completed", data=classification)


@router.get("/suggest-reply/{conversation_id}", response_model=StandardResponse[AISuggestedReplyResponse])
async def get_suggested_reply(
    conversation_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    reply = await AIService.get_suggested_reply(db, conversation_id)
    return StandardResponse(message="AI suggested response generated", data=reply)


@router.post("/rag-search", response_model=StandardResponse[VectorSearchResponse])
async def search_vector_knowledge(
    data: VectorQueryRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    results = await AIService.query_knowledge_rag(db, data)
    return StandardResponse(message="Semantic RAG search executed", data=results)
