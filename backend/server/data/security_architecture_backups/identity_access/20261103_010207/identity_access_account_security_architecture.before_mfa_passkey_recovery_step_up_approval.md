# LinkCraftor Identity, Access & Account Security Architecture

## Domain Declaration

- Domain ID: `security.identity_access_account_security`
- Domain name: Identity, Access & Account Security
- Parent domain: LinkCraftor Security Architecture
- Architecture version: `0.1.0-draft`
- Implementation status: `FOUNDATION_IN_PROGRESS`
- Security classification: `SECURITY_CRITICAL`
- Default posture: `DENY_AND_FAIL_SECURE`

## Purpose

This domain governs customer and operator identity, authentication, authorization, credential protection, account recovery, authentication-abuse prevention, and account-takeover detection throughout LinkCraftor.

## Canonical Authority Boundaries

This domain is the architectural authority for:

- User signup and account verification
- Login and logout
- Password and credential protection
- Passkeys and passwordless authentication
- Multi-factor authentication
- Step-up authentication
- Authentication tokens and user sessions
- Trusted-device management
- Account recovery
- Brute-force and credential-stuffing protection
- Account-takeover detection and containment
- User, workspace and operator authorization
- Customer-facing account-security interfaces
- Owner and Support security operations

## Reserved Implementation Locations

- Architecture and policies: `backend/infra/security/architecture`
- Runtime identity services: `backend/server/identity_access`
- Customer authentication UI: frontend authentication area
- Customer Security Centre: frontend account-security area
- Owner security operations: `backend/server/owner` and Owner Console frontend

The runtime and frontend locations are reserved boundaries. Their implementation will occur in the applicable later phases.

## Explicit Non-Ownership

This domain does not replace or assume ownership of:

- AWS IAM identities, roles or service policies
- Runtime job identity
- Article, document or workspace-content identity
- Crawler execution sessions
- TMS workflow roles
- Billing entitlement calculations
- General-purpose UDA storage

Necessary connections to those systems must be made through defined contracts without transferring credential ownership.

## Foundational Rule

No LinkCraftor component may independently create a competing customer authentication, credential-storage, session-management, or account-recovery authority outside this domain.

## Phase 1 Status

Item 1.1 establishes the dedicated architectural domain. Responsibilities, authority separation, trust boundaries, assurance levels, governance and integration rules will be added through the remaining Phase 1 items.

## Domain Responsibilities

### 1. Identity Lifecycle

The domain owns the security-controlled lifecycle of every LinkCraftor customer and operator identity, including:

- Identity creation
- Verification
- Activation
- Restriction
- Suspension
- Restoration
- Closure
- Deletion
- Security-state transitions

Editable profile information may be stored through other governed services, but those services cannot create, activate, authenticate, suspend, restore, or delete the canonical security identity independently.

### 2. Signup and Verification

The domain owns:

- Signup eligibility decisions
- Email and approved identity-channel verification
- Duplicate-identity prevention
- Signup-abuse prevention
- Verification-token issuance and validation
- Pending-account expiration
- Account activation following successful verification

### 3. Authentication

The domain owns:

- Login and logout decisions
- Password authentication
- Passkey authentication
- Passwordless authentication
- Approved federated authentication
- Multi-factor authentication
- Step-up authentication
- Authentication assurance evaluation
- Authentication success and failure evidence

No application route, plugin, API, workspace, or internal console may independently authenticate a customer or operator.

### 4. Credential Protection

The domain owns security requirements for:

- Password hashing
- Passkey public-key credentials
- MFA secrets
- Recovery codes
- Verification tokens
- Password-reset tokens
- Session credentials
- OAuth credentials
- Authentication signing keys
- Credential rotation and revocation

The domain must prevent raw passwords, MFA secrets, recovery codes, and reusable authentication tokens from entering logs, analytics, general datasets, or unapproved services.

### 5. Sessions and Trusted Devices

The domain owns:

- Authenticated-session creation
- Session expiration
- Session renewal
- Session revocation
- Refresh-token rotation
- Refresh-token reuse detection
- Trusted-device registration
- Device removal
- Logout from one or all devices
- Compromised-session containment

Crawler sessions, runtime execution sessions, and document-processing sessions remain outside this responsibility.

### 6. Account Recovery

The domain owns:

- Forgotten-password recovery
- Lost-passkey recovery
- Lost-MFA recovery
- Recovery-code verification
- Recovery risk assessment
- Support-assisted recovery controls
- Post-recovery restrictions
- Recovery notifications
- Recovery evidence and audit trails

Recovery must never provide a weaker uncontrolled route around normal authentication protections.

### 7. Authentication-Abuse Protection

The domain owns authentication-specific protection against:

- Brute-force attacks
- Credential stuffing
- Password spraying
- Account enumeration
- Automated signup abuse
- Verification-code abuse
- MFA-code guessing
- Recovery-endpoint abuse
- Session-token replay
- Malicious account lockout attempts

General network firewalls and infrastructure-level denial-of-service protection remain responsibilities of the wider Security and Cloud Infrastructure architectures.

### 8. Account-Takeover Protection

The domain owns:

- Authentication-risk evaluation
- Suspicious-login detection
- Unfamiliar-device detection
- Credential-compromise response
- High-risk account-change detection
- Risk-based authentication challenges
- Session restriction and revocation
- Temporary account containment
- Legitimate-user security notifications
- Account-takeover investigation evidence

### 9. Authorization and Tenant Protection

The domain owns:

- Identity-to-role assignment
- Role-to-permission evaluation
- Workspace membership authorization
- Privileged-action authorization
- Least-privilege enforcement
- Tenant-boundary enforcement
- Ownership-transfer protection
- Immediate access revocation
- Authorization decision evidence

Billing may supply plan and entitlement facts, but billing cannot authenticate identities or override security permissions.

### 10. Customer Security Experience

The domain owns the security behaviour and requirements of:

- Signup interfaces
- Login interfaces
- Passkey interfaces
- MFA interfaces
- Account-recovery interfaces
- Reauthentication interfaces
- Session and device management
- Customer Security Centre
- Security warnings and notifications
- Account closure and deletion interfaces

Frontend applications display and submit security operations but cannot make final authentication or authorization decisions.

### 11. Owner and Support Security Operations

The domain owns security requirements for:

- Identity-security dashboards
- Suspicious-account investigations
- Session revocation
- Account restriction
- Controlled account unlocking
- Support-assisted recovery
- Privileged operator authentication
- Separation of duties
- High-risk action approval
- Administrative audit evidence

No employee, engineer, owner-console operator, or support operator may view a user's password, MFA secret, recovery code, passkey private key, or reusable authentication token.

### 12. Security Events, Evidence and Notifications

The domain owns the production of authoritative events for:

- Signup
- Verification
- Login
- Logout
- Authentication failure
- MFA and passkey changes
- Password and recovery changes
- Session creation and revocation
- Permission changes
- Account restrictions
- Account-takeover responses
- Administrative identity actions

The Observability Architecture may collect and analyze these events but cannot alter their security meaning or authentication outcome.

### 13. Contract and Policy Governance

The domain owns its:

- Identity contracts
- Authentication contracts
- Authorization contracts
- Credential-handling policies
- Recovery policies
- Risk-decision policies
- Security-event definitions
- Frontend security requirements
- Service integration requirements
- Versioned architecture decisions

Changes affecting these responsibilities must follow the Architecture Registry and security change-approval process.

## Responsibility Enforcement Rule

A LinkCraftor component may consume identity decisions, authorization decisions, security events, or identity references through an approved contract. It may not silently duplicate, bypass, weaken, or replace the authority assigned to this domain.

## Customer Identity and AWS IAM Boundary

### Two Independent Identity Planes

LinkCraftor must maintain two separate identity planes with different authorities, credentials, sessions, permissions, and audit evidence.

| Identity plane | Identities governed | Principal purpose |
|---|---|---|
| LinkCraftor Identity Plane | Customers, workspace owners, administrators, members, plugin users, API clients, support operators and Owner Console operators | Access to LinkCraftor products, accounts, workspaces and product capabilities |
| AWS IAM Plane | AWS workloads, service roles, deployment systems, automation roles, engineers and approved infrastructure administrators | Access to AWS infrastructure, cloud services and deployment resources |

Neither identity plane may silently replace, impersonate, or inherit the authority of the other.

### LinkCraftor Identity Plane Responsibilities

The LinkCraftor Identity Plane governs:

- Customer signup and verification
- Customer login and logout
- Passwords, passkeys and MFA
- Customer sessions and trusted devices
- Workspace roles and permissions
- Product and plugin authorization
- Customer API-client identities
- Account recovery
- Account-takeover detection
- Support and Owner Console product access
- Product-level security evidence

A LinkCraftor user identity is not an AWS IAM user, role, group, policy, access key, or cloud-service principal.

### AWS IAM Plane Responsibilities

The AWS IAM Plane governs:

- AWS Console access
- Infrastructure administrator access
- Deployment and CI/CD roles
- Application workload roles
- Service-to-service AWS permissions
- Lambda, container, worker and scheduled-task roles
- Access to AWS databases, queues, storage, networking and key-management services
- Temporary workload credentials
- Infrastructure-level least privilege
- AWS control-plane audit evidence

AWS IAM does not perform LinkCraftor customer signup, login, account recovery, workspace membership, plan authorization, or customer-session management.

### Mandatory Separation Rules

1. Customer passwords, passkeys, MFA secrets and recovery credentials must never become AWS IAM credentials.

2. AWS access keys, workload credentials and infrastructure roles must never be accepted as customer login credentials.

3. A customer authentication token must not directly grant general AWS permissions.

4. A backend service must access AWS resources through its assigned workload role, not through the customer's credentials.

5. AWS IAM permissions must not be treated as LinkCraftor workspace permissions.

6. LinkCraftor workspace roles must not be translated into AWS Console or infrastructure access.

7. The same person acting as a LinkCraftor customer and as an authorized LinkCraftor employee must use separately governed identities, sessions, permissions and audit trails.

