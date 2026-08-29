"""
Emotional Intensity, Sentiment Valence, and Escalation Trigger Lexicons.
"""

from typing import Any, Dict, List, Set


# Valence scored from -1.0 (Extreme negative) to +1.0 (Extreme positive)
SENTIMENT_VALENCE_LEXICON: Dict[str, float] = {
    # Extreme Negative & Frustration
    "furious": -0.95,
    "unacceptable": -0.90,
    "scam": -0.95,
    "fraud": -0.95,
    "lawyer": -0.90,
    "attorney": -0.90,
    "sue": -0.90,
    "disgusted": -0.85,
    "horrible": -0.80,
    "terrible": -0.80,
    "worst": -0.85,
    "awful": -0.80,
    "useless": -0.75,
    "garbage": -0.80,
    "trash": -0.80,
    "pathetic": -0.85,
    "ridiculous": -0.75,
    "incompetent": -0.85,
    "appalled": -0.80,
    "infuriating": -0.85,

    # Moderate Negative
    "disappointed": -0.50,
    "frustrated": -0.60,
    "annoyed": -0.45,
    "unhappy": -0.50,
    "broken": -0.55,
    "damaged": -0.55,
    "defective": -0.55,
    "delayed": -0.40,
    "late": -0.35,
    "confused": -0.30,
    "problem": -0.30,
    "issue": -0.25,
    "mistake": -0.35,
    "error": -0.30,
    "wrong": -0.40,

    # Moderate Positive
    "thanks": 0.35,
    "thank you": 0.40,
    "appreciate": 0.50,
    "helpful": 0.45,
    "good": 0.35,
    "nice": 0.30,
    "pleased": 0.45,
    "glad": 0.40,
    "satisfied": 0.50,

    # High Positive
    "excellent": 0.85,
    "amazing": 0.90,
    "fantastic": 0.85,
    "wonderful": 0.85,
    "outstanding": 0.90,
    "perfect": 0.95,
    "superb": 0.85,
    "delighted": 0.85,
    "love": 0.75,
    "brilliant": 0.80,
}

# Key phrases indicating legal, chargeback, or executive escalation threats
ESCALATION_TRIGGER_PHRASES: List[str] = [
    "better business bureau",
    "bbb complaint",
    "talk to your supervisor",
    "speak with a manager",
    "file a chargeback",
    "contacting my lawyer",
    "legal action",
    "consumer protection",
    "attorney general",
    "small claims court",
    "posting on twitter",
    "going viral",
    "reporting to police",
]


class SentimentAnalyzerEngine:
    @staticmethod
    def analyze_sentiment(text: str) -> Dict[str, Any]:
        lower = text.lower()
        total_score = 0.0
        matches_count = 0
        is_escalation_threat = False

        # Escalation trigger detection
        for phrase in ESCALATION_TRIGGER_PHRASES:
            if phrase in lower:
                is_escalation_threat = True
                total_score -= 0.8
                matches_count += 1

        # Word-level valence matching
        words = lower.split()
        for w in words:
            clean_w = w.strip(".,!?;:\"'")
            if clean_w in SENTIMENT_VALENCE_LEXICON:
                total_score += SENTIMENT_VALENCE_LEXICON[clean_w]
                matches_count += 1

        # Punctuation & capitalization modifiers
        exclamation_count = text.count("!")
        if exclamation_count > 1:
            total_score -= 0.1 * min(exclamation_count, 5)

        if len(text) > 10 and text.isupper():
            total_score -= 0.3

        final_score = 0.0 if matches_count == 0 else max(-1.0, min(1.0, total_score / max(1, matches_count)))

        if final_score <= -0.6 or is_escalation_threat:
            label = "HIGHLY_FRUSTRATED"
        elif final_score < -0.2:
            label = "NEGATIVE"
        elif final_score > 0.3:
            label = "POSITIVE"
        else:
            label = "NEUTRAL"

        return {
            "score": round(final_score, 2),
            "label": label,
            "is_escalation_threat": is_escalation_threat,
            "detected_keywords_count": matches_count,
        }
