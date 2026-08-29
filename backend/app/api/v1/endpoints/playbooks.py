"""
Resolution Playbook endpoints.
"""

from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import CurrentUser, require_roles
from app.core.security import Role
from app.schemas.common import StandardResponse
from app.schemas.playbook import (
    PlaybookResponse,
    PlaybookExecutionResponse,
    PlaybookStepExecuteRequest,
)
from app.services.playbook_service import PlaybookService

router = APIRouter()


@router.get("", response_model=StandardResponse[List[PlaybookResponse]])
async def list_playbooks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
    category: Optional[str] = None,
):
    pbs = await PlaybookService.list_playbooks(db, category=category)
    return StandardResponse(data=[PlaybookResponse.model_validate(p) for p in pbs])


@router.get("/{playbook_id}", response_model=StandardResponse[PlaybookResponse])
async def get_playbook(
    playbook_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    pb = await PlaybookService.get_playbook(db, playbook_id)
    return StandardResponse(data=PlaybookResponse.model_validate(pb))


@router.post("/case/{case_id}/start/{playbook_id}", response_model=StandardResponse[PlaybookExecutionResponse], status_code=status.HTTP_201_CREATED)
async def start_playbook(
    case_id: str,
    playbook_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    execution = await PlaybookService.start_execution(
        db, case_id=case_id, playbook_id=playbook_id, agent_id=current_user.user_id
    )
    return StandardResponse(
        message="Playbook execution initiated",
        data=PlaybookExecutionResponse.model_validate(execution),
    )


@router.post("/executions/{execution_id}/step", response_model=StandardResponse[PlaybookExecutionResponse])
async def execute_playbook_step(
    execution_id: str,
    data: PlaybookStepExecuteRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[CurrentUser, Depends(require_roles(Role.STAFF))],
):
    execution = await PlaybookService.execute_step(
        db,
        execution_id=execution_id,
        step_id=data.step_id,
        status=data.status,
        notes=data.notes,
        result_data_json=data.result_data_json,
        actor_id=current_user.user_id,
    )
    return StandardResponse(
        message="Step executed",
        data=PlaybookExecutionResponse.model_validate(execution),
    )
