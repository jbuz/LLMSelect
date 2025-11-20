-- Migration: Add override_system_key column to api_keys table
-- Created: 2025-11-20
-- Description: Allows users to explicitly override system-wide environment API keys

-- Add the new column with default value
ALTER TABLE api_keys ADD COLUMN override_system_key BOOLEAN NOT NULL DEFAULT 0;

-- Add index for queries that check override status
CREATE INDEX idx_apikeys_override ON api_keys(user_id, provider, override_system_key);
