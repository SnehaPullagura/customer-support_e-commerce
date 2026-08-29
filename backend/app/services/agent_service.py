"""
Agent Workforce Management and Capacity Service.
"""

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, EntityNotFoundError
from app.core.telemetry import MetricsService
from app.models.agent import Agent, AgentSkill, AgentStatusLog, Skill, Team
from app.models.case import Case
from app.schemas.agent import AgentCreate, AgentUpdate, SkillCreate, TeamCreate


class AgentService:
    @staticmethod
    async def create_skill(session: AsyncSession, data: SkillCreate) -> Skill:
        existing = await session.scalar(select(Skill).where(Skill.code == data.code.upper()))
        if existing:
            raise ConflictError(f"Skill code '{data.code}' already exists.")

        skill = Skill(
            code=data.code.upper(),
            name=data.name,
            category=data.category,
            description=data.description,
        )
        session.add(skill)
        await session.commit()
        await session.refresh(skill)
        return skill

    @staticmethod
    async def list_skills(session: AsyncSession) -> List[Skill]:
        res = await session.scalars(select(Skill).order_by(Skill.name))
        return list(res.all())

    @staticmethod
    async def create_team(session: AsyncSession, data: TeamCreate) -> Team:
        existing = await session.scalar(select(Team).where(Team.name == data.name))
        if existing:
            raise ConflictError(f"Team '{data.name}' already exists.")

        team = Team(
            name=data.name,
            department=data.department,
            description=data.description,
            lead_agent_id=data.lead_agent_id,
        )
        session.add(team)
        await session.commit()
        await session.refresh(team)
        return team

    @staticmethod
    async def list_teams(session: AsyncSession) -> List[Team]:
        res = await session.scalars(select(Team).order_by(Team.name))
        return list(res.all())

    @staticmethod
    async def create_agent(session: AsyncSession, data: AgentCreate) -> Agent:
        existing = await session.scalar(select(Agent).where(Agent.user_id == data.user_id))
        if existing:
            raise ConflictError("Agent record already exists for this user.")

        agent = Agent(
            user_id=data.user_id,
            team_id=data.team_id,
            employee_code=data.employee_code,
            display_name=data.display_name,
            tier=data.tier,
            max_active_cases=data.max_active_cases,
            languages=data.languages,
            status="OFFLINE",
        )
        session.add(agent)
        await session.flush()

        for skill_id in data.skill_ids:
            sk = AgentSkill(agent_id=agent.id, skill_id=skill_id, proficiency_level=3)
            session.add(sk)

        await session.commit()
        await session.refresh(agent)
        return agent

    @staticmethod
    async def get_agent(session: AsyncSession, agent_id: str) -> Agent:
        agent = await session.scalar(
            select(Agent)
            .options(
                selectinload(Agent.team),
                selectinload(Agent.skills).selectinload(AgentSkill.skill),
            )
            .where(Agent.id == agent_id)
        )
        if not agent:
            raise EntityNotFoundError("Agent", agent_id)
        return agent

    @staticmethod
    async def list_agents(
        session: AsyncSession,
        team_id: Optional[str] = None,
        status: Optional[str] = None,
        tier: Optional[str] = None,
    ) -> List[Agent]:
        query = select(Agent).options(
            selectinload(Agent.team),
            selectinload(Agent.skills).selectinload(AgentSkill.skill),
        )
        if team_id:
            query = query.where(Agent.team_id == team_id)
        if status:
            query = query.where(Agent.status == status)
        if tier:
            query = query.where(Agent.tier == tier)

        res = await session.scalars(query.order_by(Agent.display_name))
        return list(res.all())

    @staticmethod
    async def update_status(session: AsyncSession, agent_id: str, new_status: str) -> Agent:
        agent = await AgentService.get_agent(session, agent_id)
        old_status = agent.status

        agent.status = new_status
        log = AgentStatusLog(
            agent_id=agent.id,
            previous_status=old_status,
            new_status=new_status,
        )
        session.add(log)
        await session.commit()
        await session.refresh(agent)

        # Update telemetry
        MetricsService.set_active_agents(new_status, 1)
        return agent

    @staticmethod
    async def recalculate_workloads(session: AsyncSession) -> None:
        """Update current_active_cases counter across all agents."""
        agents = await session.scalars(select(Agent))
        for agent in agents.all():
            active_count = await session.scalar(
                select(func.count(Case.id)).where(
                    Case.assigned_agent_id == agent.id,
                    Case.status.in_(["OPEN", "IN_PROGRESS", "ESCALATED"]),
                )
            ) or 0
            agent.current_active_cases = active_count
        await session.commit()
