"""
Operational metrics and Prometheus telemetry collector.
"""

import time
from typing import Dict
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Operational Metrics
http_requests_total = Counter(
    "support_http_requests_total",
    "Total HTTP Requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "support_http_request_duration_seconds",
    "HTTP Request Latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

cases_created_total = Counter(
    "support_cases_created_total",
    "Total customer support cases created",
    ["category", "priority", "source"],
)

cases_resolved_total = Counter(
    "support_cases_resolved_total",
    "Total customer support cases resolved",
    ["category", "resolution_type"],
)

sla_breaches_total = Counter(
    "support_sla_breaches_total",
    "Total SLA breaches recorded",
    ["policy_name", "breach_type", "priority"],
)

active_agents_gauge = Gauge(
    "support_active_agents_total",
    "Number of currently active agents",
    ["status"],
)

queue_depth_gauge = Gauge(
    "support_queue_depth_total",
    "Unassigned open cases in queue",
    ["priority"],
)

ai_inferences_total = Counter(
    "support_ai_inferences_total",
    "Total AI inference operations executed",
    ["task", "status"],
)


class MetricsService:
    """Helper wrapper for Prometheus instrumentation."""

    @staticmethod
    def record_case_created(category: str, priority: str, source: str = "WEB") -> None:
        cases_created_total.labels(category=category, priority=priority, source=source).inc()

    @staticmethod
    def record_case_resolved(category: str, resolution_type: str) -> None:
        cases_resolved_total.labels(category=category, resolution_type=resolution_type).inc()

    @staticmethod
    def record_sla_breach(policy_name: str, breach_type: str, priority: str) -> None:
        sla_breaches_total.labels(
            policy_name=policy_name, breach_type=breach_type, priority=priority
        ).inc()

    @staticmethod
    def set_active_agents(status: str, count: int) -> None:
        active_agents_gauge.labels(status=status).set(count)

    @staticmethod
    def set_queue_depth(priority: str, count: int) -> None:
        queue_depth_gauge.labels(priority=priority).set(count)

    @staticmethod
    def record_ai_inference(task: str, success: bool = True) -> None:
        status_str = "success" if success else "failed"
        ai_inferences_total.labels(task=task, status=status_str).inc()

    @staticmethod
    def export_metrics() -> tuple[bytes, str]:
        return generate_latest(), CONTENT_TYPE_LATEST
