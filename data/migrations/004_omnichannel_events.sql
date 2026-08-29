-- Migration: 004_omnichannel_events.sql
-- Description: Creates webhooks_inbound, customer_feedback, voice_transcripts, and audit_ledgers.
-- Engine: PostgreSQL 16 / SQLite 3 Compatible

CREATE TABLE IF NOT EXISTS migration_meta_004_omnichannel_events (
    id VARCHAR(64) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64) NOT NULL,
    execution_time_ms INTEGER NOT NULL
);

-- Performance Indexes & Constraints
CREATE INDEX IF NOT EXISTS idx_004_omnichannel_events_applied_at ON migration_meta_004_omnichannel_events (applied_at);