8. Production AWS administration must require workforce authentication that is independent of customer authentication.

9. Compromise of a customer account must not provide AWS administrative access.

10. Compromise of one workload role must not automatically provide access to every LinkCraftor account or workspace.

### Canonical Request Boundary

The normal protected request path is:

1. The user authenticates through the LinkCraftor Identity Service.
2. The Identity Service issues an approved LinkCraftor session or authentication token.
3. The LinkCraftor API verifies the token and resolves the internal identity.
4. The Authorization Service evaluates workspace and action permissions.
5. The backend workload performs the approved operation.
6. The backend workload accesses AWS through its own restricted AWS IAM role.
7. Security evidence records the customer identity, authorization result and acting workload separately.

The customer never receives the backend workload's AWS IAM credentials.

### Controlled Direct-Transfer Exception

When a browser or plugin must transfer an approved object directly to an AWS service, LinkCraftor may issue a narrowly scoped, short-lived presigned operation or brokered capability.

Such a capability must:

- Permit only the required operation
- Identify the permitted object or resource
- Expire quickly
- Prevent resource enumeration
- Prevent access to unrelated tenants
- Avoid exposing reusable AWS access keys
- Be recorded in security evidence
- Be revocable or containable where technically possible

This exception does not convert the customer into an AWS IAM user.

### Plugin and External Provider Boundary

WordPress, Shopify and approved external identity providers maintain their own credentials and sessions.

LinkCraftor must:

- Use approved OAuth or connection contracts
- Store only necessary protected connection credentials
- Map the external account to an immutable LinkCraftor identity
- Keep external-provider permissions separate from workspace authorization
- Revoke the LinkCraftor connection without requiring deletion of the external account
- Prevent an external plugin session from becoming an AWS infrastructure session

### Owner and Workforce Boundary

An Owner Console operator may hold:

- A workforce identity for infrastructure administration
- A LinkCraftor operator identity for Owner Console actions
- A normal customer identity for product use

These identities must remain logically separated. High-risk actions must record which identity plane was used, which role authorized the action, and which workload executed it.

### Failure and Recovery Boundary

If customer authentication is unavailable:

- LinkCraftor must not fall back to AWS IAM as customer login.
- New customer authentication must fail safely.
- Existing sessions may continue only according to their established validity and revocation policy.

If AWS IAM authorization or workload credentials are unavailable:

- Backend access to the affected AWS resource must fail safely.
- LinkCraftor must not request or use customer credentials as a substitute.
- The failure must be recorded and routed through operational monitoring.

### Boundary Enforcement Rule

All LinkCraftor implementations must preserve the distinction between product identity and cloud-resource identity:

`Customer identity proves who is using LinkCraftor; AWS IAM proves which trusted workload or workforce principal may access AWS resources.`

Cross-plane activity is permitted only through an explicit, least-privilege, auditable contract.

## Authentication and Authorization Separation

### Separate Security Questions

Authentication and authorization are separate security decisions:

| Decision | Security question | Authoritative output |
|---|---|---|
| Authentication | Who is presenting this request, and how strongly has the identity been verified? | Authenticated identity and assurance context |
| Authorization | May that authenticated identity perform the requested action on the specified resource within the specified tenant? | Allow, deny, or step-up-required decision |

Successful authentication does not automatically grant access to any workspace, document, API, plugin connection, administrative operation, or other protected resource.

### Authentication Responsibilities

Authentication is responsible for:

- Verifying passwords, passkeys and approved identity-provider assertions
- Verifying MFA and step-up challenges
- Establishing the immutable internal identity
- Establishing authentication time
- Establishing authentication methods used
- Establishing identity-assurance level
- Evaluating authentication-specific risk
- Creating and validating authenticated sessions
- Issuing approved authentication tokens
- Revoking compromised authentication credentials and sessions
- Producing authentication evidence

Authentication does not decide whether an authenticated identity may read, create, update, delete, publish, export, administer, bill, invite, transfer, or otherwise operate on a LinkCraftor resource.

### Authorization Responsibilities

Authorization is responsible for:

- Resolving the authenticated identity's applicable roles
- Resolving workspace or tenant membership
- Evaluating requested actions
- Evaluating protected-resource ownership
- Evaluating plan or entitlement facts where relevant
- Enforcing least privilege
- Enforcing tenant isolation
- Applying security-policy conditions
- Requiring stronger assurance for sensitive actions
- Returning allow, deny, or step-up-required decisions
- Producing authorization evidence

Authorization must not verify passwords, passkeys, MFA codes, recovery codes, or other primary credentials.

### Mandatory Decision Sequence

Every protected LinkCraftor request must follow this sequence:

1. Receive the request.
2. Validate the authentication credential or session.
3. Resolve the immutable LinkCraftor identity.
4. Establish authentication assurance and security context.
5. Reject the request if authentication fails.
6. Submit an authorization request for the specific action and resource.
7. Evaluate tenant, role, permission, entitlement and policy conditions.
8. Require step-up authentication if the current assurance is insufficient.
9. Deny the request if authorization fails.
10. Execute the operation only after an explicit authorization decision.
11. Record authentication, authorization and execution evidence separately.

No protected operation may execute between authentication and authorization.

### Authentication Result Contract

A successful authentication result must provide only the approved security context required by downstream authorization, including:

- Immutable subject identifier
- Session identifier
- Authentication time
- Authentication methods used
- Identity-assurance level
- Token issuer and audience
- Token issuance and expiration times
- Authentication risk state
- Credential or session status
- Correlation identifier

Passwords, passkey private keys, MFA secrets, recovery codes and raw reusable credentials must never be included in the authentication result.

### Authorization Request Contract

An authorization request must identify:

- Immutable subject identifier
- Session or authenticated-request identifier
- Workspace or tenant identifier
- Requested resource type
- Requested resource identifier
- Requested action
- Current identity-assurance level
- Applicable authentication risk state
- Relevant role and membership references
- Relevant entitlement references
- Request correlation identifier
- Approved contextual conditions

Information supplied by the browser, plugin or API client must not be trusted as proof of its own roles, permissions, ownership or entitlements.

### Authorization Decision Contract

Every authorization evaluation must return:

- Decision: `ALLOW`, `DENY`, or `STEP_UP_REQUIRED`
- Decision identifier
- Subject identifier
- Tenant identifier
- Resource and action evaluated
- Policy version
- Decision reason code
- Required security obligations
- Required assurance level when step-up is necessary
- Decision timestamp
- Correlation identifier

An absent, malformed, expired, unavailable or unverifiable authorization decision must be treated as `DENY`.

### Step-Up Boundary

The Authorization Service may determine that stronger authentication is required, but it must not perform the authentication itself.

The required flow is:

1. Authorization returns `STEP_UP_REQUIRED`.
2. The Identity Service performs the approved stronger challenge.
3. The Identity Service issues updated authentication assurance.
4. The original action is submitted for a new authorization decision.
5. The operation proceeds only if the new decision is `ALLOW`.

Completion of step-up authentication does not bypass authorization.

### Role and Entitlement Boundary

Roles, permissions and product entitlements must not be used as proof of identity.

The following separation applies:

- Identity Service establishes who the subject is.
- Authorization Service establishes what the subject may do.
- Workspace membership supplies tenant relationship facts.
- Billing supplies plan and entitlement facts.
- Security policy supplies required restrictions and obligations.
- The executing service performs only the explicitly authorized operation.

Billing cannot authenticate a customer, and an active subscription cannot override a security denial.

### Token and Permission Boundary

Authentication tokens may carry signed identity and assurance context. They must not become an uncontrolled permanent source of mutable permissions.

LinkCraftor must:

- Use appropriately short token lifetimes
- Validate issuer, audience, signature and expiration
- Support session and token revocation
- Re-evaluate sensitive or mutable permissions
- Invalidate affected authorization state after role or membership changes
- Prevent stale permissions from surviving removal or suspension
- Avoid placing secrets or excessive personal data in tokens

### Frontend Enforcement Boundary

The frontend may:

- Hide unavailable actions
- Display permission information
- Request authentication
- Request step-up authentication
- Submit protected operations
- Display authorization failures

The frontend cannot provide final security enforcement. Every protected backend operation must perform its own authentication and authorization enforcement.

### Service Enforcement Boundary

Every protected backend route, worker command, plugin operation and administrative operation must:

- Accept only verified authentication context
- Request or enforce the applicable authorization decision
- Confirm tenant and resource scope
- Reject missing authorization
- Reject mismatched identity or tenant context
- Record the decision identifier with execution evidence

Internal network location alone must never count as authorization.

### Caching Boundary

Authorization decisions may be cached only when:

- The decision is narrowly scoped
- The subject, tenant, resource and action are included in the cache key
- The policy version is recorded
- The cache lifetime is limited
- Revocation and membership changes can invalidate the decision
- Sensitive actions require current evaluation

A cached authentication result or authorization decision must never outlive the credential, session, membership or policy on which it depends.

### Failure Behaviour

If authentication is unavailable or unverifiable, the request must fail as unauthenticated.

If authorization is unavailable, missing or unverifiable, the protected request must fail as unauthorized.

LinkCraftor must never:

- Treat authentication success as authorization success
- Treat authorization data as authentication proof
- Default to allow during service failure
- Reuse one tenant's authorization decision for another tenant
- Permit the frontend to override a backend denial
- Execute first and authorize afterward

### Separation Enforcement Rule

`Authentication establishes the verified identity and assurance context. Authorization independently decides whether that identity may perform one specific action on one specific protected resource.`

Both decisions are mandatory, separately auditable, and fail secure.

## Identity Service Authentication Authority

### Authority Declaration

The LinkCraftor Identity Service is the sole product-level authority for establishing, validating, challenging, restricting and terminating authenticated LinkCraftor identities.

No frontend, API route, plugin, worker, workspace service, support tool or Owner Console component may independently declare that a customer or operator is authenticated.

### Managed Identity Provider Boundary

An approved managed identity provider may perform standards-based credential operations, including:

