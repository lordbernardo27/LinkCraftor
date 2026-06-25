# LinkCraftor Legacy Subsystem Retirement Report

Generated:
2026-06-25T13:30:36.096276+00:00

---

# Executive Summary

The Phase 2.0 Legacy App Retirement Audit has completed successfully.

The investigation confirms that the runtime architecture has transitioned from
`backend/app/*`
to
`backend/server/*`.

No runtime dependency on the legacy application layer remains.

---

# Audit Phases Completed

? Phase 2.0.1 ? Audit backend/app/main.py

? Phase 2.0.2 ? Audit backend/app/*

? Phase 2.0.3 ? Remaining Legacy Routers

? Phase 2.0.4 ? Remaining Legacy Stores

? Phase 2.0.5 ? Remaining Legacy Services

? Phase 2.0.6 ? Runtime Ownership Map

? Phase 2.0.7 ? Retirement Candidate Classification

? Phase 2.0.8 ? Retirement Safety Verification

? Phase 2.0.9 ? Runtime Authority Freeze

? Phase 2.0.10 ? Retirement Report

---

# Runtime Authority

Canonical runtime:

backend/server/main.py

Canonical runtime routes:

backend/server/routes/*

backend/server/routes/external/*

backend/server/orchestration/*

backend/server/owner/*

backend/server/tms/*

---

# Legacy Layer Status

Runtime imports of backend.app:

NONE

Deployment entrypoints:

backend/server/main.py

Legacy runtime entrypoints:

NONE

---

# Remaining Legacy Components

Temporary Compatibility Shell

backend/app/main.py

Status:

Temporary compatibility layer

Purpose:

Owner UI

Health endpoints

Static assets

Compatibility hosting

---

Legacy Archive Candidate

backend/app/routers/external.py

Status:

Frozen

Purpose:

Historical router

Legacy persistence

Migration archive

---

Verification Candidate

backend/app/helix_auth/pools/authority_domain_pool.py

Status:

Verify before retirement

---

Storage Helpers

backend/app/config.py

backend/app/services/exporters.py

backend/app/services/storage_local.py

Status:

Likely archive candidates after final reference confirmation.

---

# Retirement Decision

Runtime ownership migration:

COMPLETE

Runtime authority freeze:

COMPLETE

Runtime dependency on backend/app:

NONE

Legacy runtime ownership:

REMOVED

Retirement readiness:

READY FOR CONTROLLED ARCHIVAL

Immediate deletion:

NOT RECOMMENDED

Recommended strategy:

1. Quarantine

2. Archive

3. Final removal after release verification

---

# Architectural Milestone

The LinkCraftor runtime architecture now officially recognizes:

backend/server

as the single source of runtime authority.

The legacy backend/app subsystem is officially deprecated.

Phase 2.0 is complete.
