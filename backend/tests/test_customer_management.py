"""
Unit & API tests for Customer Management.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerPreferenceUpdate
from app.services.customer_service import CustomerService


@pytest.mark.asyncio
async def test_customer_lifecycle(test_session: AsyncSession):
    data = CustomerCreate(
        external_customer_id="CUST-9901",
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        phone="+1-555-0188",
        preferred_language="en",
        segment="VIP",
        tier="PLATINUM",
    )
    customer = await CustomerService.create_customer(test_session, data)
    assert customer.id is not None
    assert customer.email == "jane.doe@example.com"
    assert customer.segment == "VIP"

    # Update preferences
    pref_update = CustomerPreferenceUpdate(email_notifications=True, sms_notifications=True)
    pref = await CustomerService.update_preferences(test_session, customer.id, pref_update)
    assert pref.sms_notifications is True

    # Add Tag
    tag = await CustomerService.add_tag(test_session, customer.id, "HIGH_VALUE", "#10B981")
    assert tag.tag_name == "HIGH_VALUE"

    # Fetch customer
    fetched = await CustomerService.get_customer(test_session, customer.id)
    assert len(fetched.tags) == 1
    assert len(fetched.timeline_events) >= 1


@pytest.mark.asyncio
async def test_customer_api(client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "external_customer_id": "CUST-API-01",
        "first_name": "Michael",
        "last_name": "Scott",
        "email": "michael.scott@dundermifflin.com",
        "phone": "+1-555-0199",
        "segment": "STANDARD",
        "tier": "GOLD",
    }
    res = await client.post("/api/v1/customers", json=payload, headers=headers)
    assert res.status_code == 201
    cust_id = res.json()["data"]["id"]

    # Get Customer
    res_get = await client.get(f"/api/v1/customers/{cust_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["data"]["email"] == "michael.scott@dundermifflin.com"