- Password verification
- Passkey registration and verification
- MFA verification
- Federated identity verification
- Standards-compliant token issuance
- Provider-managed credential protection

The LinkCraftor Identity Service remains responsible for:

- Enforcing LinkCraftor authentication policies
- Mapping provider subjects to immutable LinkCraftor identities
- Evaluating account status
- Applying LinkCraftor risk and restriction decisions
- Establishing authentication-assurance context
- Establishing or recognizing approved sessions
- Revoking LinkCraftor access
- Producing authoritative authentication evidence

A provider assertion alone cannot bypass LinkCraftor security controls.

### Canonical Operations

The Identity Service owns the contracts for:

- Beginning and verifying signup
- Beginning and completing login
- Beginning and completing MFA
- Beginning and completing step-up authentication
- Registering and removing passkeys
- Establishing and validating sessions
- Refreshing and revoking sessions
- Logging out one or all sessions
- Restricting and suspending authentication
- Beginning and completing account recovery

### Permitted Authentication Outcomes

The Identity Service may return:

- `AUTHENTICATED`
- `CHALLENGE_REQUIRED`
- `STEP_UP_REQUIRED`
- `RECOVERY_REQUIRED`
- `DENIED`
- `TEMPORARILY_RESTRICTED`
- `SECURITY_SUSPENDED`

Unknown, incomplete, expired or unverifiable outcomes must be treated as `DENIED`.

### Authentication Result

An authoritative authentication result must include:

- Result identifier
- Outcome
- Immutable subject identifier where safely established
- Session identifier where applicable
- Authentication time
- Authentication methods
- Authentication-assurance level
- Risk state
- Account security status
- Issuer and audience where applicable
- Expiration
- Safe reason code
- Correlation identifier
- Evidence reference

It must never include raw passwords, MFA secrets, recovery codes, passkey private keys or reusable credentials.

### Synchronous Decision Boundary

Credential validation, account-status checks, mandatory risk checks and the authentication outcome belong to the synchronous authentication path.

The Universal Runtime and Coordinator may handle asynchronous notifications, supplementary evidence, incident escalation and cleanup, but they cannot grant access before authentication succeeds.

### Revocation Authority

The Identity Service is authoritative for:

- Session revocation
- Token-family revocation
- Trusted-device revocation
- Authentication restrictions
- Security suspension
- MFA and passkey status
- Post-recovery containment
- Global logout

All protected services must honor current revocation state.

### Failure Rule

If the Identity Service or a mandatory authentication dependency is unavailable:

- New authentication fails safely
- Unverified sessions cannot be created
- No temporary bypass may be introduced
- Existing sessions continue only according to established validity and revocation rules
- The failure must be recorded and monitored

### Identity Authority Enforcement Rule

`An identity becomes authenticated for LinkCraftor only through an approved Identity Service decision and remains authenticated only while its session, assurance, account status and revocation state remain valid.`

## Authorization Service Permissions Authority

### Authority Declaration

The LinkCraftor Authorization Service is the sole product-level authority for deciding whether an authenticated identity may perform a specific action on a specific protected resource within a specific tenant.

Authentication success does not create authorization.

### Authorization Inputs

An authorization evaluation may consume only approved facts, including:

- Immutable subject identifier
- Valid authentication context
- Authentication-assurance level
- Authentication risk state
- Workspace or tenant identifier
- Role assignments
- Membership state
- Resource ownership
- Requested action
- Billing-provided entitlement facts
- Security restrictions
- Policy version
- Approved contextual conditions

Browser, plugin or API-client claims about their own roles, permissions, ownership or entitlements must not be trusted without server-side verification.

### Canonical Decisions

The Authorization Service may return:

- `ALLOW`
- `DENY`
- `STEP_UP_REQUIRED`

Every decision must contain:

- Decision identifier
- Subject identifier
- Tenant identifier
- Resource and action
- Policy version
- Reason code
- Obligations
- Required assurance where applicable
- Decision timestamp
- Correlation identifier
- Evidence reference

Missing, expired, malformed or unverifiable decisions are treated as `DENY`.

### Permissions Authority Responsibilities

The Authorization Service owns:

- Role-to-permission evaluation
- Workspace-membership authorization
- Tenant-isolation enforcement
- Resource-ownership evaluation
- Privileged-action evaluation
- Entitlement-aware access decisions
- Security-restriction enforcement
- Step-up requirements
- Immediate permission-revocation handling
- Authorization evidence

### Enforcement Points

Authorization must be enforced by:

- Protected API routes
- Backend services
- Worker commands
- Plugin operations
- Administrative operations
- Owner Console operations
- Support operations
- Resource export and publishing operations

The frontend may display permission-aware controls but cannot provide final enforcement.

### Step-Up Boundary

The Authorization Service may return `STEP_UP_REQUIRED`, but only the Identity Service may conduct the stronger authentication.

After successful step-up, the original action must receive a new authorization decision.

### Billing Boundary

Billing may provide plan and entitlement facts. It cannot:

- Authenticate an identity
- Assign security roles
- Override tenant isolation
- Override account suspension
- Override an authorization denial

### Permission Change Rule

Role removal, membership removal, ownership transfer, suspension and security restrictions must invalidate affected authorization state without waiting for a long-lived session to expire.

### Availability Rule

If the Authorization Service or mandatory policy data is unavailable, protected actions must fail closed.

### Authorization Authority Enforcement Rule

`No protected LinkCraftor operation may execute without an explicit, current and resource-scoped authorization decision.`

## Supported Identity Types

### Identity-Type Principle

Identity type describes the nature of the principal. Role describes what that principal may do.

One identity may hold different approved roles in different workspaces. Role changes must not create a new canonical identity unless a formally separated operator identity is required.

### Human Customer Identity

Identifier: `HUMAN_CUSTOMER`

Represents an individual using LinkCraftor through the web application or another approved customer interface.

It may hold roles such as:

- Workspace owner
- Workspace administrator
- Workspace member
- Restricted workspace member
- Billing administrator

### Enterprise Federated Identity

Identifier: `ENTERPRISE_FEDERATED_USER`

Represents a human whose authentication originates from an approved enterprise identity provider.

It must map to one immutable LinkCraftor identity and remains subject to LinkCraftor account, tenant, risk and authorization policies.

### Support Operator Identity

Identifier: `SUPPORT_OPERATOR`

Represents authorized support personnel performing controlled support operations.

It requires:

- Separate operator authentication
- Strong MFA
- Least privilege
- Restricted support scopes
- Reason codes
- Complete audit evidence

It cannot be used to impersonate a customer or manufacture a customer session.

### Owner Console Operator Identity

Identifier: `OWNER_CONSOLE_OPERATOR`

Represents an authorized person accessing the LinkCraftor Owner Control Console.

It must remain logically separated from normal customer activity and AWS workforce administration.

### Customer API Client Identity

Identifier: `CUSTOMER_API_CLIENT`

Represents a non-human client authorized by a LinkCraftor customer or workspace.

It requires:

- An immutable client identifier
- Explicit scopes
- Tenant binding
- Credential rotation
- Revocation
- Rate and abuse controls
- Separate evidence from human sessions

An API client is not automatically a workspace owner or administrator.

### Plugin Connection Identity

Identifier: `PLUGIN_CONNECTION`

Represents an approved WordPress, Shopify or future platform connection.

It must be bound to:

- A LinkCraftor identity
- A workspace
- An external site or installation
- Explicit connection scopes
- Protected connection credentials
- Revocation state

A plugin connection does not inherit all permissions of the person who installed it.

### Internal Service Identity Reference

Identifier: `INTERNAL_SERVICE_REFERENCE`

Represents the product-level reference to an approved backend service or workload.

AWS IAM remains authoritative for the workload's AWS permissions. LinkCraftor service authorization remains responsible for the product operation it is allowed to request.

### Anonymous Principal

Identifier: `ANONYMOUS`

Represents an unauthenticated visitor.

Anonymous access is limited to explicitly public resources and cannot inherit customer, workspace, plugin, API or administrative permissions.

### Identity Separation Rules

- Human and machine identities must not share reusable credentials.
- Customer and operator identities must have separate security contexts.
- API clients and plugin connections must have narrower scopes than their authorizing human where possible.
- Anonymous activity must never be upgraded to authenticated activity without successful authentication.
- Deleted or suspended identities cannot be recreated silently through another provider.
- Identity linking requires explicit verified evidence.
- Every identity type must have an owner, lifecycle, credential policy and revocation mechanism.

## Identity Security Trust Boundaries

### Trust Principle

No request, identity claim, session, token, device, network location or internal service is trusted solely because of where it originated.

Every trust-boundary crossing requires validation appropriate to the identity, data, action and risk.

### Boundary 1 — Public Client to LinkCraftor Edge

Includes browsers, mobile browsers and public clients.

Required controls include:

- TLS
- Input validation
- Origin and redirect validation
- CSRF protection where applicable
- Bot and rate controls
- Secure cookie handling
- No trust in client-provided roles or tenant identifiers

### Boundary 2 — Plugin or External Platform to LinkCraftor

Includes WordPress, Shopify and future integrations.

Required controls include:

- Approved OAuth or connection protocol
- State and nonce validation
- Explicit scopes
- Site and tenant binding
- Credential rotation and revocation
- Replay protection
- Signed or otherwise authenticated requests

### Boundary 3 — API Gateway to Identity and Authorization Services

Required controls include:

- Token validation
- Issuer and audience validation
- Request correlation
- Trusted service identity
- Restricted network access
- Fail-secure behaviour
- Prevention of header or identity-context spoofing

### Boundary 4 — Managed Identity Provider to Identity Service

Required controls include:

- Approved issuer
- Signature validation
- Audience validation
- Nonce and state validation where applicable
- Provider-subject mapping
- Account-status validation
- Prevention of unsafe automatic account linking

### Boundary 5 — Identity Service to Credential and Session Stores

Required controls include:

- Encryption in transit and at rest
- Restricted service access
- Field-level protection where required
- No general-purpose data access
- Credential-safe logging
- Rotation and revocation support
- Complete security evidence

