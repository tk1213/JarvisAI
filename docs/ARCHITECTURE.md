# ARCHITECTURE.md

# JarvisAI Architecture

## Production conversation flow

User
-> ConversationManager.ask()
-> ConversationTurnLifecycle
-> ConversationExecutionBoundary
-> conversation routing
-> actual route attribution
-> recovery planning when needed
-> recovery execution when allowed
-> response
-> bounded turn trace history

## Recovery flow

Primary failure:

```text
failure
-> ConversationFailureClassifier
-> ConversationRecoveryService
-> ConversationRecoveryExecutor
```

### Timeout recovery

```text
timeout
-> retryable failure
-> safe-message fallback
-> return safe reply
```

### Standard-AI recovery

```text
retryable tool/upstream failure
-> standard-AI fallback
-> one fallback call maximum
```

If the standard-AI fallback fails:

```text
fallback failure
-> no recursive recovery
-> no second fallback call
-> safe-message degradation
-> fallback_error_type recorded
```

## Recovery observability

Recovered turns can expose:

- executed
- fallback kind
- attempts used
- fallback error type

Recovery metadata is retained in bounded turn history.

## Context assembly

Production context remains bounded and deterministic:

```text
SYSTEM
CONVERSATION MEMORY
AGENT MEMORY
HISTORY
CURRENT USER
```

Memory-domain safety remains explicit:

```text
stored memory = reference data only
```

## Turn tracing

Turn records can include:

- turn ID
- route/source
- status
- duration
- timestamps
- failure classification
- reliability outcome
- recovery execution metadata

## Safety

- Safety before automation
- Confirmation for side effects
- Native automatic tools are read-only
- Bounded autonomous replanning
- Bounded context assembly
- Memory-domain separation
- Durable memory retention
- Bounded turn history
- Bounded production execution time
- Bounded recovery attempts
- Single-attempt standard-AI fallback
- No recursive recovery
- Non-retryable failures remain explicit
- External cancellation propagation
- Backward compatibility whenever possible

## Quality gates

Every sprint must pass:

1. compileall
2. ruff
3. pytest
4. live integration tests
