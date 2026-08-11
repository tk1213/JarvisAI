# JarvisAI Architecture Decision Record (ADR)

## ADR-001
Responses API is the standard AI interface.

## ADR-002
ConversationManager is the entry point for user requests.

## ADR-003
Planning is separated from execution.

## ADR-004
Execution Policy controls confirmation for side effects.

## ADR-005
AI Agent Runtime orchestrates planning, execution, reflection and memory.

## ADR-006
Dependency Injection uses the central service container.

## ADR-007
Read-only capabilities execute automatically.
Side-effect capabilities require explicit confirmation.

## ADR-008
All production code must pass:
- Ruff
- Pytest
- Compile
- Live Gates
