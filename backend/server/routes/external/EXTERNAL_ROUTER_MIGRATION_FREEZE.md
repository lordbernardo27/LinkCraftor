# External Router Migration Freeze

Status: COMPLETE

Frozen At UTC: 2026-06-22T23:48:29.065305+00:00

Legacy Router Retired:
- backend.app.routers.external

Runtime Authority:
- backend.server.routes.external.runtime
- backend.server.routes.external.owner_sources
- backend.server.routes.external.auto
- backend.server.routes.external.manual
- backend.server.routes.external.resolver
- backend.server.routes.external.sources
- backend.server.routes.external.import_runs
- backend.server.routes.external.auto_cleanup
- backend.server.routes.external.sitemap_import
- backend.server.routes.external.resolve
- backend.server.routes.external.import_clear

Final Verification:
- No runtime external router imports backend.app.routers.external.
- No backend Python code references backend.app.routers.external.
- Legacy external router is not mounted.
- All legacy external route fragments have runtime coverage.

Frozen Routes:
- GET/POST external runtime routes are now owned by backend.server.routes.external modules.
