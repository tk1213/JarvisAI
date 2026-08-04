# Sprint 2.5 Pack H

Prerequisite: Pack G passing.

Copy Pack H into the JarvisAI project root.

Apply DI integration:

```powershell
python scripts/apply_sprint_2_5_pack_h.py
```

Quality Gate:

```powershell
python -m py_compile src/jarvis/memory/audit.py
python -m py_compile src/jarvis/memory/audit_repository.py
python -m py_compile src/jarvis/memory/audit_service.py
python -m py_compile src/jarvis/memory/service.py
python -m py_compile src/jarvis/memory/capture.py
python -m py_compile src/jarvis/core/service_factory.py
ruff check src tests tools
pytest
```

Runtime:

```powershell
python tools/test_memory_audit_live.py
```

Expected audit output should contain at least:

```text
created   audit_test_key
deleted   audit_test_key
```

Then verify existing memory behavior:

```powershell
python tools/test_memory_retrieval_live.py
jarvis chat
```