### Boundary 6 — Authorization Service to Tenant Resources

Required controls include:

- Immutable subject resolution
- Verified tenant context
- Resource ownership validation
- Role and permission evaluation
- Prevention of cross-tenant identifiers
- Explicit allow decisions
- Default denial

### Boundary 7 — Customer Plane to Owner and Support Plane

Required controls include:

- Separate operator identities
- Strong authentication
- Step-up authentication
- Least privilege
- Reason codes
- Separation of duties
- No customer impersonation
- Complete administrative audit evidence

### Boundary 8 — Synchronous Security Path to Runtime and Coordinator

Runtime and coordination systems may process approved asynchronous identity events.

They cannot:

- Declare authentication success
- Override authorization
- Manufacture sessions
- Recover accounts without the Identity Service
- Weaken security restrictions

Events crossing this boundary must exclude raw credentials and reusable authentication secrets.

### Boundary 9 — LinkCraftor Identity Plane to AWS IAM Plane

Customer identity proves who is using LinkCraftor. AWS IAM proves which workforce or workload principal may access AWS resources.

Crossing this boundary requires an explicit least-privilege workload contract. Customer credentials must never become AWS credentials.

### Boundary 10 — Tenant to Tenant

Every workspace is an independent tenant-security boundary.

All tenant-scoped access must validate:

- Subject
- Membership
- Role
- Workspace identifier
- Resource ownership
- Requested action
- Current restrictions

Possession of another tenant's resource identifier does not grant access.

### Trust-Boundary Enforcement Rule

`Every boundary crossing is authenticated, authorized, scoped, validated, auditable and fail secure. Internal location alone creates no trust.`

## Identity Assurance Levels

### Assurance Principle

Authentication assurance describes the confidence that the current actor controls the registered authentication method for the claimed LinkCraftor identity.

Authentication assurance is separate from real-world identity proofing and separate from authorization.

### AAL0 — Unauthenticated

Identifier: `AAL0`

The actor has not established an authenticated LinkCraftor identity.

Permitted only for explicitly public resources and initial authentication or recovery requests.

### AAL1 — Baseline Authenticated

Identifier: `AAL1`

Established through one approved authentication factor, such as:

- Password authentication
- Approved federated single-factor authentication
- A passkey flow that does not satisfy the stronger LinkCraftor assurance requirements

Suitable for routine customer actions when:

- The organization does not require stronger authentication
- Risk is acceptable
- No sensitive security or administrative change is requested

### AAL2 — Strong Authenticated

Identifier: `AAL2`

Established through an approved strong method, such as:

- Password plus authenticator-app MFA
- A user-verifying passkey
- Approved enterprise authentication satisfying LinkCraftor's strong-authentication policy

Required for elevated customer, workspace, billing, security and administrative actions as defined by policy.

### AAL3 — High-Assurance Privileged

Identifier: `AAL3`

Reserved for highly sensitive Owner Console, workforce or exceptional security operations.

It may require:

- Phishing-resistant hardware-backed authentication
- A recently verified strong factor
- Restricted operator identity
- Approved device or workforce condition
- Additional authorization or dual approval
- Enhanced evidence

AAL3 is not automatically granted merely because an identity is a workspace owner.

### Separate Verification State

LinkCraftor must record identity verification separately from authentication assurance.

Approved verification states include:

- `UNVERIFIED`
- `CONTACT_VERIFIED`
- `ENTERPRISE_ASSERTED`
- `ADMINISTRATIVELY_VERIFIED`

Email verification alone must not be represented as proof of a person's legal or real-world identity.

### Assurance Context

The authentication result must record:

- Current assurance level
- Authentication methods used
- Authentication time
- Step-up time where applicable
- Credential status
- Session identifier
- Risk state
- Issuer
- Evidence reference

### Assurance Rules

- Assurance cannot be supplied by the frontend.
- Assurance cannot be increased without successful approved authentication.
- Authorization may demand a higher assurance level.
- Elevated assurance expires according to its own shorter validity period.
- Recovery may temporarily reduce permitted assurance or restrict sensitive actions.
- Elevated risk may require stronger authentication regardless of the current level.
- A compromised, revoked or expired credential cannot maintain its previous assurance.
- Assurance must not survive session revocation.
- Services must reject unknown assurance levels.
- Failure to verify assurance must result in denial.

### Assurance Enforcement Rule

`LinkCraftor grants only the assurance level supported by the authentication methods, credential state, recency, risk and policy verified for the current session.`

## Normal Authentication Actions

### Normal Authentication Definition

Normal authentication means that a valid LinkCraftor session with the required baseline assurance may be used without asking the user to repeat or strengthen authentication for every routine operation.

Normal authentication never removes the requirement for authorization.

### Baseline Requirement

The normal customer baseline is:

- A valid authenticated session
- At least `AAL1`
- A verified account where required
- An active and unrestricted identity
- Acceptable authentication risk
- Current tenant membership
- Explicit authorization for the requested action

An organization may require `AAL2` as its normal baseline through an approved mandatory MFA policy.

### Routine Account Actions

Normal authentication may be sufficient for:

- Viewing the normal account profile
- Updating non-security profile preferences
- Viewing notification preferences
- Viewing existing security status without revealing protected secrets
- Viewing normal product activity
- Requesting stronger authentication for a sensitive action

Changing passwords, recovery methods, MFA, passkeys or primary identity channels is excluded and will be governed by step-up policy.

### Routine Workspace Actions

Subject to authorization, normal authentication may be sufficient for:

- Opening an authorized workspace
- Viewing workspace dashboards
- Viewing authorized workspace members
- Viewing ordinary workspace settings
- Switching between authorized workspaces
- Viewing plan and usage information
- Performing routine non-privileged workspace operations

Ownership transfer, privileged-role changes and security-policy changes are excluded.

### Routine Content and Linking Actions

Subject to authorization, normal authentication may be sufficient for:

- Viewing authorized documents
- Uploading routine documents
- Creating and editing drafts
- Running approved linking operations
- Reviewing link suggestions
- Accepting or rejecting suggestions
- Applying approved links
- Viewing link reports
- Downloading an ordinary authorized document
- Viewing connected-site content within granted scope

Unusually large exports, destructive operations and elevated publishing actions may require stronger authentication according to risk and step-up policy.

### Routine Plugin Actions

Subject to the connection's scopes, normal authentication may be sufficient for:

- Viewing plugin connection status
- Viewing authorized site content
- Running ordinary approved LinkCraftor operations
- Reviewing suggestions
- Synchronizing content within existing authorization
- Viewing routine plugin activity

Creating, transferring, expanding or revoking sensitive plugin authority may require step-up authentication.

### Routine API-Client Actions

A customer API client may perform routine operations only when:

- Its credential is valid
- Its scopes authorize the action
- Its workspace binding is valid
- The requested resource belongs to the permitted tenant
- Rate and abuse controls permit the request
- No security restriction is active

Human session assurance must not be silently reused as permanent API-client authority.

### Conditions That Terminate Normal Treatment

A routine action must be interrupted, denied or escalated when:

- The session is expired or revoked
- The account is restricted or suspended
- The device or location presents elevated risk
- Tenant membership has changed
- The role or entitlement is insufficient
- The resource belongs to another tenant
- The operation becomes sensitive or unusually large
- Recent stronger authentication is required
- Account-takeover indicators are present
- Security policy explicitly requires step-up

### Normal Authentication Enforcement Rule

`Routine use may continue under a valid baseline session only while identity, assurance, risk, membership, authorization and resource scope remain valid.`

## Step-Up Authentication Actions

### Step-Up Definition

Step-up authentication requires an already authenticated identity to provide stronger or more recent evidence before a sensitive action can continue.

Step-up does not replace authorization. The original action must receive a new authorization decision after successful step-up.

### Mandatory Step-Up Triggers

Step-up is required when:

- The current assurance level is insufficient
- Strong authentication is no longer recent enough
- Device, location, network or behaviour creates elevated risk
- Account-takeover indicators are detected
- The session follows account recovery
- The organization requires stronger authentication
- The action affects credentials, ownership, privileged access or security policy

### Credential and Account-Security Actions

Step-up is required before:

- Changing the password
- Adding or removing a passkey
- Adding, replacing or disabling MFA
- Regenerating recovery codes
- Changing recovery methods
- Changing the primary email or login identifier
- Linking or unlinking an identity provider
- Removing the final strong authentication method
- Closing or deleting the account

A new credential cannot authorize its own addition.

### Sessions and Devices

Step-up is required before:

- Revoking all other sessions
- Approving a high-risk device
- Restoring a restricted session
- Reversing takeover containment
- Changing trusted-device security policy
- Continuing sensitive activity after token-reuse detection

### Workspace and Privileged Actions

Step-up is required before:

- Transferring workspace ownership
- Adding or removing an owner
- Granting privileged administrator access
- Changing protected role assignments
- Disabling mandatory MFA
- Configuring or disabling enterprise SSO
- Changing domain-verification ownership
- Changing workspace security policies
- Performing unusually broad membership changes

### API and Integration Actions

Step-up is required before:

- Creating or revealing an API credential
- Rotating or revoking sensitive API credentials
- Expanding API scopes
- Connecting a privileged WordPress or Shopify installation
- Expanding plugin scopes
- Transferring a plugin connection
- Changing webhook authentication secrets
- Authorizing a high-privilege external integration

Existing secrets must not be redisplayed after step-up.

### Sensitive Data and Destructive Actions

Policy may require step-up before:

- Large workspace exports
- Exporting security evidence
- Bulk deletion
- Permanent workspace deletion
- High-impact bulk publishing
- Destructive operations affecting multiple connected sites

### Owner and Support Actions

Strong step-up is required before:

- Unlocking a security-restricted account
- Initiating exceptional recovery
- Revoking all customer sessions
- Changing customer security status
- Reversing takeover containment
- Approving protected identity linking
- Changing identity-security policies
- Activating emergency controls
- Viewing restricted investigation evidence

