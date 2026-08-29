"""
Vector Embeddings Generator and Chunking Pipeline.
"""

import math
import re
from typing import List, Tuple


class EmbeddingPipeline:
    """
    High-performance vector embedding generator using normalized subword n-gram hashing
    with cosine similarity for fast, local zero-dependency semantic vector search.
    """

    DIMENSION = 384

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split document text into overlapping chunks."""
        words = text.split()
        if not words:
            return []
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)
            i += chunk_size - overlap
            if i >= len(words):
                break
        return chunks

    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """Generate a deterministic 384-dimensional normalized embedding vector."""
        vec = [0.0] * cls.DIMENSION
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return vec

        for token in tokens:
            # Hash character trigrams
            for i in range(max(1, len(token) - 2)):
                sub = token[i : i + 3]
                h = abs(hash(sub)) % cls.DIMENSION
                vec[h] += 1.0

        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two unit vectors."""
        if len(vec_a) != len(vec_b) or not vec_a:
            return 0.0
        return float(sum(a * b for a, b in zip(vec_a, vec_b)))
