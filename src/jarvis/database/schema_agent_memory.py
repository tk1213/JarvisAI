from __future__ import annotations

AGENT_MEMORY_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_plan_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal TEXT NOT NULL,
    capabilities_json TEXT NOT NULL,
    success INTEGER NOT NULL,
    completed_steps INTEGER NOT NULL,
    failed_steps INTEGER NOT NULL,
    reflection_decision TEXT NOT NULL,
    created_at TEXT NOT NULL,
    metadata_json TEXT NOT NULL
);
"""

AGENT_MEMORY_INDEXES = (
    """
    CREATE INDEX IF NOT EXISTS
    idx_agent_plan_memories_created_at
    ON agent_plan_memories(created_at);
    """,
    """
    CREATE INDEX IF NOT EXISTS
    idx_agent_plan_memories_success
    ON agent_plan_memories(success);
    """,
)
