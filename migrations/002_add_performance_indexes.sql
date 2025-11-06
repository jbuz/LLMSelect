-- Migration: Add performance indexes for Phase 4
-- Date: 2025-11-06
-- Description: Add additional indexes for optimal query performance

-- Add provider-specific conversation index (for filtering by provider)
CREATE INDEX IF NOT EXISTS idx_conversations_user_provider 
ON conversations(user_id, provider);

-- Add user-provider index for API keys (for quick lookup)
CREATE INDEX IF NOT EXISTS idx_apikeys_user_provider 
ON api_keys(user_id, provider);

-- Note: The following indexes already exist in models:
-- - idx_conversation_user_created (conversations.user_id, conversations.created_at)
-- - idx_message_conversation_created (messages.conversation_id, messages.created_at)
-- - idx_comparison_user_created (comparison_results.user_id, comparison_results.created_at)
