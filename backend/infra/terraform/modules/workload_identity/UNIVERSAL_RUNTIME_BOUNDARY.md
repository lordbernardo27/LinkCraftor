# Universal Runtime / AWS Workload Identity Boundary

AWS IAM provides the AWS-resource identity.

The existing LinkCraftor Universal Runtime remains authoritative for:

- worker identity validation
- execution authorization
- signed execution grants
- runtime authorization
- service-to-service trust
- worker lifecycle
- leasing
- heartbeat
- runtime permission fencing

The AWS workload role MUST NOT:

- replace the Universal Runtime worker
- bypass runtime authorization
- grant TerraformApplyRole
- activate queued jobs
- establish a second worker service
- become the application customer identity

Canonical existing authorities include:

- backend/server/runtime/security/ak6_operational_trust.py
- backend/server/runtime/security/ak6_signed_execution_grants.py
- backend/server/runtime/security/execution_authorization.py
- backend/server/runtime/security/runtime_authorization.py
- backend/server/runtime/security/service_to_service_trust.py
- backend/server/runtime/security/worker_identity_validation.py
- backend/server/runtime/universal_runtime_worker_service.py
