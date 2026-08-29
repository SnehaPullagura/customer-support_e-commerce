"""
AI Inference Logs, Suggested Responses, and Vector RAG Embeddings storage models.
"""

from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseEntity


class AIInferenceLog(BaseEntity):
    __tablename__ = "ai_inference_logs"

    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # INTENT_CLASSIFICATION, SENTIMENT_ANALYSIS, SUMMARIZATION, RAG_RETRIEVAL, SUGGESTED_REPLY, RESOLUTION_RECOMMENDATION
    
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    output_result_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    case_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    actor_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)


class AISuggestedReply(BaseEntity):
    __tablename__ = "ai_suggested_replies"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    suggestion_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    suggested_playbook_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="PROPOSED", nullable=False)
    # PROPOSED, ACCEPTED, EDITED_AND_SENT, REJECTED


class VectorDocumentChunk(BaseEntity):
    __tablename__ = "vector_document_chunks"

    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # KNOWLEDGE_ARTICLE, PLAYBOOK, POLICY, HISTORICAL_CASE
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_json: Mapped[List[float]] = mapped_column(JSON, nullable=False)  # Vector embedding array
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
