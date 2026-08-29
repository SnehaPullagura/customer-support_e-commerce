"""
Intelligent Routing Engine evaluating category, language, skills, availability, and capacity.
"""

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.events import EventBus, Event, EventTopic, get_event_bus
from app.models.case import Case
from app.models.agent import Agent, AgentSkill, Skill, Team
from app.models.routing import RoutingRule, RoutingExecutionLog
from app.models.customer import Customer
from app.schemas.routing import RoutingRuleCreate, RoutingDecisionResponse


class RoutingService:
    @staticmethod
    async def create_rule(session: AsyncSession, data: RoutingRuleCreate) -> RoutingRule:
        rule = RoutingRule(
            name=data.name,
            description=data.description,
            priority_order=data.priority_order,
            match_conditions_json=data.match_conditions_json,
            target_team_id=data.target_team_id,
            required_skill_code=data.required_skill_code,
            routing_strategy=data.routing_strategy,
            is_active=data.is_active,
        )
        session.add(rule)
        await session.commit()
        await session.refresh(rule)
        return rule

    @staticmethod
    async def route_case(
        session: AsyncSession,
        case_id: str,
        event_bus: Optional[EventBus] = None,
    ) -> RoutingDecisionResponse:
        case = await session.scalar(
            select(Case).options(selectinload(Case.customer)).where(Case.id == case_id)
        )
        if not case:
            return RoutingDecisionResponse(
                case_id=case_id,
                routing_strategy="FAILED",
                decision_reason="Case not found",
            )

        # 1. Fetch active routing rules ordered by priority_order ASC
        rules = await session.scalars(
            select(RoutingRule).where(RoutingRule.is_active == True).order_by(RoutingRule.priority_order)
        )
        all_rules = list(rules.all())

        matched_rule: Optional[RoutingRule] = None
        for rule in all_rules:
            conds = rule.match_conditions_json or {}
            match = True
            if "category" in conds and conds["category"] != case.category:
                match = False
            if "priority" in conds and conds["priority"] != case.priority:
                match = False
            if "customer_segment" in conds and case.customer and conds["customer_segment"] != case.customer.segment:
                match = False
            if match:
                matched_rule = rule
                break

        # 2. Determine target skill or team
        target_team_id = matched_rule.target_team_id if matched_rule else None
        required_skill = matched_rule.required_skill_code if matched_rule else None
        routing_strategy = matched_rule.routing_strategy if matched_rule else "LEAST_BUSY"

        # 3. Find candidate agents
        query = select(Agent).options(
            selectinload(Agent.skills).selectinload(AgentSkill.skill)
        ).where(Agent.status.in_(["AVAILABLE", "BUSY"]))

        if target_team_id:
            query = query.where(Agent.team_id == target_team_id)

        candidates = list((await session.scalars(query)).all())

        # Filter by language match if customer has language preference
        cust_lang = case.customer.preferred_language if case.customer else "en"
        lang_candidates = [
            a for a in candidates if (not a.languages or cust_lang in a.languages or "en" in a.languages)
        ]
        if lang_candidates:
            candidates = lang_candidates

        # Filter by required skill if present
        if required_skill:
            skill_matched = [
                a for a in candidates
                if any(s.skill.code == required_skill.upper() for s in a.skills if s.skill)
            ]
            if skill_matched:
                candidates = skill_matched

        # Filter agents with available capacity (current_active < max_active)
        available_capacity = [a for a in candidates if a.current_active_cases < a.max_active_cases]
        if available_capacity:
            candidates = available_capacity

        selected_agent: Optional[Agent] = None
        decision_reason: str = ""

        if candidates:
            # Sort by least busy (lowest current_active_cases) and highest CSAT
            candidates.sort(key=lambda a: (a.current_active_cases, -a.csat_score))
            selected_agent = candidates[0]
            decision_reason = (
                f"Assigned to {selected_agent.display_name} via {routing_strategy} strategy. "
                f"Workload: {selected_agent.current_active_cases}/{selected_agent.max_active_cases}"
            )
        else:
            decision_reason = "No online agents with capacity available. Placed into unassigned queue."

        # Update case
        if selected_agent:
            case.assigned_agent_id = selected_agent.id
            case.assigned_team_id = selected_agent.team_id
            selected_agent.current_active_cases += 1
            if case.status == "NEW":
                case.status = "OPEN"
        elif target_team_id:
            case.assigned_team_id = target_team_id

        # Log routing execution
        log = RoutingExecutionLog(
            case_id=case.id,
            matched_rule_id=matched_rule.id if matched_rule else None,
            assigned_agent_id=selected_agent.id if selected_agent else None,
            assigned_team_id=case.assigned_team_id,
            routing_strategy=routing_strategy,
            decision_reason=decision_reason,
            evaluated_candidates_count=len(candidates),
        )
        session.add(log)
        await session.commit()

        # Emit Routing Completed Event
        bus = event_bus or get_event_bus()
        await bus.publish(
            Event(
                topic=EventTopic.ROUTING_COMPLETED,
                payload={
                    "case_id": case.id,
                    "assigned_agent_id": selected_agent.id if selected_agent else None,
                    "reason": decision_reason,
                },
            )
        )

        return RoutingDecisionResponse(
            case_id=case.id,
            assigned_agent_id=selected_agent.id if selected_agent else None,
            assigned_team_id=case.assigned_team_id,
            routing_strategy=routing_strategy,
            decision_reason=decision_reason,
            matched_rule_id=matched_rule.id if matched_rule else None,
        )
