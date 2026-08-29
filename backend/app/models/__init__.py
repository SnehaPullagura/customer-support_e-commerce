"""
Model registry exporting all database entities across all 25 domains.
"""

from app.models.base import BaseEntity
from app.models.identity import User, UserSession, LoginHistory
from app.models.customer import (
    Customer,
    CustomerPreference,
    CustomerTag,
    CustomerDevice,
    CustomerTimelineEvent,
)
from app.models.case import Case, CaseLink, CaseTimelineEvent
from app.models.ticket import Ticket, TicketAttachment, TicketTag, TicketHistory
from app.models.conversation import (
    Conversation,
    Message,
    MessageAttachment,
    MessageReadReceipt,
    ConversationParticipant,
)
from app.models.agent import Team, Skill, Agent, AgentSkill, AgentStatusLog
from app.models.routing import RoutingQueue, RoutingRule, RoutingExecutionLog
from app.models.sla import SLAPolicy, SLATracker, SLAPauseLog, SLABreachLog, HolidayCalendar
from app.models.escalation import EscalationPolicy, EscalationEvent
from app.models.resolution import (
    Resolution,
    ResolutionAction,
    ResolutionApproval,
    CustomerFeedback,
)
from app.models.playbook import Playbook, PlaybookStep, PlaybookExecution, PlaybookStepLog
from app.models.knowledge import (
    ArticleCategory,
    KnowledgeArticle,
    ArticleVersion,
    ArticleFeedback,
)
from app.models.self_service import TroubleshootingFlow, SelfServiceSession
from app.models.returns import ReturnRequest, ReturnItem, ReplacementOrder
from app.models.refunds import RefundRequest, RefundTransaction
from app.models.notification import NotificationTemplate, Notification
from app.models.customer_intelligence import (
    CustomerFrustrationScore,
    CustomerChurnRisk,
)
from app.models.ai import AIInferenceLog, AISuggestedReply, VectorDocumentChunk
from app.models.analytics import (
    DailyOperationalMetric,
    AgentPerformanceSnapshot,
    ProductComplaintMetric,
)
from app.models.admin import SystemSetting, FeatureFlag
from app.models.audit import AuditEvent
from app.models.integration import (
    IntegrationConfig,
    WebhookSubscription,
    WebhookDeliveryLog,
)

__all__ = [
    "BaseEntity",
    "User",
    "UserSession",
    "LoginHistory",
    "Customer",
    "CustomerPreference",
    "CustomerTag",
    "CustomerDevice",
    "CustomerTimelineEvent",
    "Case",
    "CaseLink",
    "CaseTimelineEvent",
    "Ticket",
    "TicketAttachment",
    "TicketTag",
    "TicketHistory",
    "Conversation",
    "Message",
    "MessageAttachment",
    "MessageReadReceipt",
    "ConversationParticipant",
    "Team",
    "Skill",
    "Agent",
    "AgentSkill",
    "AgentStatusLog",
    "RoutingQueue",
    "RoutingRule",
    "RoutingExecutionLog",
    "SLAPolicy",
    "SLATracker",
    "SLAPauseLog",
    "SLABreachLog",
    "HolidayCalendar",
    "EscalationPolicy",
    "EscalationEvent",
    "Resolution",
    "ResolutionAction",
    "ResolutionApproval",
    "CustomerFeedback",
    "Playbook",
    "PlaybookStep",
    "PlaybookExecution",
    "PlaybookStepLog",
    "ArticleCategory",
    "KnowledgeArticle",
    "ArticleVersion",
    "ArticleFeedback",
    "TroubleshootingFlow",
    "SelfServiceSession",
    "ReturnRequest",
    "ReturnItem",
    "ReplacementOrder",
    "RefundRequest",
    "RefundTransaction",
    "NotificationTemplate",
    "Notification",
    "CustomerFrustrationScore",
    "CustomerChurnRisk",
    "AIInferenceLog",
    "AISuggestedReply",
    "VectorDocumentChunk",
    "DailyOperationalMetric",
    "AgentPerformanceSnapshot",
    "ProductComplaintMetric",
    "SystemSetting",
    "FeatureFlag",
    "AuditEvent",
    "IntegrationConfig",
    "WebhookSubscription",
    "WebhookDeliveryLog",
]
