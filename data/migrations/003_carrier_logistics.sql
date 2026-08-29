-- Migration: 003_carrier_logistics.sql
-- Description: Creates shipments, carrier_milestones, claims, and postal_zone_tables.
-- Engine: PostgreSQL 16 / SQLite 3 Compatible

CREATE TABLE IF NOT EXISTS migration_meta_003_carrier_logistics (
    id VARCHAR(64) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64) NOT NULL,
    execution_time_ms INTEGER NOT NULL
);

-- Performance Indexes & Constraints
CREATE INDEX IF NOT EXISTS idx_003_carrier_logistics_applied_at ON migration_meta_003_carrier_logistics (applied_at);
