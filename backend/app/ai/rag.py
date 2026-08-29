"""
Vector RAG Knowledge Retriever and Context Synthesizer.
"""

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.ai.embeddings import EmbeddingPipeline
from app.models.ai import VectorDocumentChunk
from app.models.knowledge import KnowledgeArticle
from app.schemas.ai import VectorSearchResponse, VectorSearchResultItem


class VectorRAGService:
    @staticmethod
    async def index_knowledge_article(session: AsyncSession, article: KnowledgeArticle) -> None:
        """Chunk and index an approved knowledge article into vector storage."""
        # Delete existing chunks for this article
        existing = await session.scalars(
            select(VectorDocumentChunk).where(
                VectorDocumentChunk.source_type == "KNOWLEDGE_ARTICLE",
                VectorDocumentChunk.source_id == article.id,
            )
        )
        for chunk in existing.all():
            await session.delete(chunk)

        text_to_index = f"Title: {article.title}\n\nContent: {article.content}"
        chunks = EmbeddingPipeline.chunk_text(text_to_index, chunk_size=300, overlap=40)

        for idx, chunk_text in enumerate(chunks):
            embedding = EmbeddingPipeline.generate_embedding(chunk_text)
            doc_chunk = VectorDocumentChunk(
                source_type="KNOWLEDGE_ARTICLE",
                source_id=article.id,
                chunk_index=idx,
                content=chunk_text,
                embedding_json=embedding,
                metadata_json={"title": article.title, "slug": article.slug, "tags": article.tags},
            )
            session.add(doc_chunk)
        await session.commit()

    @staticmethod
    async def search_similar(
        session: AsyncSession,
        query: str,
        top_k: int = 4,
        source_type: Optional[str] = None,
    ) -> VectorSearchResponse:
        """Search vectorized knowledge repository for top-k semantically relevant chunks."""
        query_embedding = EmbeddingPipeline.generate_embedding(query)

        stmt = select(VectorDocumentChunk)
        if source_type:
            stmt = stmt.where(VectorDocumentChunk.source_type == source_type)

        chunks = list((await session.scalars(stmt)).all())

        scored: List[Tuple[VectorDocumentChunk, float]] = []
        for c in chunks:
            sim = EmbeddingPipeline.cosine_similarity(query_embedding, c.embedding_json)
            scored.append((c, sim))

        # Sort descending by similarity
        scored.sort(key=lambda x: x[1], reverse=True)
        top_results = scored[:top_k]

        items = [
            VectorSearchResultItem(
                source_type=c.source_type,
                source_id=c.source_id,
                content=c.content,
                score=round(score, 4),
                metadata_json=c.metadata_json,
            )
            for c, score in top_results
        ]
        return VectorSearchResponse(query=query, results=items)

    @staticmethod
    async def synthesize_grounded_context(session: AsyncSession, query: str) -> str:
        """Retrieve and synthesize approved policy context for LLM prompt injection."""
        results = await VectorRAGService.search_similar(session, query, top_k=3)
        if not results.results:
            return "No specific internal policy documents found for this query."

        context_blocks = []
        for idx, r in enumerate(results.results, 1):
            title = (r.metadata_json or {}).get("title", r.source_type)
            context_blocks.append(f"[Document {idx} - {title}]\n{r.content}")

        return "\n\n---\n\n".join(context_blocks)
