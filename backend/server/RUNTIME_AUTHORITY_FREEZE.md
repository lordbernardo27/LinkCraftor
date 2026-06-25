# LinkCraftor Runtime Authority Freeze

Freeze timestamp UTC: 2026-06-25T13:29:09.394847+00:00

## Runtime Authority

The canonical runtime application authority is:

- `backend/server/main.py`

The canonical runtime route layer is:

- `backend/server/routes/*`
- `backend/server/routes/external/*`
- `backend/server/orchestration/*`
- `backend/server/owner/*`
- `backend/server/tms/*`

## Legacy App Status

The legacy application layer is no longer runtime-owned.

Legacy layer:

- `backend/app/*`

Current retirement status:

- `backend/app/main.py` remains a temporary compatibility shell.
- `backend/app/routers/external.py` is a legacy archive/quarantine candidate.
- No executable runtime dependency on `backend.app.*` was found.
- No deployment entrypoint to `backend/app/main.py` was found.
- Runtime does not import `backend.app.*`.

## Authority Rules

1. New runtime routes must be added under `backend/server/routes/*` or an approved runtime submodule.
2. No new route should be added under `backend/app/*`.
3. No runtime module should import from `backend.app.*`.
4. `backend/app/routers/external.py` must remain frozen.
5. Legacy files may only be archived, quarantined, or retired after reference checks.
6. `backend/server/main.py` is the only approved FastAPI runtime entrypoint.

## Freeze Decision

Runtime authority is frozen to `backend/server`.

Phase 2.0.9 status: COMPLETE.