Critical operator operations may require `AAL3`, separation of duties and dual approval.

### Approved Assurance Targets

| Target | Minimum expectation |
|---|---|
| `AAL1_RECENT` | Recently repeated approved baseline authentication |
| `AAL2` | User-verifying passkey or approved multi-factor authentication |
| `AAL3` | Phishing-resistant privileged authentication plus required operator controls |

Password re-entry alone cannot satisfy `AAL2` or `AAL3`.

Email confirmation alone cannot satisfy strong step-up for high-risk actions.

### Context Binding

Successful step-up must be bound to:

- Immutable subject
- Current session
- Required assurance
- Authentication methods
- Completion and expiration times
- Risk state
- Tenant where applicable
- Protected action and resource where required
- Correlation identifier
- Evidence reference

It must not be replayed across identities, sessions, tenants, devices or critical actions.

### Canonical Flow

1. The authenticated identity requests a protected action.
2. Authorization returns `STEP_UP_REQUIRED`.
3. The Identity Service performs the stronger challenge.
4. Updated assurance context is established.
5. The original action is resubmitted.
6. Authorization evaluates the action again.
7. Execution occurs only after `ALLOW`.
8. All evidence is correlated.

### Failure Rule

Failed, expired, abandoned, mismatched or insufficient step-up must prevent the protected action from executing.

### Enforcement Rule

`Sensitive actions require authentication that is sufficiently strong, sufficiently recent and bound to the correct identity, session, tenant, resource and action.`

## Architecture Ownership and Change Approval

### Ownership Declaration

The Identity, Access & Account Security Architecture is a security-critical subdomain of the LinkCraftor Security Architecture.

It must have named accountability for:

- Architecture ownership
- Authentication policy
- Authorization policy
- Credential protection
- Account-recovery policy
- Account-takeover protection
- Runtime implementation
- Frontend security implementation
- Operational monitoring
- Change approval

### Responsible Authorities

| Authority | Responsibility |
|---|---|
| Identity Security Architecture Owner | Maintains the canonical architecture and domain boundaries |
| Security Architecture Authority | Confirms alignment with LinkCraftor-wide security requirements |
| Identity Service Owner | Implements authentication and session controls |
| Authorization Service Owner | Implements roles, permissions and tenant protection |
| Frontend Security Owner | Implements approved authentication and Security Centre interfaces |
| Security Operations | Monitors abuse, takeover and emergency events |
| Architecture Registry | Records versions, dependencies, classifications and migration requirements |
| Owner Control Console Authority | Presents protected approvals and migration decisions |
| LinkCraftor Owner | Final approval for major, critical and exceptional risk changes |

One person may temporarily perform multiple roles during early development, but the responsibilities and evidence must remain logically separated.

### Change Classifications

Identity-security changes must be classified as:

| Classification | Examples |
|---|---|
| `PATCH` | Documentation correction or non-behavioural internal improvement |
| `MINOR` | Backward-compatible authentication method, policy or evidence enhancement |
| `MAJOR` | Breaking identity schema, token, session, role or authentication-flow change |
| `EMERGENCY` | Time-critical security containment during an active or imminent incident |

The Architecture Registry Change Classification Engine remains authoritative for final classification.

### Mandatory Change Record

Every material change must record:

- Change identifier
- Requester
- Description and justification
- Affected components
- Security impact
- Tenant impact
- Credential impact
- Data and privacy impact
- Compatibility impact
- Migration requirement
- Testing evidence
- Rollout plan
- Rollback plan
- Monitoring plan
- Required approvals
- Final decision
- Architecture version

### Approval Requirements

- Patch changes require responsible technical review.
- Minor changes require identity-security and affected-service review.
- Major changes require security review, migration assessment and owner approval.
- Emergency changes follow the emergency override policy.
- A requester cannot provide every required approval for their own high-risk change.
- Approval must occur before production activation unless the emergency process explicitly permits containment first.

### Prohibited Unreviewed Changes

No component may independently change:

- Accepted authentication methods
- Password or passkey policy
- MFA enforcement
- Token signing or validation
- Session lifetimes
- Recovery requirements
- Assurance-level definitions
- Step-up requirements
- Role or permission semantics
- Tenant-isolation rules
- Account-takeover responses
- Security audit requirements

### Deployment and Rollback

Approved changes must have:

- Versioned configuration
- Environment-specific rollout
- Pre-deployment validation
- Controlled production deployment
- Security monitoring
- Defined success and failure criteria
- Tested rollback or containment
- Post-deployment evidence

Rollback must not restore a known-vulnerable security state.

### Ownership Enforcement Rule

`Every identity-security control has a named owner, and every material change is classified, reviewed, versioned, tested, approved and auditable before becoming permanent.`

## Non-Weakenable Security Defaults

### Security Floor

LinkCraftor users, workspaces, subscriptions, plugins and ordinary administrators may strengthen permitted security settings but cannot weaken the mandatory security floor.

### Mandatory Defaults

The following defaults cannot be disabled through ordinary customer settings:

1. Protected operations default to denial.

2. Authentication and authorization remain separate mandatory decisions.

3. Tenant isolation is enforced by the backend.

4. Raw passwords are never stored or logged.

5. Passkey private keys are never collected by LinkCraftor.

6. MFA secrets and recovery credentials receive approved protection.

7. Authentication tokens have defined expiration and validation requirements.

8. Session and credential revocation remains available.

9. Secure transport is required for authentication traffic.

10. Secure cookie controls apply where browser cookies are used.

11. Account-enumeration-resistant responses are required.

12. Signup, login, MFA and recovery endpoints remain rate limited.

13. Brute-force and credential-stuffing protection remains active.

14. Account-takeover detection and containment cannot be disabled globally by a customer.

15. Step-up authentication remains mandatory for protected security actions.

16. Owner Console and support identities require strong authentication.

17. Sensitive operator actions remain auditable.

18. Authentication and authorization failures fail secure.

19. Frontend permission hiding never replaces backend enforcement.

20. Credentials and reusable secrets are excluded from logs and analytics.

21. Recovery cannot silently bypass authentication protections.

22. Critical security notifications remain enabled.

23. Workspace ownership transfer remains protected.

24. Role and membership removal invalidates affected access.

25. No component may create a shadow authentication authority.

### Customer-Configurable Strengthening

Customers may be permitted to strengthen security by:

- Requiring MFA for all members
- Restricting accepted authentication methods
- Shortening session duration
- Requiring more frequent step-up
- Restricting API and plugin scopes
- Limiting approved domains
- Enforcing enterprise SSO
- Restricting administrator roles
- Increasing notification coverage

Customer configuration cannot reduce controls below the mandatory floor.

### Safe Configuration Behaviour

Security configuration must:

- Use secure defaults
- Validate every change
- Reject unsupported values
- Require step-up for sensitive changes
- Record previous and new values
- Identify the actor
- Produce security evidence
- Support safe rollback
- Prevent configuration from silently expiring into a weaker state

### Secret Display Rule

Passwords, password hashes, MFA seeds, recovery-code values, passkey private keys and reusable session credentials must never be displayed in customer, support or Owner Console interfaces.

A newly generated secret may be displayed once only when specifically required, after which only a safe identifier or fingerprint may be shown.

### Failure Rule

Missing, malformed or unavailable security configuration must resolve to the approved secure default, not to an unrestricted state.

### Security-Floor Enforcement Rule

`Configuration may increase protection but may not reduce LinkCraftor below its mandatory identity-security floor.`

## Emergency Security Policy Overrides

### Emergency Override Purpose

An emergency security override is a temporary, controlled and auditable measure used to contain an active or imminent identity-security threat or restore a critical security capability safely.

It is not an ordinary configuration mechanism.

### Permitted Emergency Uses

Emergency controls may be used to:

- Block a compromised authentication method
- Revoke sessions or token families
- Force global logout
- Require stronger authentication
- Temporarily restrict signup or recovery
- Disable a compromised integration
- Block suspicious networks, devices or credential patterns
- Suspend affected identities
- Reduce credential or session lifetimes
- Require additional approval
- Contain an account-takeover campaign
- Activate an emergency signing-key rotation

Emergency changes should normally make access more restrictive.

### Prohibited Overrides

An emergency override must never:

- Disable authentication for protected resources
- Default authorization to allow
- Disable tenant isolation
- Permit customer impersonation
- Expose passwords or credential secrets
- Store credentials in plaintext
- Disable mandatory security evidence
- Convert customer credentials into AWS credentials
- Grant unrestricted Owner Console access
- Remove all account-recovery verification
- Permanently bypass MFA or step-up requirements
- Conceal the override from audit evidence
- Remain active without an expiration

### Emergency Authority

Emergency activation must require an authorized security or owner-level operator using:

- A separately governed operator identity
- Strong authentication
- Current step-up authentication
- Explicit emergency permission
- A reason code
- An incident identifier
- Defined scope
- Defined expiration
- Complete evidence

Where immediate containment is essential, a designated responder may activate a pre-approved restrictive control before secondary approval. Secondary review must follow within the defined emergency window.

Risk-increasing emergency actions require dual approval before activation unless a separately approved break-glass procedure explicitly states otherwise.

### Mandatory Emergency Record

Every override must record:

- Override identifier
- Incident identifier
- Requester and approver
- Activation reason
- Threat being addressed
- Affected identities, tenants or systems
- Previous policy
- Temporary policy
- Start time
- Automatic expiration time
- Expected impact
- Monitoring requirements
- Rollback or replacement plan
- Final review outcome
- Evidence references

### Time-Bounded Behaviour

Every emergency override must:

- Have an explicit expiration
- Expire automatically
- Produce warning notifications before expiration
- Be reviewed if extension is required
- Require a new approval for extension
- Be removed when the threat ends
- Never silently become permanent policy

A permanent change must follow the normal architecture change process.

### Break-Glass Boundary

Break-glass access belongs to the separately governed workforce and infrastructure identity plane.

It must not:

