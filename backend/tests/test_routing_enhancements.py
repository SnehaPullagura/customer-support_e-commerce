import pytest
from app.services.routing_service import RoutingService


def test_routing_affinity_scoring_and_ranking():
    # Agent 1: Full skill match, 0 active cases, 5.0 CSAT -> Max affinity
    score1 = RoutingService.calculate_agent_affinity_score(
        agent_skills=["BILLING", "RETURNS"],
        required_skills=["BILLING", "RETURNS"],
        current_active=0,
        max_active=5,
        csat=5.0,
    )
    assert score1 == 100.0

    # Agent 2: Partial skill match, at capacity (5/5), 4.0 CSAT
    score2 = RoutingService.calculate_agent_affinity_score(
        agent_skills=["BILLING"],
        required_skills=["BILLING", "RETURNS"],
        current_active=5,
        max_active=5,
        csat=4.0,
    )
    assert score2 < 50.0

    # Candidate ranking
    agents = [
        {"id": "agent_b", "name": "Bob", "skills": ["BILLING"], "current_active_cases": 4, "max_active_cases": 5, "csat_score": 4.0},
        {"id": "agent_a", "name": "Alice", "skills": ["BILLING", "RETURNS"], "current_active_cases": 1, "max_active_cases": 5, "csat_score": 4.9},
    ]
    ranked = RoutingService.rank_candidate_agents(agents, required_skills=["BILLING", "RETURNS"])
    assert ranked[0]["id"] == "agent_a"
    assert ranked[0]["affinity_score"] > ranked[1]["affinity_score"]
