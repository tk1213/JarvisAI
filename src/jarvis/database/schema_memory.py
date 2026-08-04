from __future__ import annotations

MEMORY_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    category TEXT NOT NULL,

    key TEXT NOT NULL,

    value TEXT NOT NULL,

    importance INTEGER NOT NULL DEFAULT 1,

    source TEXT NOT NULL DEFAULT "user",

    created_at TEXT NOT NULL,

    updated_at TEXT NOT NULL
);
"""

MEMORY_INDEXES = (
    """
    CREATE INDEX IF NOT EXISTS
    idx_memories_key
    ON memories(key);
    """,
    """
    CREATE INDEX IF NOT EXISTS
    idx_memories_category
    ON memories(category);
    """,
    """
    CREATE INDEX IF NOT EXISTS
    idx_memories_importance
    ON memories(importance);
    """,
)