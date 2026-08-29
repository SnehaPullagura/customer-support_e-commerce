"""
Agent Workforce Management endpoints.
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, CurrentUser, require_roles
from app.core.security import Role
from app.schemas.common import StandardResponse
from app.schemas.agent import (
    AgentCreate,
    AgentUpdate,
    AgentResponse,
    AgentDetailResponse,
    AgentStatusUpdateRequest,
    SkillCreate,
    SkillResponse,
    TeamCreate,
    TeamResponse,
)
from app.services.agent_service import AgentService

router = APIRouter()


@router.post("", response_model=StandardResponse[AgentResponse], status_code=status.HTTP_201_CREATED)
async def create_agent(
    data: AgentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.MANAGEMENT))],
):
    agent = await AgentService.create_agent(db, data)
    return StandardResponse(
        message="Agent profile created successfully",
        data=AgentResponse.model_validate(agent),
    )


@router.get("", response_model=StandardResponse[List[AgentDetailResponse]])
async def list_agents(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
    team_id: Optional[str] = None,
    status: Optional[str] = None,
    tier: Optional[str] = None,
):
    agents = await AgentService.list_agents(db, team_id=team_id, status=status, tier=tier)
    return StandardResponse(data=[AgentDetailResponse.model_validate(a) for a in agents])


@router.get("/{agent_id}", response_model=StandardResponse[AgentDetailResponse])
async def get_agent(
    agent_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    agent = await AgentService.get_agent(db, agent_id)
    return StandardResponse(data=AgentDetailResponse.model_validate(agent))


@router.patch("/{agent_id}/status", response_model=StandardResponse[AgentResponse])
async def update_agent_status(
    agent_id: str,
    data: AgentStatusUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    agent = await AgentService.update_status(db, agent_id, data.status)
    return StandardResponse(
        message=f"Agent status updated to {data.status}",
        data=AgentResponse.model_validate(agent),
    )


@router.post("/skills", response_model=StandardResponse[SkillResponse], status_code=status.HTTP_201_CREATED)
async def create_skill(
    data: SkillCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.MANAGEMENT))],
):
    skill = await AgentService.create_skill(db, data)
    return StandardResponse(message="Skill created", data=SkillResponse.model_validate(skill))


@router.get("/skills/list", response_model=StandardResponse[List[SkillResponse]])
async def list_skills(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    skills = await AgentService.list_skills(db)
    return StandardResponse(data=[SkillResponse.model_validate(s) for s in skills])


@router.post("/teams", response_model=StandardResponse[TeamResponse], status_code=status.HTTP_201_CREATED)
async def create_team(
    data: TeamCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.MANAGEMENT))],
):
    team = await AgentService.create_team(db, data)
    return StandardResponse(message="Team created", data=TeamResponse.model_validate(team))


@router.get("/teams/list", response_model=StandardResponse[List[TeamResponse]])
async def list_teams(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    teams = await AgentService.list_teams(db)
    return StandardResponse(data=[TeamResponse.model_validate(t) for t in teams])