- Create a customer session
- Impersonate a customer
- Reveal customer credentials
- Bypass tenant isolation
- Become a reusable normal-access method

Break-glass use requires strong authentication, narrow scope, immediate notification and enhanced evidence.

### Monitoring and Containment

While an emergency override is active, LinkCraftor must monitor:

- Authentication failures
- Authorization denials
- Affected-user impact
- Suspicious activity
- Session revocation
- Recovery activity
- Operator actions
- Override effectiveness
- Unexpected side effects

Failure of an emergency control must escalate through the incident-response process.

### Closure Requirements

An emergency override may be closed only after:

- The threat is contained or resolved
- Temporary access changes are removed
- Affected credentials are rotated where necessary
- Sessions are re-evaluated
- Monitoring confirms stable operation
- Residual risk is recorded
- Permanent remediation is assigned
- The final incident and override evidence is preserved

### Emergency Override Enforcement Rule

`Emergency authority is temporary, narrowly scoped, strongly authenticated, explicitly approved, continuously monitored, automatically expiring and fully auditable; it never authorizes silent weakening of LinkCraftor's fundamental security boundaries.`

<!-- PHASE_2_ITEM_2_1_MANAGED_IDENTITY_FOUNDATION -->

## Phase 2 - Identity Provider and Cryptographic Foundation

### 2.1 Managed Customer-Identity Foundation Evaluation

- Item status: `IN_PROGRESS`
- Provider decision: `NOT_APPROVED`
- Leading candidate: `Amazon Cognito User Pools`
- Candidate status: `CANDIDATE_UNDER_EVALUATION`
- AWS architecture readiness: `NOT_YET_ASSESSED`
- AWS deployment status: `NOT_STARTED`
- Implementation authorization: `NONE`
- Architecture posture: `PROVIDER_NEUTRAL`
- Customer identity plane: `SEPARATE_FROM_AWS_IAM`

#### What Has Been Completed

The repository discovery step has been completed.

It established that:

- No customer identity provider is currently installed.
- No customer authentication runtime currently exists.
- No Cognito user pool has been created by this architecture work.
- No provider-specific dependency currently locks LinkCraftor to Cognito, Auth0, Clerk, Firebase, Keycloak or Okta.
- The existing cloud-service portfolio lists Cognito only as conditionally approved when selected by this architecture.

Repository discovery does not constitute provider selection, AWS deployment, runtime integration or production certification.

<!-- PHASE_2_ITEM_2_1_APPROVED_IDENTITY_REALMS -->

#### Approved Identity Realms and Product Identity Continuity

- Requirement status: `APPROVED`
- Requirement ID: `2.1-R1-R2`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-02`
- Provider dependency: `NONE`
- AWS deployment authorization: `NONE`

LinkCraftor adopts three distinct identity realms:

1. Customer Realm
2. Staff Realm
3. Machine and Installation Realm

These realms may interoperate through explicit contracts, but they must not silently share credentials, sessions, permissions or recovery authority.

##### Customer Realm

The Customer Realm contains human customers who use LinkCraftor products.

Customer principals may include:

- Individual customers
- Agency owners
- Company workspace owners
- Workspace administrators
- Workspace members
- Billing administrators

Workspace owner, administrator, member and billing-administrator designations are authorization roles. They are not separate human identities.

One human customer must have one canonical LinkCraftor customer principal that can participate in multiple workspaces and hold different roles in each workspace.

A customer must not be required to create separate human accounts for:

- The WordPress Linking Plugin
- The LinkCraftor web Editor
- Customer billing
- Subscription management
- The Customer Security Centre
- Future approved LinkCraftor customer applications

The same customer principal may access these product channels subject to entitlement, workspace membership, authentication assurance and authorization policy.

##### Staff Realm

The Staff Realm contains authorized internal operators, including:

- Founder and Owner
- Support personnel
- Engineering personnel
- Security operators
- Finance and billing personnel
- Other explicitly approved staff roles

Staff access must use the Universal Staff Operations Portal or another approved workforce entry point.

Staff identities require stronger authentication, monitoring and authorization than ordinary customer identities.

A staff identity must not automatically inherit customer access.

A person who legitimately requires both customer and staff access must use logically separate security contexts. Customer sessions must not become staff sessions, and staff sessions must not become customer sessions.

Cross-company staff identity may be shared through the approved Universal Staff Operations identity boundary, but every action must retain company, product, role and authorization scope.

##### Machine and Installation Realm

The Machine and Installation Realm contains non-human actors such as:

- Connected WordPress installations
- Approved API clients
- Backend services
- Runtime workers
- Scheduled jobs
- Integration clients

A WordPress installation must receive its own revocable installation identity linked to the appropriate customer workspace.

A WordPress installation must never store or reuse a customer's password, MFA secret, passkey credential or interactive session as its machine identity.

Machine identities must use scoped, rotatable and independently revocable credentials.

Internal AWS workloads, runtime jobs and service identities remain under their canonical AWS IAM and Universal Runtime identity authorities. This identity architecture defines their trust contracts but does not replace those authorities.

##### Cross-Realm Separation Rules

The following rules are mandatory:

- Customer credentials must not authenticate staff operations.
- Staff credentials must not be embedded in customer products.
- Human credentials must not be used as permanent machine credentials.
- Machine credentials must not permit interactive human login.
- Recovery in one realm must not automatically recover another realm.
- Revocation must be independently enforceable per realm and identity.
- Every transition between realms must be explicit, authorized, logged and auditable.
- No realm may silently elevate privileges in another realm.

##### Shared Product Account Rule

The WordPress Linking Plugin and future LinkCraftor web Editor must share the same canonical customer-account authority.

Product access remains independently controlled through:

- Subscription entitlement
- Workspace membership
- Product permission
- Connected-site ownership
- Authentication assurance
- Security and risk state

Sharing a customer identity does not mean every customer automatically receives every product or permission.

##### Approval Limitation

This approval defines LinkCraftor's identity populations and product-account continuity only.

It does not:

- Select Amazon Cognito or another provider
- Create an AWS resource
- Authorize production implementation
- Define final signup methods
- Define final MFA or passkey policy
- Complete Phase 2.1

<!-- PHASE_2_ITEM_2_1_APPROVED_SIGNUP_AND_GOOGLE -->

#### Approved Customer Signup, Verification and Google Sign-In Journey

- Requirement status: `APPROVED`
- Requirement ID: `2.1-R3`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-02`
- Provider dependency: `PROVIDER_NEUTRAL`
- Provider decision: `NOT_APPROVED`
- AWS deployment authorization: `NONE`
- Google deployment authorization: `NONE`

##### Approved Customer Signup Methods

LinkCraftor approves two customer signup and login routes:

1. Continue with email
2. Continue with Google

The Google route is optional. The email route must remain available so that LinkCraftor does not become operationally dependent on Google.

The approved MVP position is:

- Email and password signup is supported.
- Email verification is mandatory for email signup.
- Continue with Google is supported.
- A Google-verified email may satisfy initial email-channel verification.
- Passkey enrollment is offered after account creation.
- MFA enrollment is offered or required according to the later assurance policy.
- A phone number is not mandatory during initial signup.
- Public staff signup is prohibited.
- Microsoft login is deferred for later evaluation.
- Enterprise SSO is deferred to its dedicated requirement.
- Additional social providers are not required for MVP.

##### Canonical Customer Identity

Every customer must receive an immutable LinkCraftor `principal_id`.

Email addresses and external-provider identifiers are login bindings. They are not the permanent owner identifier for LinkCraftor business records.

The canonical relationship is:

`external identity binding -> LinkCraftor principal_id -> workspace memberships and product entitlements`

Changing an email address or linking another authentication method must not change the customer's canonical principal.

##### Continue With Email Journey

Initial email signup collects only:

- Email address
- Password
- Acceptance of the current Terms of Service
- Acceptance or acknowledgement of the current Privacy Notice

Additional profile and workspace information should be collected after verification unless required earlier for security or legal reasons.

The account begins in:

`PENDING_EMAIL_VERIFICATION`

LinkCraftor must send:

- A one-time verification link
- An optional six-digit verification code
- A clear expiry time
- Instructions for reporting an unauthorized signup

The default verification lifetime is 30 minutes.

The verification secret must:

- Be generated using an approved secure random generator
- Be stored only in protected or hashed form when LinkCraftor controls storage
- Be invalidated immediately after successful use
- Be invalidated when a replacement verification message is issued
- Be subject to attempt throttling
- Be excluded from logs, analytics and support interfaces

Expired verification attempts must allow the customer to request a new verification transaction without exposing whether another account exists.

Email verification proves control of the email channel. It does not prove legal identity, company ownership, employment authority or website ownership.

##### Continue With Google Journey

The frontend may display an approved Google-branded button such as:

`Continue with Google`

The Google authentication request must be limited to the minimum authentication scopes:

- `openid`
- `email`
- `profile`

LinkCraftor must not request Google Drive, Gmail, Contacts, Calendar or other Google API access merely for authentication.

The trusted backend or approved identity provider must validate:

- Token signature
- Issuer (`iss`)
- Audience (`aud`)
- Expiration (`exp`)
- Nonce when used
- Authorized presenter when applicable
- Email verification status
- The stable Google subject identifier (`sub`)

The Google `sub` identifier, together with the trusted issuer, identifies the Google account binding.

The Google email address must not be used as the permanent external-account identifier because email addresses may change.

A new Google-authenticated customer must still:

- Accept LinkCraftor's Terms of Service
- Receive or acknowledge the Privacy Notice
- Create or join a workspace
- Satisfy applicable product-entitlement rules
- Complete required security setup
- Receive a LinkCraftor account-creation notification

A Google-verified email does not prove company ownership, connected-site ownership or authority to represent an organization.

##### Existing Account Linking

LinkCraftor must not silently merge accounts merely because an email returned by Google matches an existing LinkCraftor email.

When a matching account exists:

1. Present a generic existing-account continuation message.
2. Require authentication to the existing LinkCraftor account.
3. Require explicit confirmation to link Google.
4. Bind the trusted Google issuer and `sub` to the existing principal.
5. Record a security event.
6. Notify the customer through an already verified channel.
7. Preserve the ability to report unauthorized linking.

