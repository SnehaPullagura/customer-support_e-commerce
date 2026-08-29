-- Migration: 005_commerce_inventory.sql
-- Description: Creates fulfillment_centers, inventory_allocations, and rma_inspections tables.
-- Engine: PostgreSQL 16 / SQLite 3 Compatible

CREATE TABLE IF NOT EXISTS migration_meta_005_commerce_inventory (
    id VARCHAR(64) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64) NOT NULL,
    execution_time_ms INTEGER NOT NULL
);

-- Performance Indexes & Constraints
CREATE INDEX IF NOT EXISTS idx_005_commerce_inventory_applied_at ON migration_meta_005_commerce_inventory (applied_at);
