"""
FastAPI Enterprise Application Factory, Lifespan Hooks, Middlewares, and Metrics.
"""

import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import init_db, close_db, get_db_context
from app.core.exceptions import AppException
from app.core.logging import setup_logging, set_correlation_id
from app.core.redis import redis_manager
from app.core.telemetry import MetricsService, http_requests_total, http_request_duration_seconds
from app.services.identity_service import IdentityService
from app.services.agent_service import AgentService
from app.services.playbook_service import PlaybookService
from app.services.self_service_service import SelfServiceService
from app.services.notification_service import NotificationService
from app.schemas.auth import UserRegisterRequest
from app.schemas.agent import AgentCreate, TeamCreate, SkillCreate


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handling startup and shutdown hooks."""
    setup_logging()
    await init_db()
    await redis_manager.connect()

    # Seed core domain defaults
    async with get_db_context() as session:
        await PlaybookService.seed_default_playbooks(session)
        await SelfServiceService.seed_default_flows(session)
        await NotificationService.seed_default_templates(session)

        # Seed initial Admin & Agent users if not already present
        try:
            admin_req = UserRegisterRequest(
                email="admin@support.internal",
                password="AdminPassword123!",
                first_name="System",
                last_name="Administrator",
                role="ADMIN",
            )
            await IdentityService.register_user(session, admin_req)
        except Exception:
            pass  # Already exists

        try:
            agent_req = UserRegisterRequest(
                email="agent.sarah@support.internal",
                password="AgentPassword123!",
                first_name="Sarah",
                last_name="Jenkins",
                role="AGENT",
            )
            agent_user = await IdentityService.register_user(session, agent_req)
            
            # Create Skill & Team
            skill = await AgentService.create_skill(
                session,
                SkillCreate(code="HARDWARE_SUPPORT", name="Hardware & Electronics Diagnostics", category="TECHNICAL"),
            )
            team = await AgentService.create_team(
                session,
                TeamCreate(name="Tier 1 Electronics Team", department="CUSTOMER_SUPPORT"),
            )
            
            # Create Agent record
            await AgentService.create_agent(
                session,
                AgentCreate(
                    user_id=agent_user.id,
                    team_id=team.id,
                    employee_code="EMP-8001",
                    display_name="Sarah Jenkins",
                    tier="TIER_1",
                    max_active_cases=8,
                    languages=["en", "es"],
                    skill_ids=[skill.id],
                ),
            )
        except Exception:
            pass  # Already exists

        try:
            cust_req = UserRegisterRequest(
                email="customer.david@example.com",
                password="CustomerPassword123!",
                first_name="David",
                last_name="Miller",
                role="CUSTOMER",
            )
            await IdentityService.register_user(session, cust_req)
        except Exception:
            pass

    yield

    # Teardown
    await redis_manager.close()
    await close_db()


def create_application() -> FastAPI:
    """Instantiate and configure the FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Production Enterprise E-Commerce Customer Support & Resolution Management Platform",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Correlation ID & Telemetry Middleware
    @application.middleware("http")
    async def telemetry_and_correlation_middleware(request: Request, call_next):
        corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        set_correlation_id(corr_id)

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Track metrics
        endpoint = request.url.path
        method = request.method
        status_code = str(response.status_code)
        http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

        response.headers["X-Correlation-ID"] = corr_id
        response.headers["X-Response-Time"] = f"{duration * 1000:.2f}ms"
        return response

    # Global Exception Handler
    @application.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    # Mount API v1 Routers
    application.include_router(api_router, prefix=settings.API_V1_STR)

    # Health Probe
    @application.get("/health", tags=["Health & Monitoring"])
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": time.time(),
        }

    # Prometheus Metrics
    @application.get("/metrics", tags=["Health & Monitoring"])
    async def get_metrics():
        data, content_type = MetricsService.export_metrics()
        return Response(content=data, media_type=content_type)

    return application


app = create_application()
