"""
AI Service Facade orchestrating inference logging, classification, and copilot capabilities.
"""

import time
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.assistant import AIAssistant
from app.ai.classifier import AIClassifier
from app.ai.rag import VectorRAGService
from app.core.telemetry import MetricsService
from app.models.ai import AIInferenceLog
from app.schemas.ai import (
    AIClassificationRequest,
    AIClassificationResponse,
    AISuggestedReplyResponse,
    VectorQueryRequest,
    VectorSearchResponse,
)


class AIService:
    @staticmethod
    async def classify_ticket_or_case(
        session: AsyncSession, request: AIClassificationRequest, actor_id: Optional[str] = None
    ) -> AIClassificationResponse:
        start_time = time.time()
        result = AIClassifier.classify_text(request.text, customer_tier=request.customer_tier or "STANDARD")
        latency_ms = int((time.time() - start_time) * 1000)

        # Log AI inference
        log = AIInferenceLog(
            task_type="INTENT_CLASSIFICATION",
            input_text=request.text[:1000],
            output_result_json=result.model_dump(mode="json"),
            confidence_score=result.confidence_score,
            latency_ms=latency_ms,
            actor_id=actor_id,
        )
        session.add(log)
        await session.commit()

        MetricsService.record_ai_inference("classification", success=True)
        return result

    @staticmethod
    async def get_suggested_reply(
        session: AsyncSession, conversation_id: str
    ) -> AISuggestedReplyResponse:
        start_time = time.time()
        reply_response = await AIAssistant.generate_suggested_reply(session, conversation_id)
        latency_ms = int((time.time() - start_time) * 1000)

        log = AIInferenceLog(
            task_type="SUGGESTED_REPLY",
            input_text=f"Conversation: {conversation_id}",
            output_result_json=reply_response.model_dump(mode="json"),
            confidence_score=reply_response.confidence,
            latency_ms=latency_ms,
        )
        session.add(log)
        await session.commit()

        MetricsService.record_ai_inference("suggested_reply", success=True)
        return reply_response

    @staticmethod
    async def query_knowledge_rag(
        session: AsyncSession, request: VectorQueryRequest
    ) -> VectorSearchResponse:
        start_time = time.time()
        res = await VectorRAGService.search_similar(
            session, request.query, top_k=request.top_k, source_type=request.source_type
        )
        latency_ms = int((time.time() - start_time) * 1000)

        log = AIInferenceLog(
            task_type="RAG_RETRIEVAL",
            input_text=request.query,
            output_result_json={"results_count": len(res.results)},
            latency_ms=latency_ms,
        )
        session.add(log)
        await session.commit()

        MetricsService.record_ai_inference("rag_retrieval", success=True)
        return res
