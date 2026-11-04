# AK.5 ? Connected Domain Production Trust Handoff

Status: BLOCKED ? CANONICAL IDENTITY INTEGRATION REQUIRED

## Architectural Authorities

1. Canonical Identity Service
   - Sole application authentication authority.
   - Validates trusted authentication and internal principal identity.
   - External identity subject IDs are mappings, not internal principals.

2. Canonical Authorization Service
   - Sole workspace ownership, membership, role and permission authority.
   - Returns current, resource-scoped and revocation-aware decisions.
   - Unavailable, missing, stale or conflicting authority means DENY.

3. Universal Runtime
   - Consumes verified authorization evidence.
   - Never creates workspace ownership or authentication evidence.
   - Enforces execution permission before any protected mutation.

## Canonical Target

Workspace: ws_whattoexpect_com
Domain: whattoexpect.com
Workflow: workflow_connect_domain_a3ab8627c22ea34444e0aef30128889a

Only the existing six jobs in EXPECTED_SCOPE are in scope.
The five legacy queued jobs remain excluded.

## Required Identity Evidence

- Verified internal principal identity and principal type.
- Trusted issuer and verified authentication provenance.
- Current principal status and revocation status.
- Verified workspace-to-account relationship.
- Active membership or explicitly delegated permission.
- Canonical authorization decision with audit reference.
- Resource, action, expiry and revision binding.

A workspace profile, caller-provided user ID,
unverified JWT claims, or API context object alone
does not satisfy this requirement.

## Required Worker Evidence

- Verified registered worker and instance identity.
- Valid current registration, heartbeat and assignment.
- Authorized runtime capability and handler registration.
- Lease and fence binding where required.
- Trusted workload authentication and revocation status.

## Required Execution Evidence

- Exact workflow ID, workspace ID and job ID.
- Permitted operations: CONSUME_QUEUE, START_EXECUTION
  and INVOKE_HANDLER as applicable.
- Exact authorized handler and registered job type.
- Validity interval and replay protection.
- Audit evidence tied to authoritative issuer and grants.

## Enforcement Rules

1. Default DENY for all six jobs.
2. Authenticate and authorize through canonical services.
3. Validate workspace, worker, workflow and candidate job.
4. Enforce authority under the atomic dequeue lock.
5. Revalidate when authorization or lease state can change.
6. Authorize the handler before dispatch.
7. Protect REUSE_EXISTING and alternative mutation paths.
8. Deny when evidence is missing, revoked, stale or mismatched.
9. Never treat a caller-supplied boolean as trusted authority.
10. Do not enable the worker or queue claim feature flags
    until end-to-end certification succeeds.

## Current Implementation

- Worker pre-start authorization guard: IMPLEMENTED.
- Worker pre-claim authorization guard: IMPLEMENTED.
- Six-job atomic queue deny guard: IMPLEMENTED.
- Isolated recovery rehearsal: PASSED.
- Canonical authenticated workspace authority: NOT CONNECTED.
- Trusted production worker authority: NOT CONNECTED.
- Job-specific production authorization: NOT CONNECTED.
- End-to-end production execution permission: DENIED.

## Cross-Architecture Dependencies

Identity Architecture production integration gate:
PENDING ? previously deferred.

Authorization Service workspace ownership integration:
PENDING.

Worker registry and verified workload authentication:
PENDING.

Runtime per-job enforcement with trusted decisions:
PENDING.

## Exit Criteria

AK.5 requires real provider-backed authentication,
verified ownership/membership, current authorization
decisions and negative/revocation tests.

AK overall requires trusted queue and handler
enforcement, auditability and end-to-end certification.

Until all relevant gates pass, the canonical six jobs
must remain unclaimed and the production worker disabled.
