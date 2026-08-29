"""
Database Seeding Script for development, staging, and demo environments.
Populates realistic customers, cases, agents, skills, teams, playbooks, knowledge articles, and SLA policies.
"""

import asyncio
from datetime import datetime, timedelta, timezone

from app.core.database import async_session_factory, init_db
from app.core.security import Role, hash_password
from app.models.identity import User
from app.models.customer import Customer, CustomerPreference, CustomerTag
from app.models.agent import Agent, Team, Skill, AgentSkill
from app.models.sla import SLAPolicy
from app.models.routing import RoutingRule
from app.models.knowledge import ArticleCategory, KnowledgeArticle
from app.models.case import Case, CaseTimelineEvent
from app.models.conversation import Conversation, Message
from app.services.playbook_service import PlaybookService
from app.services.self_service_service import SelfServiceService
from app.services.notification_service import NotificationService
from app.ai.rag import VectorRAGService


async def seed_all() -> None:
    print("Initializing database tables...")
    await init_db()

    async with async_session_factory() as session:
        print("Seeding playbooks, self-service flows, and templates...")
        await PlaybookService.seed_default_playbooks(session)
        await SelfServiceService.seed_default_flows(session)
        await NotificationService.seed_default_templates(session)

        # 1. Skills
        print("Seeding Skills and Teams...")
        s_hw = Skill(code="HARDWARE_SUPPORT", name="Electronics & Hardware Diagnostics", category="TECHNICAL")
        s_bill = Skill(code="PAYMENT_BILLING", name="Payment & Billing Resolution", category="BILLING")
        s_log = Skill(code="LOGISTICS_TRACE", name="Logistics & Carrier Tracing", category="LOGISTICS")
        s_vip = Skill(code="VIP_SERVICES", name="VIP Concierge Support", category="VIP")
        session.add_all([s_hw, s_bill, s_log, s_vip])
        await session.flush()

        # 2. Teams
        t_tier1 = Team(name="Tier 1 Frontline Support", department="CUSTOMER_CARE")
        t_tier2 = Team(name="Tier 2 Hardware & Diagnostics", department="TECHNICAL_SUPPORT")
        t_fin = Team(name="Finance & Fraud Operations", department="FINANCE")
        session.add_all([t_tier1, t_tier2, t_fin])
        await session.flush()

        # 3. Users & Agents
        print("Seeding Users and Agents...")
        u_admin = User(
            email="admin@ecommerce-support.internal",
            hashed_password=hash_password("AdminSecure2026!"),
            first_name="Alexandra",
            last_name="Cross",
            role=Role.ADMIN,
            is_active=True,
            is_verified=True,
        )
        u_mgr = User(
            email="manager@ecommerce-support.internal",
            hashed_password=hash_password("ManagerSecure2026!"),
            first_name="David",
            last_name="Kim",
            role=Role.MANAGER,
            is_active=True,
            is_verified=True,
        )
        u_agent1 = User(
            email="marcus.vance@support.internal",
            hashed_password=hash_password("AgentPass123!"),
            first_name="Marcus",
            last_name="Vance",
            role=Role.AGENT,
            is_active=True,
            is_verified=True,
        )
        u_agent2 = User(
            email="elena.rodriguez@support.internal",
            hashed_password=hash_password("AgentPass123!"),
            first_name="Elena",
            last_name="Rodriguez",
            role=Role.AGENT,
            is_active=True,
            is_verified=True,
        )
        session.add_all([u_admin, u_mgr, u_agent1, u_agent2])
        await session.flush()

        ag1 = Agent(
            user_id=u_agent1.id,
            team_id=t_tier2.id,
            employee_code="EMP-101",
            display_name="Marcus Vance",
            tier="TIER_2",
            status="AVAILABLE",
            max_active_cases=6,
            languages=["en", "es"],
            csat_score=4.9,
            avg_resolution_mins=12.5,
            total_resolved_cases=142,
        )
        ag2 = Agent(
            user_id=u_agent2.id,
            team_id=t_fin.id,
            employee_code="EMP-102",
            display_name="Elena Rodriguez",
            tier="TIER_1",
            status="AVAILABLE",
            max_active_cases=5,
            languages=["en", "fr"],
            csat_score=4.8,
            avg_resolution_mins=15.0,
            total_resolved_cases=98,
        )
        session.add_all([ag1, ag2])
        await session.flush()

        session.add(AgentSkill(agent_id=ag1.id, skill_id=s_hw.id, proficiency_level=5))
        session.add(AgentSkill(agent_id=ag1.id, skill_id=s_log.id, proficiency_level=4))
        session.add(AgentSkill(agent_id=ag2.id, skill_id=s_bill.id, proficiency_level=5))
        await session.flush()

        # 4. Customers
        print("Seeding Customers...")
        now = datetime.now(timezone.utc)
        c1 = Customer(
            external_customer_id="CUST-1001",
            first_name="Sarah",
            last_name="Connor",
            email="sarah.connor@example.com",
            phone="+1-555-0192",
            segment="VIP",
            tier="PLATINUM",
            total_orders_count=12,
            lifetime_value_cents=184990,
        )
        c2 = Customer(
            external_customer_id="CUST-1002",
            first_name="Alex",
            last_name="Chen",
            email="alex.chen@example.com",
            phone="+1-555-0144",
            segment="STANDARD",
            tier="SILVER",
            total_orders_count=3,
            lifetime_value_cents=42900,
        )
        session.add_all([c1, c2])
        await session.flush()

        session.add(CustomerPreference(customer_id=c1.id, email_notifications=True, sms_notifications=True))
        session.add(CustomerPreference(customer_id=c2.id, email_notifications=True, sms_notifications=False))
        session.add(CustomerTag(customer_id=c1.id, tag_name="VIP_PLATINUM", color="#8B5CF6"))
        session.add(CustomerTag(customer_id=c1.id, tag_name="HIGH_LTV", color="#10B981"))
        await session.flush()

        # 5. Knowledge Base
        print("Seeding Knowledge Base & Vector Indexing...")
        cat_returns = ArticleCategory(
            name="Returns & Replacements", slug="returns-and-replacements", display_order=1
        )
        cat_shipping = ArticleCategory(name="Shipping & Delivery", slug="shipping-and-delivery", display_order=2)
        cat_billing = ArticleCategory(name="Billing & Payments", slug="billing-and-payments", display_order=3)
        session.add_all([cat_returns, cat_shipping, cat_billing])
        await session.flush()

        art1 = KnowledgeArticle(
            title="30-Day Electronics Return & Replacement Policy",
            slug="electronics-return-policy",
            content="All electronics and wireless headphones are covered under our 30-Day Hassle-Free Replacement Policy. If your item arrives damaged or develops a hardware fault within 30 days of confirmed delivery, our support team can issue a zero-cost replacement order with expedited courier dispatch or a full refund to your original payment method.",
            category_id=cat_returns.id,
            visibility="PUBLIC",
            tags=["returns", "replacement", "electronics", "warranty"],
            author_id=u_admin.id,
            status="PUBLISHED",
            published_at=now,
        )
        art2 = KnowledgeArticle(
            title="Late Delivery & Carrier In-Transit Delay Guide",
            slug="late-delivery-guide",
            content="Packages in transit occasionally experience carrier weather delays or hub routing exceptions. If tracking shows no movement for more than 48 hours past the estimated delivery window, support agents can file an automated carrier trace and issue a $10.00 courtesy credit or dispatch an emergency reshipment.",
            category_id=cat_shipping.id,
            visibility="PUBLIC",
            tags=["shipping", "fedex", "delays", "tracking"],
            author_id=u_admin.id,
            status="PUBLISHED",
            published_at=now,
        )
        session.add_all([art1, art2])
        await session.flush()

        # Index articles in vector store
        await VectorRAGService.index_knowledge_article(session, art1)
        await VectorRAGService.index_knowledge_article(session, art2)

        # 6. Sample Live Cases
        print("Seeding Sample Cases and Conversations...")
        case1 = Case(
            case_number="CASE-20260829-1001",
            customer_id=c1.id,
            title="AeroSound ANC Headphones arrived with broken headband",
            description="Package box was crushed upon delivery and left earcup plastic is cracked. Requesting replacement.",
            category="PRODUCT",
            subcategory="DAMAGED_ITEM",
            priority="HIGH",
            status="OPEN",
            source="WEB_PORTAL",
            assigned_agent_id=ag1.id,
            assigned_team_id=t_tier2.id,
            order_id="ORD-5001",
            product_id="PROD-9001",
            payment_id="PAY-8801",
            shipment_id="SHIP-7701",
            sentiment_score=-0.7,
            frustration_score=45.0,
            first_response_due_at=now + timedelta(minutes=30),
            resolution_due_at=now + timedelta(hours=8),
        )
        session.add(case1)
        await session.flush()

        conv1 = Conversation(case_id=case1.id, channel="WEB_CHAT", status="OPEN")
        session.add(conv1)
        await session.flush()

        m1 = Message(
            conversation_id=conv1.id,
            sender_type="CUSTOMER",
            sender_name="Sarah Connor",
            content="Hi, my AeroSound headphones arrived crushed and the headband is broken. Can I get a replacement?",
        )
        m2 = Message(
            conversation_id=conv1.id,
            sender_type="AGENT",
            sender_name="Marcus Vance",
            content="Hello Sarah! I am so sorry about the damage. I have verified your order delivery and will authorize an expedited zero-cost replacement for you right away.",
            sender_id=u_agent1.id,
        )
        session.add_all([m1, m2])
        await session.commit()
        print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_all())
