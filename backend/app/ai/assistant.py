"""
AI Support Copilot, Suggested Replies, Summarizer, and Copilot Recommendations.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.ai.classifier import AIClassifier
from app.ai.rag import VectorRAGService
from app.models.case import Case
from app.models.conversation import Conversation, Message
from app.schemas.ai import AISuggestedReplyResponse


class AIAssistant:
    @staticmethod
    async def generate_suggested_reply(
        session: AsyncSession, conversation_id: str
    ) -> AISuggestedReplyResponse:
        conv = await session.scalar(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id)
        )
        if not conv or not conv.messages:
            return AISuggestedReplyResponse(
                reply_text="Hello! How can I assist you with your order today?",
                confidence=0.70,
            )

        # Get latest customer message
        customer_msgs = [m for m in conv.messages if m.sender_type == "CUSTOMER"]
        last_msg = customer_msgs[-1].content if customer_msgs else conv.messages[-1].content

        # 1. Run classifier
        classification = AIClassifier.classify_text(last_msg)

        # 2. Retrieve grounded knowledge
        rag_context = await VectorRAGService.synthesize_grounded_context(session, last_msg)

        # 3. Formulate empathetic response
        if classification.intent == "DAMAGED_PRODUCT":
            reply = (
                "I am very sorry to hear that your order arrived damaged! "
                "I would be glad to help you immediately. We can either dispatch a brand-new replacement right away "
                "or issue a full refund to your original payment method. Could you please share a quick photo of the damage so I can process this for you?"
            )
        elif classification.intent == "LATE_DELIVERY":
            reply = (
                "Thank you for reaching out regarding your shipment. "
                "I have checked our logistics tracking system. I apologize for the delay you are experiencing. "
                "Let me trace this package with our carrier and ensure it reaches you as soon as possible."
            )
        elif classification.intent == "PAYMENT_ISSUE":
            reply = (
                "I understand your concern regarding the billing charge on your account. "
                "I am reviewing your payment ledger now to ensure everything is resolved accurately."
            )
        else:
            reply = (
                f"Thank you for contacting support regarding your inquiry. "
                f"I am reviewing your order details now to assist you with the best resolution."
            )

        return AISuggestedReplyResponse(
            reply_text=reply,
            confidence=classification.confidence_score,
            suggested_playbook_code=classification.recommended_playbook_code,
            source_articles=["Knowledge Base Policy Guidelines"],
        )

    @staticmethod
    async def summarize_case(session: AsyncSession, case_id: str) -> str:
        case = await session.scalar(
            select(Case)
            .options(selectinload(Case.conversations).selectinload(Conversation.messages))
            .where(Case.id == case_id)
        )
        if not case:
            return "Case not found."

        all_msgs = []
        for conv in case.conversations:
            for m in conv.messages:
                prefix = "[Internal]" if m.is_internal else f"[{m.sender_type}]"
                all_msgs.append(f"{prefix} {m.sender_name}: {m.content}")

        if not all_msgs:
            return f"Case #{case.case_number} filed for {case.category}. Description: {case.description}"

        convo_text = "\n".join(all_msgs[-8:])  # Last 8 messages
        return f"Executive Summary for Case #{case.case_number} ({case.category} - {case.priority}):\n- Customer reported: '{case.description[:100]}'\n- Status: {case.status}\n- Latest interaction:\n{convo_text[:400]}"
