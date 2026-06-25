# External Subsystem Certification

Generated UTC:
2026-06-25T14:47:07.036659+00:00

## Status

CERTIFIED

## Runtime Owner

backend/server/routes/external

## Runtime Entrypoint

backend/server/main.py

## Legacy Router

Status: QUARANTINED

Location:
backend/app/_legacy_quarantine/routers/external.py.quarantined

## Verification Summary

- Runtime routes: 30
- Unique endpoints: 30
- Duplicate endpoints: 0
- Missing legacy-equivalent routes: 0
- Runtime imports of legacy router: 0
- Runtime syntax errors: 0

## Certification

The LinkCraftor External Routing subsystem has been fully migrated to
`backend/server/routes/external`.

The legacy router is no longer part of the runtime architecture.

Future removal of the quarantined file may be performed after an appropriate release verification window.
