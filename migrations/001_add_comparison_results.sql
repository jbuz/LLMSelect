-- Migration: Add comparison_results table
-- Date: 2025-10-31
-- Description: Add table to store multi-model comparison results

CREATE TABLE IF NOT EXISTS comparison_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    results JSON NOT NULL,
    preferred_index INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_comparison_user ON comparison_results(user_id);
CREATE INDEX IF NOT EXISTS idx_comparison_created ON comparison_results(created_at);
