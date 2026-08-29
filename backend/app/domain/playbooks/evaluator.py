"""
Playbook Evaluation Engine, Dynamic Recommendation, and Step Transitions.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from app.domain.playbooks.catalog import PlaybookCatalogService, PlaybookDef, PlaybookStepDef


class PlaybookRecommendation(BaseModel):
    playbook_code: str
    playbook_name: str
    category: str
    confidence_score: float
    reason: str
    estimated_duration_mins: int
    first_step_title: str


class PlaybookEvaluator:
    @staticmethod
    def recommend_playbook(
        intent: str, category: str, priority: str, customer_tier: str = "STANDARD"
    ) -> Optional[PlaybookRecommendation]:
        pb = PlaybookCatalogService.find_playbook_by_intent(intent)
        if not pb:
            # Fallback by category
            if category == "PRODUCT":
                pb = PlaybookCatalogService.get_playbook_definition("DAMAGED_PRODUCT_PLAYBOOK")
            elif category == "DELIVERY":
                pb = PlaybookCatalogService.get_playbook_definition("LOST_IN_TRANSIT_PLAYBOOK")
            elif category == "PAYMENT":
                pb = PlaybookCatalogService.get_playbook_definition("DOUBLE_CHARGE_DISPUTE_PLAYBOOK")
            else:
                pb = PlaybookCatalogService.get_playbook_definition("DAMAGED_PRODUCT_PLAYBOOK")

        if not pb:
            return None

        first_step = pb.steps[0].title if pb.steps else "Review Case"
        return PlaybookRecommendation(
            playbook_code=pb.code,
            playbook_name=pb.name,
            category=pb.category,
            confidence_score=0.92,
            reason=f"Recommended based on customer issue intent '{intent}' and category '{category}'.",
            estimated_duration_mins=pb.estimated_duration_mins,
            first_step_title=first_step,
        )

    @staticmethod
    def validate_step_execution(
        playbook_code: str, step_order: int, input_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        pb = PlaybookCatalogService.get_playbook_definition(playbook_code)
        if not pb or step_order > len(pb.steps):
            return False
        return True
