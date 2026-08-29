"""
Unit & Integration tests for AI Classification, Frustration Scorer, and Vector RAG search.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.classifier import AIClassifier
from app.ai.embeddings import EmbeddingPipeline
from app.ai.rag import VectorRAGService
from app.schemas.customer import CustomerCreate
from app.schemas.case import CaseCreate
from app.schemas.knowledge import KnowledgeArticleCreate
from app.services.customer_service import CustomerService
from app.services.case_service import CaseService
from app.services.knowledge_service import KnowledgeService
from app.services.customer_intelligence_service import CustomerIntelligenceService


def test_ai_classifier_damaged_product():
    text = "My headphone box was smashed and the plastic ear cup is broken and cracked!"
    result = AIClassifier.classify_text(text)
    assert result.intent == "DAMAGED_PRODUCT"
    assert result.suggested_category == "PRODUCT"
    assert result.sentiment_label in ["NEGATIVE", "HIGHLY_FRUSTRATED"]
    assert result.recommended_playbook_code == "DAMAGED_PRODUCT_PLAYBOOK"


def test_ai_classifier_late_delivery():
    text = "Where is my package? The tracking says delayed and has not arrived for 5 days."
    result = AIClassifier.classify_text(text)
    assert result.intent == "LATE_DELIVERY"
    assert result.suggested_category == "DELIVERY"


def test_embeddings_and_cosine_similarity():
    text1 = "AeroSound wireless noise cancelling headphones return warranty policy."
    text2 = "Headphones warranty return policy and replacement procedures."
    text3 = "Fresh organic avocados recipe for salad."

    vec1 = EmbeddingPipeline.generate_embedding(text1)
    vec2 = EmbeddingPipeline.generate_embedding(text2)
    vec3 = EmbeddingPipeline.generate_embedding(text3)

    sim_related = EmbeddingPipeline.cosine_similarity(vec1, vec2)
    sim_unrelated = EmbeddingPipeline.cosine_similarity(vec1, vec3)

    assert sim_related > sim_unrelated
    assert sim_related > 0.3


@pytest.mark.asyncio
async def test_vector_rag_indexing_and_search(test_session: AsyncSession):
    article_data = KnowledgeArticleCreate(
        title="30-Day Return & Replacement Policy for Electronics",
        slug="electronics-return-policy",
        content="All consumer electronics including wireless headphones and cables are eligible for free replacement or refund within 30 days of confirmed delivery if defective or damaged.",
        visibility="PUBLIC",
        tags=["returns", "headphones", "warranty"],
    )
    article = await KnowledgeService.create_article(test_session, article_data, author_id="author-1")
    article = await KnowledgeService.publish_article(test_session, article.id, reviewer_id="reviewer-1")

    # Index into RAG
    await VectorRAGService.index_knowledge_article(test_session, article)

    # Query
    search_res = await VectorRAGService.search_similar(
        test_session, query="How do I return damaged headphones within 30 days?", top_k=2
    )
    assert len(search_res.results) >= 1
    assert search_res.results[0].source_id == article.id
    assert "replacement" in search_res.results[0].content.lower()


@pytest.mark.asyncio
async def test_customer_frustration_score(test_session: AsyncSession):
    customer = await CustomerService.create_customer(
        test_session,
        CustomerCreate(first_name="Natasha", last_name="Romanoff", email="natasha@shield.gov"),
    )

    # Case with negative sentiment
    case = await CaseService.create_case(
        test_session,
        CaseCreate(
            customer_id=customer.id,
            title="Angry complaint about worst delivery ever!",
            description="Terrible service, package is late and completely broken. Worst experience!",
            priority="HIGH",
        ),
    )
    case.sentiment_score = -0.8
    await test_session.commit()

    frust_resp = await CustomerIntelligenceService.compute_frustration_score(
        test_session, customer.id, case_id=case.id
    )
    assert frust_resp.frustration_score > 30.0
    assert frust_resp.risk_level in ["MEDIUM", "HIGH", "CRITICAL"]