Disconnecting Google must require step-up authentication.

LinkCraftor must not remove the customer's final usable authentication or recovery method without first establishing another approved method.

##### Post-Verification Journey

After successful email or Google verification:

1. Create or activate the canonical customer principal.
2. Record the applicable legal-consent versions and timestamps.
3. Send an account-created security notification.
4. Allow the customer to create a workspace or join an invited workspace.
5. Offer passkey enrollment.
6. Offer or require MFA according to policy.
7. Encourage at least two independent authentication or recovery methods.
8. Continue to the selected LinkCraftor product.

##### WordPress Plugin Connection Journey

The WordPress plugin must not collect or store a customer's LinkCraftor password, Google credential, Google ID token or reusable human session credential.

The approved connection journey is:

1. The customer selects `Connect to LinkCraftor` in WordPress.
2. The browser opens the official LinkCraftor authentication interface.
3. The customer chooses Continue with email or Continue with Google.
4. LinkCraftor authenticates the customer.
5. The customer selects or creates a workspace.
6. LinkCraftor displays the exact WordPress site requesting access.
7. The customer explicitly approves the connection.
8. LinkCraftor issues a short-lived one-time authorization code.
9. The plugin exchanges the code for its own scoped installation credential.
10. The installation credential is linked to the approved workspace and site.

The connection flow must use Authorization Code with PKCE or an equivalently approved secure flow.

Redirect destinations must be exactly registered and validated. Open redirectors and wildcard trust are prohibited.

##### Frontend UI Requirements

The customer authentication frontend must include:

- Create account
- Continue with Google
- Continue with email
- Password entry
- Check your email
- Enter verification code
- Resend verification
- Verification expired
- Account verified
- Existing account continuation
- Explicit Google-account linking confirmation
- Create workspace
- Join invited workspace
- Secure your account
- Register a passkey
- Configure MFA
- Connect WordPress site
- Review site connection
- Connection approved
- Signup blocked or under review
- Report unauthorized signup or account linking

The UI must be responsive, keyboard accessible and screen-reader compatible.

The UI must not reveal whether an email, Google account or workspace membership exists when disclosure would enable account enumeration.

Google buttons and consent presentation must comply with current Google branding and user-data requirements.

##### Signup Abuse Protection

Both signup routes require:

- Per-IP rate limits
- Per-account and per-email limits where applicable
- Verification resend cooldowns
- Progressive delay
- Risk-based bot challenges
- Disposable-email and reputation signals where lawful
- Duplicate-account protection
- Generic security-sensitive responses
- Security-event logging
- Suspicious-signup containment
- Monitoring for automation and credential stuffing

An IP address alone must not permanently lock or terminate a legitimate customer account.

##### Google Availability and Recovery

Google authentication is an optional convenience method, not LinkCraftor's sole account-recovery authority.

A Google-only customer must be encouraged to add:

- A passkey
- Another approved authentication method
- An approved recovery method

If Google is unavailable, the email route and any independently enrolled approved method must remain available according to security policy.

Loss, suspension or deletion of a Google Account must not automatically delete the corresponding LinkCraftor principal or business records.

##### Cost and Commercial Boundary

Basic Sign in with Google currently has no planned direct Google per-login charge for the approved authentication-only scopes.

Before production, LinkCraftor must revalidate:

- Current Google Identity Services terms and pricing
- Google brand-verification requirements
- Managed identity-provider MAU pricing
- Email-delivery costs
- SMS costs if SMS is later enabled
- Security-assessment requirements if sensitive or restricted Google scopes are ever proposed

Any Cognito, Auth0, Clerk, Google Identity Platform or other managed-provider charges remain part of the later provider and cost comparison.

No sensitive or restricted Google scope may be added without a new security, privacy, cost and founder-approval review.

##### Approval Limitation

This approval defines the required customer journey and supported signup choices.

It does not:

- Select Cognito or another managed identity provider
- Create a Google Cloud project or OAuth client
- Create an AWS resource
- Install an authentication SDK
- Authorize production deployment
- Complete Phase 2.1

<!-- PHASE_2_ITEM_2_1_APPROVED_WORKSPACE_ENTERPRISE_IDENTITY -->

#### Approved Workspace Invitations, Membership Lifecycle and Enterprise Identity Policy

