"""
Customer Self-Service, Guided Interactive Troubleshooting, and Deflection Service.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import EntityNotFoundError
from app.models.self_service import TroubleshootingFlow, SelfServiceSession
from app.schemas.self_service import (
    TroubleshootingFlowCreate,
    SelfServiceStepRequest,
    SelfServiceResponse,
)


DEFAULT_TROUBLESHOOTING_FLOWS = [
    {
        "code": "WHERE_IS_MY_ORDER",
        "title": "Where is my package / Track Delivery",
        "category": "DELIVERY",
        "description": "Guided self-service lookup for shipment milestones and carrier status.",
        "decision_tree_json": {
            "root": {
                "question": "What issue are you experiencing with your delivery?",
                "options": [
                    {"key": "LATE", "label": "Package is late past estimated delivery date", "next": "CHECK_CARRIER"},
                    {"key": "MARKED_DELIVERED", "label": "Tracking says Delivered but I cannot find it", "next": "LOOK_AROUND"},
                    {"key": "TRACKING_NOT_UPDATING", "label": "Tracking number has no movement", "next": "CARRIER_TRANSIT_DELAY"},
                ],
            },
            "LOOK_AROUND": {
                "question": "Carriers occasionally leave packages near back gates or with building management. Have you checked porch or neighbors?",
                "options": [
                    {"key": "FOUND", "label": "Yes, I found it!", "is_resolved": True, "is_deflected": True},
                    {"key": "STILL_MISSING", "label": "Still missing after checking", "can_escalate_to_case": True},
                ],
            },
            "CHECK_CARRIER": {
                "question": "If your package is less than 48 hours overdue, carriers often deliver next day. Would you like to file a lost trace claim?",
                "options": [
                    {"key": "WAIT_A_DAY", "label": "I will wait 24 hours", "is_resolved": True, "is_deflected": True},
                    {"key": "FILE_CLAIM", "label": "File support case immediately", "can_escalate_to_case": True},
                ],
            },
        },
    }
]


class SelfServiceService:
    @staticmethod
    async def seed_default_flows(session: AsyncSession) -> None:
        for flow_data in DEFAULT_TROUBLESHOOTING_FLOWS:
            existing = await session.scalar(
                select(TroubleshootingFlow).where(TroubleshootingFlow.code == flow_data["code"])
            )
            if not existing:
                fl = TroubleshootingFlow(
                    code=flow_data["code"],
                    title=flow_data["title"],
                    category=flow_data["category"],
                    description=flow_data["description"],
                    decision_tree_json=flow_data["decision_tree_json"],
                    is_active=True,
                )
                session.add(fl)
        await session.commit()

    @staticmethod
    async def list_flows(session: AsyncSession) -> List[TroubleshootingFlow]:
        res = await session.scalars(select(TroubleshootingFlow).where(TroubleshootingFlow.is_active == True))
        return list(res.all())

    @staticmethod
    async def execute_step(
        session: AsyncSession, request: SelfServiceStepRequest, customer_id: Optional[str] = None
    ) -> SelfServiceResponse:
        flow = await session.scalar(
            select(TroubleshootingFlow).where(TroubleshootingFlow.code == request.flow_code)
        )
        if not flow:
            raise EntityNotFoundError("TroubleshootingFlow", request.flow_code)

        tree = flow.decision_tree_json or {}
        
        # Determine current node
        current_node_key = "root"
        if request.chosen_option_key:
            # Look up parent options
            for node_name, node_data in tree.items():
                for opt in node_data.get("options", []):
                    if opt.get("key") == request.chosen_option_key:
                        current_node_key = opt.get("next", node_name)
                        break

        current_node = tree.get(current_node_key, tree.get("root", {}))
        is_resolved = current_node.get("is_resolved", False)
        is_deflected = current_node.get("is_deflected", False)
        can_escalate = current_node.get("can_escalate_to_case", False)

        session_id = request.session_id or f"SS-{flow.code}"
        return SelfServiceResponse(
            session_id=session_id,
            flow_code=flow.code,
            current_node=current_node,
            is_resolved=is_resolved,
            is_deflected=is_deflected,
            can_escalate_to_case=can_escalate,
            suggested_articles=[{"title": "Delivery Exception Policy", "slug": "delivery-policy"}],
        )
