# JarvisAI Developer Handbook v1.0

## Purpose
This handbook defines the engineering standards for JarvisAI.

## Core Principles
- Production-first development
- Stability before new features
- Backward compatibility
- Test-first mindset
- Async Python 3.12+
- Type hints everywhere

## Architecture
- ConversationManager
- AIService
- OpenAIClient (Responses API)
- Planner
- Tool Calling
- Execution Engine
- Reflection
- Memory
- Smart Home
- Skills

## Coding Standards
- Ruff clean
- Pytest required
- No blind exceptions unless justified
- Small focused modules
- Dependency injection through container

## Workflow
1. Implement feature
2. Unit tests
3. Live test
4. Ruff
5. Compile
6. Gate
7. Git checkpoint

## Branch Policy
- main always releasable
- Small atomic commits
- Tagged sprint releases

## Quality Gates
- Compile
- Ruff
- Pytest
- Live integration tests

## Sprint Philosophy
Each sprint ends with:
- Static Gate PASS
- Live Gate PASS
- Clean git status