- Requirement status: `APPROVED`
- Requirement ID: `2.1-R4`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-02`
- Provider dependency: `PROVIDER_NEUTRAL`
- Provider decision: `NOT_APPROVED`
- AWS deployment authorization: `NONE`
- Google deployment authorization: `NONE`
- Enterprise SSO deployment authorization: `NONE`
- SCIM deployment authorization: `NONE`

##### Workspace Security Boundary

A LinkCraftor workspace is a tenant authorization boundary.

One canonical LinkCraftor principal may belong to multiple workspaces. Access to one workspace must never imply access to another workspace.

The canonical relationship is:

`principal_id -> workspace membership -> workspace role -> permitted actions`

A membership must contain, directly or by authoritative reference:

- Immutable membership identifier
- Immutable LinkCraftor principal identifier
- Immutable workspace identifier
- Current role
- Current membership state
- Authorization version
- Creation and modification timestamps
- Invitation or provisioning provenance
- Actor responsible for material changes

Email addresses, Google identifiers and identity-provider identifiers must not be used as workspace ownership keys.

##### Initial Workspace Roles

The initial role model contains:

| Role | Baseline authority |
|---|---|
| Owner | Controls the workspace, ownership, membership administration and security-critical workspace settings |
| Administrator | Manages ordinary workspace settings and members within delegated limits |
| Member | Uses authorized LinkCraftor products and workspace resources |
| Billing Administrator | Manages billing information and subscription administration without receiving general content or security authority |

Custom enterprise roles may be introduced later through a separately approved authorization design.

The following rules apply:

- Permissions must be enforced by trusted backend authorization.
- A frontend label must never be treated as authorization evidence.
- Billing authority must not imply identity-security authority.
- Product entitlement must not imply workspace administration.
- Administrator authority must not silently equal Owner authority.
- Owner and high-privilege role changes require step-up authentication.
- Role assignments must follow least privilege.
- Default membership assignment must never be Owner or Administrator.

##### Workspace Invitation Lifecycle

An authorized Owner or Administrator may initiate an invitation by entering:

- Invitee email address
- Proposed workspace role
- Optional permitted product scope where supported

The approved invitation journey is:

1. Validate the inviter's current membership and invitation permission.
2. Validate workspace seat, plan and policy limits.
3. Create a `PENDING` invitation.
4. Generate a high-entropy one-time invitation token.
5. Store only a protected cryptographic hash of the token.
6. Send the invitation to the intended email address.
7. Require the invitee to authenticate through an approved LinkCraftor method.
8. Require the authenticated verified email to match the invited email.
9. Display the workspace, inviter and proposed role.
10. Require explicit acceptance.
11. Create the active membership transactionally.
12. Mark the invitation `ACCEPTED`.
13. Notify the inviter and new member.
14. Record authoritative security events.

An invitation alone grants no workspace permission.

The default invitation lifetime is seven days.

Invitation states are:

`PENDING -> ACCEPTED`

`PENDING -> EXPIRED`

`PENDING -> REVOKED`

An accepted, expired or revoked invitation must not be reusable.

Invitation-token requirements are:

- Generated by an approved cryptographically secure random generator
- Sufficient entropy to resist guessing
- Bound to one workspace
- Bound to one normalized invited email address
- Bound to the proposed role
- Bound to an expiry time
- One-time use
- Revocable
- Excluded from logs, analytics and support displays
- Subject to request and attempt rate limits
- Invalidated when a replacement invitation is issued

Resending an invitation must invalidate its previous token.

Invitation issuance must respect workspace seat limits, subscription rules, risk controls and abuse-prevention limits.

If an invitee authenticates with the wrong Google account, LinkCraftor must not disclose protected workspace information. The interface must instruct the customer to use the invited account or request a new invitation.

##### Membership Lifecycle

The membership states are:

`ACTIVE -> SUSPENDED -> ACTIVE`

`ACTIVE -> REMOVED`

`SUSPENDED -> REMOVED`

A suspended membership:

- Cannot access the workspace
- Retains the membership record for investigation and recovery
- Retains appropriate audit history
- May be reactivated by an authorized actor

A removed membership:

- Immediately loses workspace access
- Does not delete the global LinkCraftor principal
- Does not remove memberships in other workspaces
- Does not automatically delete business records
- Must remain represented in security and audit evidence

Suspension, removal and security-critical role changes must invalidate applicable workspace authorization caches and sessions within the approved revocation objective.

Authorization caches must be tied to a membership or authorization version so stale authorization can be rejected.

Role changes must be:

- Performed by an authorized actor
- Validated against owner-protection rules
- Recorded in security evidence
- Communicated to the affected member
- Protected by step-up authentication when privilege increases materially

##### Owner Protection and Transfer

Every active workspace must retain at least one active Owner.

The last active Owner must not be removed, demoted or allowed to leave.

Ownership transfer requires:

1. Step-up authentication by the current Owner.
2. Selection of an eligible active member.
3. Explicit acceptance by the proposed new Owner.
4. Revalidation of both memberships.
5. Transactional completion of the transfer.
6. Notifications to all affected Owners.
7. A high-severity security event.

The existing Owner must retain ownership until the transfer completes successfully.

Support personnel must not bypass the last-Owner rule through ordinary administration.

Any exceptional ownership recovery must follow the separately approved account-recovery and privileged-operations process.

##### Tenant-Isolation Enforcement

Every protected workspace operation must evaluate:

- The principal is active.
- The workspace is active.
- The membership belongs to that principal and workspace.
- The membership is active.
- The requested resource belongs to the same workspace.
- The role permits the requested action.
- Product entitlement permits the operation.
- Required authentication assurance has been satisfied.
- Current security and risk state permits the operation.

Every workspace-owned database record, object, event, job and audit record must carry an authoritative workspace reference.

The active workspace context must be explicit. It must not be inferred only from a browser route, editable request field or frontend state.

Tokens may contain workspace hints, but a token claim alone must not be the sole long-lived authority for current membership after suspension, removal or role change.

Cross-workspace enumeration, error disclosure and identifier substitution must fail securely.

Background jobs and WordPress installations must receive explicit workspace scope and must not inherit all workspaces belonging to a human principal.

##### Enterprise Federation Policy

Future enterprise federation may support:

- OpenID Connect
- SAML 2.0
- Approved workforce identity providers
- Verified organization domains
- Organization-specific SSO enforcement

An enterprise identity must be mapped using a stable trusted provider identifier, such as trusted issuer plus subject. Email alone must not be the permanent federation identifier.

Domain verification proves control of a domain-management channel. It does not:

- Automatically create memberships
- Automatically grant product access
- Automatically create administrators
- Prove employment for every email address
- Transfer ownership of existing accounts
- Merge existing principals

Enterprise SSO activation must be staged:

1. Verify the organization domain.
2. Configure provider metadata and credentials.
3. Validate signatures, issuer, audience and redirect locations.
4. Test with restricted pilot identities.
5. Test account linking and deprovisioning.
6. Confirm approved emergency Owner access.
7. Notify affected members.
8. Enable enforcement only after successful validation.

A failed or unavailable enterprise provider must not cause LinkCraftor to bypass authentication.

##### Just-in-Time Provisioning

Just-in-time provisioning is disabled by default.

If separately enabled for an enterprise workspace, it must require:

- Explicit Owner approval
- Verified organization domains
- Approved provider and tenant identifiers
- An explicit lowest-privilege default role
- Workspace seat and entitlement validation
- Audit evidence
- Rate limits and abuse controls

Just-in-time provisioning must never automatically assign Owner or Administrator.

An authenticated enterprise identity must not receive membership merely because its email suffix resembles a workspace domain.

##### SCIM Provisioning Policy

Future enterprise provisioning may support SCIM 2.0 for:

- User creation
- User attribute updates
- Membership activation
- Membership suspension
- Membership removal
- Approved group-to-role mappings

SCIM provisioning must affect only the authorized enterprise workspace.

A SCIM `active=false` operation must suspend the applicable workspace membership. It must not delete the global LinkCraftor principal or affect unrelated workspaces.

SCIM requirements include:

- TLS-protected connections
- Narrowly scoped machine credentials
- Independently revocable credentials
- Credential rotation
- No reusable human password
- No credential exposure in logs
- Idempotent provisioning operations
- Replay and duplicate protection where applicable
- Complete provisioning audit evidence

Group-to-role mappings must be explicit and reviewable.

A group mapping must never automatically grant Owner. Administrative role mappings require separate approval and stronger controls.

##### Enterprise Recovery and Emergency Access

Local LinkCraftor recovery must not bypass an enterprise workspace's enforced identity-provider policy.

Enterprise deactivation or confirmed compromise must trigger timely workspace-access revocation.

An enterprise workspace must maintain an approved emergency-access design before mandatory SSO enforcement.

Emergency Owner accounts must:

- Be explicitly designated
- Use phishing-resistant authentication
- Avoid dependency on the same enterprise provider
- Be tightly monitored
- Be used only for documented emergencies
- Generate high-severity security events
- Be reviewed after every use

##### Frontend UI Design

The workspace security frontend must include the following surfaces.

**Workspace Members**

- Searchable member list
- Name and verified email
- Role
- Membership state
- Authentication or SSO status where disclosure is appropriate
- Date joined
- Last relevant security change
- Actions permitted to the current operator

**Invitations**

- Invite-member action
- Email and role fields
- Clear explanation of proposed access
- Pending invitation list
- Expiry time
- Resend action
- Revoke action
- Invitation status
- Seat-limit and policy feedback

**Invitation Acceptance**

- LinkCraftor branding
- Invited workspace name
- Inviter identity where safe
- Proposed role
- Sign in with email
- Continue with Google
- Wrong-account warning
- Explicit Accept invitation action
- Decline or report invitation action
- Expired, revoked and already-used states

**Member Administration**

- Change role
- Suspend access
- Reactivate access
- Remove from workspace
- Reason and impact confirmation
- Step-up challenge for sensitive changes
- Protection against changing the last Owner
- Success and failure notifications

**Ownership Transfer**

- Current Owner verification
- Proposed new Owner selection
- Step-up authentication
- New Owner acceptance
- Clear transfer consequences
- Pending and completed status
- Cancellation before completion

**Enterprise Identity**

- Domain verification
- Configure OIDC or SAML
- Test connection
- Pilot-user status
- Enable or disable enforcement
- Configure SCIM
- Rotate or revoke SCIM credentials
- Group-mapping review
- Provisioning status and error history
- Emergency-access readiness
- Security history

The frontend must be responsive, keyboard accessible and screen-reader compatible.

Destructive and privilege-increasing actions require clear confirmation. The interface must not reveal protected membership or workspace information to unauthenticated or unauthorized users.

Frontend controls initiate operations only. Trusted backend services make all final authorization decisions.

##### Security Events and Notifications

The authoritative event model must include:

- `workspace_invitation_created`
- `workspace_invitation_sent`
- `workspace_invitation_resent`
- `workspace_invitation_accepted`
- `workspace_invitation_expired`
- `workspace_invitation_revoked`
- `workspace_membership_created`
- `workspace_membership_role_changed`
- `workspace_membership_suspended`
- `workspace_membership_reactivated`
- `workspace_membership_removed`
- `workspace_ownership_transfer_started`
- `workspace_ownership_transfer_completed`
- `enterprise_domain_verified`
- `enterprise_sso_configured`
- `enterprise_sso_enforcement_changed`
- `enterprise_scim_configured`
- `enterprise_provisioning_changed`

Material membership, ownership, SSO and provisioning changes must notify affected customers and appropriate workspace Owners through approved verified channels.

##### Approval Limitation

This approval defines workspace invitations, membership lifecycle, tenant-isolation requirements and future enterprise identity policy.

It does not:

- Select Cognito or another managed identity provider
- Configure OIDC, SAML or SCIM
- Verify an enterprise domain
- Create an AWS or Google resource
- Implement runtime authorization
- Authorize production deployment
- Complete Phase 2.1

#### What Has Not Been Completed

The following work remains:

1. Define MFA, passkey, recovery and step-up requirements.
2. Define expected login bursts and concurrent-session capacity.
3. Define data location, privacy and retention requirements.
4. Assess dependencies on the unfinished general AWS architecture.
5. Compare qualified managed identity providers.
6. Estimate provider, messaging, security and high-availability costs.
7. Obtain explicit founder approval before recording a final provider decision.

#### Relationship to the General AWS Architecture

The general AWS architecture and this identity architecture are separate but connected.

The general AWS architecture must eventually provide or approve:

- AWS account and environment structure
- Primary and recovery Regions
- Domain and DNS management
- TLS certificates
- AWS WAF protection
- Email and SMS delivery
- CloudWatch monitoring and alarms
- Security-event destinations
- AWS KMS and secret-management boundaries
- Infrastructure-as-code ownership
- Service quotas and capacity planning
- Backup, failover and disaster-recovery policy

The identity architecture may define its requirements before those components are built, but production deployment must not occur until the required AWS integration gates pass.

#### Candidate Evaluation Position

Amazon Cognito User Pools is currently the leading candidate because LinkCraftor is expected to use AWS infrastructure.

This is not a final selection.

The evaluation must also consider:

- Auth0
- Clerk
- Firebase Authentication with Identity Platform
- Keycloak or another qualified managed alternative
- Provider cost at expected scale
- Migration and exit capability
- Enterprise federation requirements
- Passkey and MFA capability
- Account-takeover protection
- Availability and disaster recovery
- Operational complexity
- Frontend customization requirements

No candidate may be selected solely because it belongs to the expected cloud provider.

#### Provider-Neutral Boundary

Regardless of the eventual provider:

- LinkCraftor must retain its own immutable principal identifiers.
- Customer identity must remain separate from AWS IAM.
- Provider-specific code must remain behind an identity-provider adapter.
- Business services must consume canonical LinkCraftor identity contracts.
- Workspace membership, roles and permissions must remain under LinkCraftor authorization.
- No business record may depend exclusively on a provider-specific user identifier.
- Credential secrets must never be stored in ordinary LinkCraftor application tables.

#### Intended Authentication Flow

The intended conceptual flow is:

1. A customer uses the LinkCraftor signup or login interface.
2. The selected identity provider verifies the customer's authentication factors.
3. The provider returns a signed authentication result.
4. The LinkCraftor runtime verifies that result.
5. The LinkCraftor Authorization Service determines permitted workspaces, resources and actions.

The provider proves identity. LinkCraftor controls business authorization.

#### Frontend Design Scope

The eventual frontend design must include:

- Signup
- Account verification
- Login
- MFA enrollment and challenge
- Passkey enrollment and management
- Password management
- Account recovery
- Active-session review and revocation
- Trusted-device management
- Recent security activity
- Suspicious-login warnings
- Step-up authentication
- Customer Security Centre

Frontend implementation has not started under this architecture phase.

#### Scale Evaluation Gate

Provider selection must account for:

`peak authentication RPS = sign-in starts per second x authentication operations per sign-in x safety headroom`

The calculation must include:

- Signup bursts
- Login bursts
- MFA and passkey challenges
- Token refresh
- Recovery traffic
- Credential-stuffing attacks
- Bot traffic
- Provider throttling
- Regional failure scenarios

No provider may be approved based only on its default service quotas.

#### Current Decision

Amazon Cognito User Pools remains a candidate under evaluation.

No managed customer-identity provider has yet been finally selected, deployed or integrated.

#### Item 2.1 Completion Rule

Item 2.1 remains incomplete until requirements, AWS dependencies, provider comparison, scale, cost, portability and founder approval have all been documented and validated.
