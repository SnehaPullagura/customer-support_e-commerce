"""
AI Lexicons, NLP Multi-Language Matchers, and Entity Extractors.
"""

from app.ai.lexicons.patterns import INTENT_PATTERNS_MAP
from app.ai.lexicons.multilingual import MultilingualIntentMatcher, MULTILINGUAL_INTENT_SYNONYMS
from app.ai.lexicons.entities import EntityExtractor, ExtractedEntities
from app.ai.lexicons.sentiment_lexicon import (
    SentimentAnalyzerEngine,
    SENTIMENT_VALENCE_LEXICON,
    ESCALATION_TRIGGER_PHRASES,
)

__all__ = [
    "INTENT_PATTERNS_MAP",
    "MultilingualIntentMatcher",
    "MULTILINGUAL_INTENT_SYNONYMS",
    "EntityExtractor",
    "ExtractedEntities",
    "SentimentAnalyzerEngine",
    "SENTIMENT_VALENCE_LEXICON",
    "ESCALATION_TRIGGER_PHRASES",
]
