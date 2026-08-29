"""
Consolidated API v1 Router mounting all 24 domain endpoint routers.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    customers,
    cases,
    tickets,
    conversations,
    agents,
    routing,
    sla,
    escalations,
    resolutions,
    playbooks,
    knowledge,
    self_service,
    returns,
    refunds,
    notifications,
    customer_intelligence,
    ai,
    analytics,
    admin,
    audit,
    integrations,
    commerce,
    ws,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["01. Identity & Auth"])
api_router.include_router(customers.router, prefix="/customers", tags=["02. Customer Management"])
api_router.include_router(cases.router, prefix="/cases", tags=["03. Case Management"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["04. Ticket Management"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["05. Conversation Management"])
api_router.include_router(agents.router, prefix="/agents", tags=["06. Agent Management"])
api_router.include_router(routing.router, prefix="/routing", tags=["07. Intelligent Routing"])
api_router.include_router(commerce.router, prefix="/commerce", tags=["08. Commerce Context & Adapter"])
api_router.include_router(sla.router, prefix="/sla", tags=["09. SLA Management"])
api_router.include_router(escalations.router, prefix="/escalations", tags=["10. Escalation Management"])
api_router.include_router(resolutions.router, prefix="/resolutions", tags=["11. Resolution Engine"])
api_router.include_router(playbooks.router, prefix="/playbooks", tags=["12. Resolution Playbooks"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["13. Knowledge Base"])
api_router.include_router(self_service.router, prefix="/self-service", tags=["14. Customer Self-Service"])
api_router.include_router(returns.router, prefix="/returns", tags=["15. Return & Replacement Support"])
api_router.include_router(refunds.router, prefix="/refunds", tags=["16. Refund Support"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["17. Notification Service"])
api_router.include_router(customer_intelligence.router, prefix="/intelligence", tags=["18. Customer Intelligence"])
api_router.include_router(ai.router, prefix="/ai", tags=["19. AI Assistant & RAG"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["21. Analytics & Metrics"])
api_router.include_router(admin.router, prefix="/admin", tags=["22. Administration"])
api_router.include_router(audit.router, prefix="/audit", tags=["23. Audit & Security"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["24. Integrations & Webhooks"])
api_router.include_router(ws.router, prefix="/ws", tags=["25. Real-Time WebSockets"])
