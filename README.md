# JarvisAI Sprint 4.2.2 — Pack A

## Structured Tool Arguments

This pack is built from the uploaded JarvisAI source tree.

### Adds

- `CapabilityArgument`
- JSON Schema types for string, integer, number, boolean, array and object
- required fields
- enums
- minimum and maximum
- array item schemas
- OpenAI tool-schema serialization

### Compatibility

Existing definitions remain valid:

```python
arguments={
    "device_query": "Device description",
}
```

Structured definitions are now available:

```python
arguments={
    "limit": CapabilityArgument(
        type="integer",
        description="Maximum records.",
        required=True,
        minimum=1,
        maximum=100,
    ),
}
```

### Install

Place and extract the ZIP under `D:\Projects\JarvisAI\packs`, then run
from the project root:

```powershell
& .\packs\Sprint_4.2.2_Pack_A\INSTALL.ps1
& .\packs\Sprint_4.2.2_Pack_A\VERIFY.ps1
```

The installer creates timestamped backups.
