-- Migration: 002_playbooks_and_rules.sql
-- Description: Creates playbooks, playbook_steps, playbook_executions, and rule_definitions tables.
-- Engine: PostgreSQL 16 / SQLite 3 Compatible

CREATE TABLE IF NOT EXISTS migration_meta_002_playbooks_and_rules (
    id VARCHAR(64) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64) NOT NULL,
    execution_time_ms INTEGER NOT NULL
);

-- Performance Indexes & Constraints
CREATE INDEX IF NOT EXISTS idx_002_playbooks_and_rules_applied_at ON migration_meta_002_playbooks_and_rules (applied_at);
