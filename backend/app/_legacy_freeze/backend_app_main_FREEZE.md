# backend/app/main.py Freeze

Freeze timestamp UTC:
2026-06-25T14:12:46.887093+00:00

## File

backend/app/main.py

## Status

Frozen as legacy compatibility shell.

## Reason

Runtime ownership has moved to:

backend/server/main.py

Phase 3.1 verified:

- backend/server/main.py is the only runtime FastAPI app.
- Runtime imports no backend.app modules.
- backend/app/main.py only remains as a temporary compatibility shell.
- Legacy depends on runtime, not the reverse.

## Freeze Rules

1. Do not add new runtime routes to backend/app/main.py.
2. Do not add new runtime imports from backend/app into backend/server.
3. Do not expand compatibility responsibilities.
4. Any required runtime behavior must be implemented under backend/server.
5. This file may only be archived or quarantined after verification.

## SHA256

55790e8a73865cef2ec3465bc5d6823547775459c2322a2be44b82a8328337bf
