-- Migration: 001_initial_schema.sql
-- Description: Creates initial core tables: customers, orders, cases, timeline_events, messages.
-- Engine: PostgreSQL 16 / SQLite 3 Compatible

CREATE TABLE IF NOT EXISTS migration_meta_001_initial_schema (
    id VARCHAR(64) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64) NOT NULL,
    execution_time_ms INTEGER NOT NULL
);

-- Performance Indexes & Constraints
CREATE INDEX IF NOT EXISTS idx_001_initial_schema_applied_at ON migration_meta_001_initial_schema (applied_at);
