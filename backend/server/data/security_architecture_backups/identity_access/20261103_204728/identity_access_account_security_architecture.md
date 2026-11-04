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

<!-- PHASE_2_ITEM_2_1_APPROVED_MFA_PASSKEY_RECOVERY_STEP_UP -->

#### Approved MFA, Passkey, Account Recovery and Step-Up Authentication Policy

- Requirement status: `APPROVED`
- Requirement ID: `2.1-R5`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`
- Provider dependency: `PROVIDER_NEUTRAL`
- Provider decision: `NOT_APPROVED`
- AWS deployment authorization: `NONE`
- Google deployment authorization: `NONE`
- Authentication SDK deployment authorization: `NONE`
- Passkey deployment authorization: `NONE`
- TOTP deployment authorization: `NONE`
- Email or SMS transmission authorization: `NONE`

##### Relationship to the Phase 1 Assurance Model

This policy operationalizes the previously approved LinkCraftor assurance model.

It does not replace or redefine:

- `AAL0` - unauthenticated
- `AAL1` - baseline authenticated
- `AAL2` - strong authenticated
- `AAL3` - high-assurance privileged
- The approved normal-authentication rules
- The approved step-up action list
- The separation between authentication assurance and authorization

Phase 1 remains authoritative for assurance meaning and mandatory step-up action categories.

##### Approved Customer Authentication Methods

| Method | LinkCraftor treatment |
|---|---|
| User-verifying passkey | Preferred phishing-resistant `AAL2` method |
| Password only | `AAL1` |
| Google OIDC sign-in | `AAL1` unless trustworthy assurance evidence proves a stronger result |
| Password plus TOTP | `AAL2` but not phishing-resistant |
| Google plus a LinkCraftor passkey or TOTP | May establish `AAL2` after complete validation |
| Saved recovery code | Recovery evidence, not an ordinary unrestricted high-assurance session |
| Email verification or reset link | Contact verification or restricted recovery |
| Remembered or trusted device | Risk signal only; never an authentication factor |

SMS and voice OTP are disabled for the MVP.

Security questions and knowledge-based authentication are prohibited.

A remembered browser, device cookie, device reputation result or trusted-device designation must not independently increase authentication assurance.

##### Mandatory MFA Policy

Workspace Owners, Administrators and Billing Administrators must enroll at least one approved `AAL2` method.

The approved privileged-role controls are:

- A newly created workspace Owner must complete strong-authentication setup before exercising security-critical Owner authority.
- A member promoted to Owner, Administrator or Billing Administrator must complete required security setup before the increased privileges become active.
- Privileged actions require current and sufficiently recent `AAL2`.
- Ordinary Members are strongly encouraged to enroll an `AAL2` method.
- An enterprise workspace may require `AAL2` for every member.
- A workspace may adopt a stronger policy but cannot weaken mandatory LinkCraftor controls.
- A phone number is not required merely to enroll MFA.
- Failure to complete mandatory setup must retain the account in a restricted security-setup state.

Staff, workforce and Owner Console identities remain governed by their separate realm and may require phishing-resistant or `AAL3` authentication.

##### Password Policy

LinkCraftor customer passwords must contain at least 15 characters.

The password system must:

- Support at least 64 characters
- Permit spaces
- Permit all normal printable characters
- Support Unicode safely where the selected provider supports it
- Compare new passwords against an approved compromised and commonly used password blocklist
- Permit password-manager-generated passwords
- Permit paste and browser autofill
- Provide clear strength and rejection guidance
- Verify the complete password without silent truncation
- Apply authentication-attempt throttling
- Prevent passwords from appearing in URLs, logs, analytics or support interfaces

The password system must not:

- Require arbitrary mixtures of uppercase, lowercase, numbers and symbols
- Require routine periodic password changes
- Store password hints accessible to unauthenticated users
- Use security questions
- Reveal whether an account exists through password-reset responses
- Send an existing password by email
- Allow support personnel to view a password

A password change is required when compromise is known or strongly suspected.

##### Password Credential Protection

Raw passwords must never be stored by LinkCraftor.

Where a managed identity provider performs password authentication:

- The provider must own protected password-verifier storage.
- Ordinary LinkCraftor business services must not receive password hashes.
- Password handling must remain inside the approved authentication boundary.
- Passwords must travel only through authenticated encrypted channels.
- Provider logs and integration logs must exclude credential values.

Any future proposal for LinkCraftor-controlled password-verifier storage requires a separate security review, approved adaptive salted password hashing, protected secret management, migration planning and founder approval.

##### Passkey Policy

Passkeys are the preferred phishing-resistant customer authentication method.

The implementation must use an approved WebAuthn-compatible standard and must:

- Use an explicitly approved relying-party identifier
- Validate the exact permitted origins
- Use server-generated cryptographically secure challenges
- Make every challenge short-lived and one-time
- Bind registration to the authenticated principal and current session
- Require user verification for an `AAL2` result
- Prefer discoverable credentials for passkey use
- Support synchronized multi-device passkeys
- Support device-bound and hardware security-key passkeys
- Permit multiple passkeys per account
- Prevent duplicate or unauthorized credential binding
- Validate credential type, challenge, origin, relying-party identifier, signature and user-verification result
- Evaluate signature-counter anomalies as risk evidence rather than relying on the counter alone
- Record backup eligibility and current backup state where provided
- Permit immediate revocation of a lost or compromised passkey

LinkCraftor may store:

- Credential identifier
- Public key
- Sign counter or counter-related risk state
- Transport hints
- Creation time
- Last-used time
- Customer-assigned passkey name
- Backup-eligibility state
- Backup-state information
- Revocation state
- Security-event references

LinkCraftor must never receive or store a passkey private key.

Default passkey attestation must preserve customer privacy. Hardware or enterprise attestation may be required only by a separately approved high-assurance policy.

Customers must be encouraged to maintain at least two independent authentication or recovery methods.

Adding a passkey requires authentication at the strongest currently available appropriate assurance level.

A newly created passkey cannot authorize its own registration.

Adding or removing a passkey must produce an independent security notification.

Removing the final usable authentication or recovery method is prohibited until another approved method exists.

##### TOTP Authenticator-App Policy

TOTP is the approved non-passkey MFA fallback for the MVP.

TOTP must be combined with an independent first factor before it can establish `AAL2`.

TOTP enrollment must:

1. Require an authenticated session.
2. Require appropriate recent authentication.
3. Generate a unique high-entropy secret.
4. Protect the secret at rest.
5. Display the QR code or manual secret only during enrollment.
6. Require successful code verification before activation.
7. Generate authoritative security evidence.
8. Notify the customer through an independently verified channel.
9. Offer creation or review of recovery codes.

TOTP verification must:

- Use narrowly bounded clock-drift tolerance
- Prevent replay of an already accepted code where technically supported
- Rate-limit failed attempts
- Apply progressive delay or containment
- Exclude codes and secrets from logs
- Record relevant risk and security events
- Fail securely when verification is unavailable

A TOTP secret must not be redisplayed after enrollment.

Replacing or disabling TOTP requires step-up authentication.

TOTP is not classified as phishing-resistant.

##### Recovery-Code Policy

Saved recovery codes must be:

- Generated using an approved secure random generator
- High entropy
- Displayed only once
- Downloadable or printable through a protected interface
- Stored only as protected one-way hashes
- Individually one-time use
- Excluded from logs and support interfaces
- Rate-limited during verification
- Revocable
- Regenerated only after appropriate authentication or controlled recovery

Regenerating recovery codes invalidates every unused code from the previous set.

Using a recovery code creates a recovery event. It does not automatically establish an unrestricted long-lived `AAL2` session.

##### Recovery Classification

LinkCraftor distinguishes between credential replacement and full account recovery.

**Credential replacement with another working authenticator**

When the customer still controls another approved authenticator:

1. Authenticate with the available method.
2. Perform required step-up.
3. Bind the replacement authenticator.
4. Review existing authenticators and sessions.
5. Notify the customer.
6. Record security evidence.

Replacing a forgotten password while another approved authenticator remains available is treated as credential replacement rather than exceptional recovery.

**Normal account recovery**

Normal recovery may use:

- A saved one-time recovery code
- Another previously enrolled passkey
- Another approved authentication method
- An enterprise-controlled recovery path where enterprise policy applies

**Exceptional account recovery**

Exceptional recovery applies when every normal authentication and recovery method is unavailable.

Exceptional recovery requires:

- Enhanced risk evaluation
- Generic non-enumerating responses
- Verified recovery evidence
- Waiting or cooling periods where risk requires them
- Independent notification
- Review of sessions and authenticators
- Restricted post-recovery assurance
- Complete security evidence
- Additional controls for privileged accounts

##### Email Recovery Limitation

A verified email recovery link may restore only a restricted `AAL1` recovery path.

Email recovery alone must not:

- Establish `AAL2`
- Remove an existing MFA method
- Remove a passkey
- Change the primary email address
- Transfer workspace ownership
- Add or remove an Owner
- Disable enterprise SSO
- Create or reveal an API credential
- Reverse high-risk account-takeover containment
- Immediately restore unrestricted privileged authority

Email recovery transactions must be:

- Short-lived
- One-time use
- Invalidated when replaced
- Rate-limited
- Protected against automated guessing
- Excluded from logs and analytics
- Presented through generic account-enumeration-resistant responses

##### Post-Recovery Containment

Successful full or high-risk recovery must:

- Revoke existing sessions and refresh credentials according to policy
- Review or invalidate potentially compromised authenticators
- Notify every suitable previously verified channel
- Establish restricted assurance
- Require enrollment or verification of secure authentication methods
- Present the customer with recent security activity
- Provide a route to report unauthorized recovery
- Increase monitoring for subsequent suspicious activity

The default high-risk post-recovery cooling period is 24 hours.

During the cooling period, policy may block:

- Workspace ownership transfer
- Primary-email changes
- Removal of strong authenticators
- Disabling mandatory MFA
- Creation or revelation of API credentials
- Enterprise SSO changes
- High-impact exports
- Permanent account or workspace deletion

A previously registered phishing-resistant authenticator may permit policy-controlled reduction of the cooling period after successful independent verification.

##### Support-Assisted Recovery

Support personnel must never:

- Ask for or view a password
- Ask for a TOTP seed
- Ask for a complete recovery-code set
- Bind an invisible authenticator
- Grant `AAL2` by administrative declaration
- Silently disable mandatory MFA
- Silently bypass enterprise SSO
- Conceal recovery from the customer or other authorized Owners

Exceptional recovery for an Owner, Administrator or other protected identity requires:

- A formal recovery case
- Evidence review
- Separation of duties or dual approval
- Notifications to existing verified channels
- Notifications to other appropriate workspace Owners
- A cooling period
- Restricted post-recovery access
- Full audit evidence
- Post-event security review

Support-assisted recovery cannot provide stronger assurance than the evidence actually verified.

##### Enterprise Recovery Boundary

Local LinkCraftor recovery must not bypass enforced enterprise identity-provider policy.

Enterprise deactivation must not be reversed merely through consumer email recovery.

Enterprise recovery must preserve:

- Workspace-specific SSO enforcement
- IdP deprovisioning decisions
- Approved break-glass controls
- SCIM membership state
- Enterprise security notifications
- Complete audit evidence

##### Authentication-Method Change Protection

Adding, replacing or removing an authenticator requires authentication appropriate to the strongest currently available method or the assurance level of the new method, according to approved policy.

The following controls apply:

- A new authenticator cannot approve its own binding.
- A replacement authenticator cannot silently invalidate every existing method.
- Security notifications must use a channel independent of the binding transaction where possible.
- The customer must receive instructions for reporting an unauthorized change.
- High-risk changes may trigger session revocation or temporary containment.
- Factor changes must remain visible in security history.
- Removal of the final usable method is prohibited.

##### Step-Up Authentication Implementation

The previously approved Phase 1 step-up action list remains authoritative.

General sensitive actions require fresh authentication, normally completed within the previous 15 minutes.

Critical ownership, credential, recovery, SSO and API-secret actions require fresh `AAL2`, normally completed within the previous five minutes.

A successful step-up result must be bound to:

- Immutable principal
- Current session
- Authentication methods
- Achieved assurance level
- Completion time
- Expiration time
- Workspace where applicable
- Protected action
- Protected resource where applicable
- Current risk state
- Correlation identifier
- Evidence reference

Critical step-up authority must be single-purpose or narrowly scoped. It must not silently authorize unrelated sensitive actions.

The canonical step-up flow is:

1. The authenticated customer requests a protected action.
2. Authorization returns `STEP_UP_REQUIRED`.
3. The Identity Service presents an approved stronger challenge.
4. The customer completes the challenge.
5. The Identity Service records updated assurance context.
6. The original action is resubmitted.
7. Authorization evaluates the action again.
8. Execution occurs only after a new `ALLOW` decision.
9. Authentication, authorization and execution evidence are correlated.

Password re-entry alone cannot establish `AAL2`.

Email confirmation alone cannot establish strong step-up.

A remembered device cannot satisfy step-up.

Elevated risk may require a phishing-resistant method or deny the action entirely.

Failed, expired, abandoned, replayed, mismatched or insufficient step-up must prevent the protected action from executing.

##### Frontend UI Design

The authentication frontend must include:

**Login and Challenge**

- Use a passkey
- Continue with Google
- Continue with email
- Password entry
- Authenticator-app code entry
- Choose another approved method
- Lost-device or unavailable-method route
- Clear challenge expiry and retry states
- Generic non-enumerating error responses

**Mandatory Security Setup**

- Explanation of why strong authentication is required
- Recommended passkey enrollment
- Authenticator-app alternative
- Recovery-code creation
- Completion status
- Restricted-state explanation
- Return to the intended action after successful setup

**Customer Security Centre**

- Authentication-method overview
- Passkey list
- Customer-defined passkey names
- Passkey creation and last-use information
- Add passkey
- Rename passkey
- Revoke lost or compromised passkey
- Authenticator-app status
- Replace or disable authenticator app
- Generate or regenerate recovery codes
- Password-change interface
- Recent authentication-method changes
- Security notifications
- Report unauthorized security change

**Step-Up Interface**

- Clear explanation of the protected action
- Required assurance level
- Passkey challenge as the preferred option
- Approved alternative method
- Challenge expiry
- Cancellation
- Failure and containment state
- Return to the exact protected action after success

**Account Recovery**

- Start recovery
- Check your email
- Enter recovery code
- Use another enrolled method
- Recovery-link expired
- Recovery under review
- Exceptional-recovery pending state
- Post-recovery restriction notice
- Review authenticators
- Review active sessions
- Secure your account
- Report unauthorized recovery

Frontend interfaces must be responsive, keyboard accessible and screen-reader compatible.

Secret values must not be exposed to analytics, session replay, error-reporting tools or ordinary support interfaces.

Frontend controls initiate authentication operations only. Trusted backend or provider-controlled components make all final security decisions.

##### Security Events and Notifications

The authoritative security-event model must include:

- `mfa_enrollment_required`
- `mfa_enrollment_completed`
- `mfa_challenge_succeeded`
- `mfa_challenge_failed`
- `mfa_method_replaced`
- `mfa_method_disabled`
- `passkey_registration_started`
- `passkey_registered`
- `passkey_authentication_succeeded`
- `passkey_authentication_failed`
- `passkey_renamed`
- `passkey_revoked`
- `totp_enrolled`
- `totp_replaced`
- `totp_disabled`
- `recovery_codes_generated`
- `recovery_code_used`
- `recovery_codes_regenerated`
- `account_recovery_started`
- `account_recovery_completed`
- `account_recovery_rejected`
- `post_recovery_containment_started`
- `post_recovery_containment_ended`
- `support_recovery_case_opened`
- `support_recovery_approved`
- `support_recovery_rejected`
- `step_up_required`
- `step_up_succeeded`
- `step_up_failed`
- `authenticator_added`
- `authenticator_removed`

Material authenticator, recovery and step-up events must notify the affected customer through suitable previously verified channels.

Notifications must never contain passwords, TOTP secrets, recovery-code values, passkey private keys or reusable session credentials.

##### Provider Evaluation Requirements

Every managed identity-provider candidate must demonstrate support for or safe integration with:

- The approved `AAL1` and `AAL2` model
- User-verifying passkeys
- WebAuthn validation requirements
- TOTP MFA
- Multiple authenticators
- Secure authenticator binding
- Recovery codes or an approved equivalent
- Independent security notifications
- Credential revocation
- Step-up authentication
- Provider-neutral identity mapping
- Custom LinkCraftor frontend requirements
- Rate limits and abuse protection
- Security-event production
- Export and migration planning

Failure to provide a required capability must be recorded as a provider gap. Provider-specific limitations must not silently weaken this policy.

##### Standards Basis

Implementation and later provider evaluation must consider the current applicable versions of:

- NIST SP 800-63B authentication and authenticator-lifecycle guidance
- W3C Web Authentication
- FIDO passkey guidance
- LinkCraftor Phase 1 assurance and step-up requirements
- Applicable privacy, accessibility and security requirements

Standards references must be revalidated before production certification.

##### Approval Limitation

This approval defines LinkCraftor's MFA, passkey, recovery and step-up requirements.

It does not:

- Select Cognito or another provider
- Install WebAuthn or an authentication SDK
- Register a relying-party identifier
- Create a passkey
- Generate a TOTP secret
- Generate recovery codes
- Send an email or SMS
- Create an AWS or Google resource
- Implement the frontend
- Authorize production deployment
- Complete Phase 2.1

<!-- PHASE_2_ITEM_2_1_APPROVED_AUTHENTICATION_SCALE_SESSION_CAPACITY -->

#### Approved Authentication Scale, Burst Capacity and Concurrent-Session Policy

- Requirement status: `APPROVED`
- Requirement ID: `2.1-R6`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`
- Provider dependency: `PROVIDER_NEUTRAL`
- Provider decision: `NOT_APPROVED`
- AWS deployment authorization: `NONE`
- Provider-quota request authorization: `NONE`
- Provisioned-capacity purchase authorization: `NONE`
- Load-test execution authorization: `NONE`
- Token-lifetime change authorization: `NONE`
- Session-configuration change authorization: `NONE`

##### Scale Principle

Thousands of customers holding valid LinkCraftor sessions must not cause thousands of managed identity-provider calls for every application request.

The intended scale model is:

1. The customer authenticates through the approved identity boundary.
2. The approved provider issues signed tokens.
3. LinkCraftor verifies those tokens through approved local cryptographic verification.
4. Normal product requests reuse valid authentication evidence.
5. The provider is contacted only when an authentication, challenge, refresh, recovery, revocation or credential-management operation requires it.
6. LinkCraftor authorization separately evaluates workspace membership, role, entitlement, resource scope, assurance and current security state.

Authentication-provider traffic and normal LinkCraftor application traffic must be measured and scaled independently.

##### Capacity Definitions

For this policy:

- A concurrent authenticated session is an unexpired, non-revoked interactive human session.
- A login start is a customer beginning an authentication flow.
- A provider operation is an operation counted against the selected provider's quota.
- A token validation is LinkCraftor verifying signed authentication evidence.
- A refresh attempt is a request for renewed authentication tokens.
- A short burst is intentionally higher traffic over a limited duration.
- Sustained capacity is traffic maintained for the specified certification period.
- Machine and installation sessions remain separate from human interactive sessions.

A concurrent session does not represent:

- A permanent server process
- A dedicated database connection
- A provider request on every API call
- A permanent open network connection
- A reusable human credential for a WordPress installation

##### Initial Certification Capacity Envelope

The approved initial certification envelope is:

| Capacity area | Certification target |
|---|---:|
| Concurrent authenticated customer sessions | 25,000 |
| Growth capacity without identity-model redesign | 100,000 |
| Sustained login starts | 100 per second for 5 minutes |
| Short login burst | 250 per second for 60 seconds |
| Sustained authenticated token validations | 5,000 per second |
| Token-validation burst | 10,000 per second for 60 seconds |
| Signup starts | 50 per second for 5 minutes |
| Token-refresh storm | 5,000 attempts within 60 seconds |
| Recovery starts | 20 per second under abuse controls |
| LinkCraftor authentication-entry availability target | 99.95 percent monthly |

These values are certification targets. They are not permanent architectural ceilings.

Growth from 25,000 to 100,000 concurrent sessions must not require:

- Changing canonical LinkCraftor principal identifiers
- Replacing workspace membership identifiers
- Rewriting the identity-realm model
- Converting customer identities into AWS IAM users
- Requiring customer re-registration solely because LinkCraftor scaled horizontally
- Moving authorization ownership into the external identity provider

Implementation must permit horizontal scaling, quota adjustment and regional evolution without changing canonical business ownership.

##### Login-Burst Calculation

Peak login-start rate must be calculated as:

`peak login starts per second = customers starting login during burst / burst duration in seconds`

Required provider-category capacity must be calculated as:

`required category RPS = provider-counted operations per flow x peak flow starts per second + refresh RPS + other operations + safety headroom`

The calculation must be performed separately for:

- Email and password authentication
- Google federation
- Passkey authentication
- TOTP challenges
- Signup
- Account confirmation
- Token redemption
- Token refresh
- Password reset
- Account recovery
- Credential changes
- Logout and revocation
- Enterprise federation
- SCIM-related identity changes where provider quotas apply

Provider-specific accounting rules must be used. One customer action must not be assumed to equal one provider operation.

##### Approved Planning Example

For 10,000 customers beginning login during five minutes:

`10,000 / 300 seconds = 33.34 login starts per second`

If the selected flow consumes two counted provider operations:

`33.34 x 2 = 66.68 provider operations per second`

With three-times forecast headroom:

`66.68 x 3 = approximately 201 provider operations per second`

This example demonstrates why monthly active-user counts alone cannot establish burst readiness.

##### Provider Headroom

The selected provider must support provisioned or contractually available capacity of at least:

`maximum certified provider workload x 2 safety headroom`

Additional headroom must be evaluated for:

- Marketing campaigns
- Enterprise onboarding
- WordPress Plugin launches
- Customer migrations
- Bot attacks
- Credential stuffing
- Google federation spikes
- Token-refresh synchronization
- Regional impairment
- Provider retries
- Recovery attacks
- Unexpected challenge multiplication

No production launch may rely only on undocumented provider bursting or assumed quota elasticity.

##### Current Cognito Candidate Observation

Amazon Cognito remains a candidate only.

As observed during the 2026-11-03 requirements review, its documented default regional category quotas included:

| Category | Observed default |
|---|---:|
| User authentication | 120 RPS, adjustable |
| Local user creation | 50 RPS, adjustable |
| Third-party user federation | 25 RPS, adjustable |
| User account recovery | 30 RPS, not adjustable |
| User updates | 25 RPS, not adjustable |

These quota observations:

- Do not select Cognito.
- Do not authorize a quota request.
- Do not guarantee future availability.
- Must be revalidated before provider selection and production.
- Must be mapped to the exact approved login flows.
- Must be evaluated together with regional aggregation rules.
- Must be evaluated together with cost and quota-increase lead time.
- Must include Google federation, MFA, passkeys and token refresh.

Cognito's default quotas do not automatically prove compliance with the approved LinkCraftor capacity envelope.

##### Local Token-Verification Boundary

Normal LinkCraftor APIs must not call the identity provider to validate every authenticated request.

Approved token verification must validate:

- Cryptographic signature
- Approved algorithm
- Issuer
- Audience or client identifier
- Expiration
- Not-before condition where present
- Token type and intended use
- Required scopes
- Key identifier
- Approved authentication context where required

Public signing keys must be:

- Retrieved only from the approved issuer
- Cached by key identifier
- Refreshed safely
- Protected against untrusted key substitution
- Retained through approved rotation overlap
- Refetched when a legitimate unknown key identifier indicates rotation
- Rejected when verification cannot be completed

Unknown, malformed, expired or incorrectly scoped tokens must fail securely.

Offline token verification does not eliminate current authorization checks.

Workspace membership, authorization version, role, entitlement, restriction and revocation-sensitive state remain LinkCraftor-controlled facts.

##### Revocation and Authorization Freshness

Local signature validation alone may not detect every revocation before token expiration.

The implementation must therefore combine:

- Appropriately bounded access-token lifetime
- Session revocation
- Authorization-version checks
- Membership-version checks
- Risk and containment state
- Stronger live checks for critical actions
- Step-up for protected operations

Exact token lifetimes remain an implementation and provider decision. R6 does not change them.

A valid signature must not override:

- Suspended workspace membership
- Removed workspace membership
- Revoked session
- Disabled account
- Account-takeover containment
- Insufficient role
- Expired entitlement
- Required step-up

##### Refresh-Storm Prevention

Clients must not refresh all tokens at one fixed synchronized moment.

The refresh model must include:

- Refresh according to approved token policy
- Randomized refresh jitter
- A single in-flight refresh per session
- Coalescing of duplicate refresh attempts
- Secure reuse of valid authentication evidence
- Bounded exponential backoff with jitter
- Strict retry limits
- Immediate termination for non-retryable credential errors
- Protection against refresh-token replay
- Monitoring of refresh failures and spikes

A token refresh must not occur on every application request.

Browser tabs sharing one session should not independently create uncontrolled refresh traffic.

##### Per-Principal Interactive Session Policy

The approved default interactive-session limits are:

- Soft limit: 10 active human sessions per customer principal
- Hard security limit: 20 active human sessions per customer principal

Approaching or exceeding the soft limit may require:

- Session review
- Step-up authentication
- Revocation of stale sessions
- Customer confirmation
- Elevated risk evaluation

At the hard limit, a new interactive session must not be created until an existing session is revoked or policy explicitly authorizes another outcome.

Enterprise workspaces may establish lower limits.

Increasing the system hard limit requires an approved security and capacity review.

Shared human customer accounts are prohibited. Each team member must use an individual principal and workspace membership.

WordPress installations, backend services, API clients and scheduled jobs must use separate machine or installation identities and must not consume human interactive-session allowance.

##### Scalable Session Registry

The canonical session registry must be capable of recording protected metadata such as:

- Session identifier
- Principal identifier
- Provider-session reference
- Authentication time
- Authentication methods
- Assurance level
- Device or browser description
- Creation time
- Last-seen time
- Approximate location where lawful
- Risk state
- Revocation state
- Authorization version
- Recovery or containment state
- Security-event references

Raw reusable tokens must not be stored in ordinary LinkCraftor application tables.

The session registry must not require a synchronous persistent write for every API request.

High-frequency activity updates must be:

- Coalesced
- Sampled
- Buffered
- Written asynchronously where safe
- Protected against unbounded queue growth

The registry must permit immediate security-relevant revocation without depending on last-seen write completion.

Session-data retention and geographic residency will be governed by the next privacy, residency and retention requirement.

##### Provider Traffic Reduction

LinkCraftor must not perform provider profile lookups on every request.

Frequently required canonical business data must be resolved through approved LinkCraftor authorities, including:

- Principal identifier
- Workspace membership
- Role
- Entitlement
- Connected-site authority
- Product permissions
- Authorization version
- Security restrictions

Provider tokens must be securely reused during their approved lifetime.

Machine-to-machine token requests must use approved caching and scope separation where applicable.

Caching must never extend a credential beyond its approved expiration or bypass revocation requirements.

##### Throttling, Backpressure and Retry Policy

Authentication traffic must use layered controls including:

- Per-IP rate limits
- Per-account rate limits
- Per-device or risk-subject limits where lawful
- Per-workspace administrative-operation limits
- Provider-category limits
- Global emergency limits
- Bot and credential-stuffing controls
- Request deduplication
- Idempotency where applicable
- Circuit breakers
- Bounded queues for appropriate non-interactive work
- Exponential backoff with jitter
- Strict retry ceilings

Invalid passwords, invalid TOTP codes, rejected passkeys and invalid recovery credentials must not be blindly retried.

Interactive authentication challenges must not be held indefinitely in queues.

A controlled waiting room may be used for a known exceptional event when:

- Capacity is temporarily constrained
- The queue is bounded
- The customer receives truthful status
- Challenge expiration is respected
- The intended destination is preserved
- Security decisions are not bypassed
- Account existence is not disclosed

##### Provider-Outage Behaviour

If the selected identity provider is unavailable:

- New authentication must fail safely.
- Signup must fail safely.
- Recovery must fail safely.
- Token refresh may fail.
- Authentication protections must not be bypassed.
- AWS IAM must not become customer login.
- Support must not issue an unrestricted substitute session.
- Existing valid tokens may continue only within approved validity, risk and revocation policy.
- Critical operations may be denied when live step-up is unavailable.
- Unknown signing keys must fail closed.
- Previously trusted cached signing keys may continue only under approved rotation rules.
- Security and operational events must be generated.
- The customer frontend must show a safe service-status message.

Google unavailability must not remove the separately approved email authentication route.

Provider availability must never weaken tenant isolation or authorization.

##### Frontend Authentication-Capacity Experience

The customer authentication frontend must:

- Prevent accidental duplicate submissions
- Show clear progress during redirects and challenges
- Provide safe retry timing
- Avoid endless loading indicators
- Preserve the intended post-login destination
- Offer another approved method where available
- Show temporary-provider or capacity messages
- Avoid exposing internal infrastructure
- Avoid account enumeration
- Announce status changes accessibly
- Remain keyboard and screen-reader accessible

The frontend must distinguish:

- Invalid credentials
- Expired challenge
- Temporary capacity condition
- Provider unavailability
- Customer-side connectivity problem
- Security containment
- Session-limit condition

The distinction must be presented without exposing protected account facts.

##### Customer Session-Management UI

The Customer Security Centre must include:

- Current session
- Other active sessions
- Browser or device label
- Authentication method
- Assurance level
- Creation time
- Last-active time
- Approximate location where lawful
- Current risk or security warning where appropriate
- Revoke one session
- Revoke all other sessions
- Report suspicious session
- Soft-limit warning
- Hard-limit resolution flow

Revoking a session must produce immediate customer feedback and authoritative security evidence.

##### Owner Control Tower Capacity UI

The future Owner Control Tower authentication-capacity view must include:

- Login starts per second
- Login completion rate
- Login failures by safe category
- Password traffic
- Google federation traffic
- Passkey traffic
- TOTP traffic
- Signup traffic
- Recovery traffic
- Token-refresh rate
- Token-validation rate
- Concurrent sessions
- Provider quota by category
- Quota utilization percentage
- Provider throttling
- LinkCraftor throttling
- p50, p95 and p99 latency
- Authentication error rate
- Email-delivery backlog
- Provider incidents
- Regional health
- Autoscaling health
- Capacity alarms
- Current certification-envelope utilization

The dashboard must not expose passwords, tokens, TOTP codes, recovery codes or passkey private material.

##### Monitoring and Alerting Requirements

Monitoring must distinguish legitimate customer load from suspected abuse.

Required signals include:

- Authentication starts
- Successful authentication
- Failed authentication
- Challenge failures
- Provider operation counts
- Provider throttles
- LinkCraftor rate-limit decisions
- Token refreshes
- Refresh failures
- Recovery starts
- Recovery completions
- Session creation
- Session revocation
- Concurrent session count
- Signing-key refreshes
- Unknown signing-key events
- Retry volume
- Circuit-breaker state
- Notification backlog

Alerts must exist for:

- Approaching provider quota
- Unplanned throttling
- Refresh storms
- Large authentication-failure spikes
- Recovery abuse
- Signing-key verification failure
- Excessive retry volume
- Session-registry degradation
- Authentication latency degradation
- Regional or provider outage

##### Load-Test Certification

Production launch requires controlled load testing of:

- Email and password login
- Google federation callback
- Passkey login
- TOTP challenge
- Signup and confirmation
- Token redemption
- Token refresh
- Recovery
- Credential changes
- Logout
- Session revocation
- Signing-key rotation
- Unknown signing-key handling
- Provider `429` responses
- Provider `5xx` responses
- Network timeouts
- Concurrent-session limits
- Membership suspension during active sessions
- Refresh storms
- Regional impairment
- Bot traffic
- Credential-stuffing traffic
- Sustained target traffic
- Short burst traffic

Load testing must use synthetic identities in an approved non-production or controlled test environment.

Production customer credentials and real customer accounts must not be used as load generators.

Certification must demonstrate:

- No cross-workspace access
- No authentication bypass
- No secret leakage
- No uncontrolled retry storm
- No duplicate security-critical operation
- No unplanned legitimate-customer throttling inside the certified envelope
- Correct session revocation
- Correct membership and authorization-version enforcement
- Complete security evidence
- Safe degradation during provider failure
- Recovery after the load returns to normal

##### Capacity Change Governance

Any material increase or reduction to the approved envelope must record:

- Forecast
- Traffic model
- Provider operation mapping
- Current quotas
- Requested quotas
- Cost effect
- Regional effect
- Test evidence
- Failure-mode assessment
- Approval
- Effective date

Emergency capacity changes must remain auditable and must not disable authentication protections.

##### Approval Limitation

This approval defines authentication scale, burst, session and certification requirements.

It does not:

- Select Cognito or another provider
- Request an AWS quota increase
- Purchase provisioned capacity
- Create a user pool
- Create users or sessions
- Change token lifetimes
- Configure session limits
- Deploy a waiting room
- Configure autoscaling
- Execute a load test
- Implement monitoring
- Implement the frontend
- Complete Phase 2.1

<!-- PHASE_2_ITEM_2_1_APPROVED_IDENTITY_DATA_PRIVACY_RETENTION -->

#### Approved Identity-Data Location, Privacy, Residency and Retention Policy

- Requirement status: `APPROVED`
- Requirement ID: `2.1-R7`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`
- Provider dependency: `PROVIDER_NEUTRAL`
- Provider decision: `NOT_APPROVED`
- AWS Region decision: `NOT_SELECTED`
- Data-migration authorization: `NONE`
- Account-deletion execution authorization: `NONE`
- Regulatory-registration authorization: `NONE`
- DPA or transfer-agreement authorization: `NONE`
- Encryption-key deployment authorization: `NONE`
- Retention-job execution authorization: `NONE`
- Integration-gate status: `DEFERRED`
- Legal status: `ARCHITECTURAL_POLICY_NOT_FINAL_LEGAL_ADVICE`

##### Purpose

This policy defines:

- What customer identity information LinkCraftor may collect
- Which authority owns each identity-data category
- Where identity data may be stored
- How identity data must be protected
- How long identity data may be retained
- How identity records must be deleted or anonymised
- How customer privacy requests must be handled
- How international transfers must be governed
- What customer and Owner interfaces must eventually provide

This approval does not select an AWS Region, identity provider, legal entity role or international-transfer mechanism.

##### Identity-Data Classifications

| Classification | Examples | Required treatment |
|---|---|---|
| `PROHIBITED_PERSISTENCE` | Raw passwords, passkey private keys, raw TOTP codes, raw recovery codes and raw reset links | Must never enter ordinary LinkCraftor storage, logs or analytics |
| `RESTRICTED_CREDENTIAL` | Password verifier, encrypted TOTP seed, recovery-code hash, refresh-token reference and SCIM secret | Provider-controlled or strongly encrypted with narrowly restricted access |
| `RESTRICTED_IDENTITY` | Email, name, Google issuer and subject, passkey credential ID and public key | Personal data subject to purpose, region, access and retention controls |
| `SECURITY_TELEMETRY` | IP address, device information, login history and risk signals | Security use only with limited justified retention |
| `AUTHORIZATION_DATA` | Principal ID, workspace membership, role and entitlement | Canonical LinkCraftor authorization data |
| `SECURITY_EVIDENCE` | Recovery case, authenticator change, suspicious login and administrative action | Tamper-resistant, access-controlled and retention-governed |
| `ANONYMISED_METRICS` | Irreversibly aggregated capacity and security statistics | May be retained longer only when re-identification is not reasonably possible |

Classification must be applied before production storage is authorized.

Unknown identity data must default to the more restrictive applicable classification.

##### Prohibited Identity Data

Ordinary LinkCraftor systems must never persist:

- Raw customer passwords
- Passkey private keys
- Biometric templates
- Raw TOTP verification codes
- Plaintext TOTP seeds
- Raw recovery-code values after initial display
- Raw verification links
- Raw password-reset links
- Raw account-recovery links
- Reusable session tokens in logs
- OAuth authorization codes in logs
- Google ID tokens in analytics
- Unredacted authentication headers
- Secret-bearing query strings

Crash reports, session-replay tools, observability pipelines and customer-support interfaces must enforce the same prohibition.

##### Canonical Data Ownership

LinkCraftor owns the canonical authority for:

- Immutable `principal_id`
- Account status
- Workspace membership
- Roles and permissions
- Product entitlements
- Provider-to-principal mappings
- Consent and privacy-notice versions
- Session-security metadata
- Security-event history
- Recovery and containment state
- Customer security preferences

The selected identity provider may own protected authentication material such as:

- Password verifier
- Provider-managed passkey public credentials
- Provider-managed TOTP secret
- Provider-issued authentication tokens
- Provider authentication records

Google remains an external identity provider.

The Google authentication scope remains limited to:

- `openid`
- `email`
- `profile`

Google Drive, Gmail, Contacts, Calendar and unrelated Google content remain outside the authentication scope.

AWS IAM must not become the owner of customer identities.

Billing may retain legally required billing records under its own authority. It must not become the authentication authority.

##### Data Minimisation

LinkCraftor may collect only information required for:

- Authentication
- Account security
- Workspace membership
- Product access
- Billing linkage
- Legal notices and consent evidence
- Fraud and account-takeover prevention
- Support
- Account recovery
- Regulatory compliance

The MVP must not require:

- Phone number
- Government identification
- Date of birth
- Home address
- Biometric templates
- Google Drive content
- Gmail content
- Unrelated social-profile information

Optional profile fields must be clearly identified and must not silently become authentication requirements.

Passkey biometric comparison must remain on the customer's device or authenticator. LinkCraftor receives the cryptographic result and must not collect the fingerprint or facial image.

Identity and authentication data must not be used for advertising profiles or general AI-model training without:

- A separately documented purpose
- A lawful basis
- A privacy assessment
- Applicable customer notice or consent
- Security review
- Founder approval

##### Purpose and Transparency

Every identity-data category must have:

- Specific processing purpose
- Named data owner
- Controller and processor determination
- Lawful basis or other applicable legal justification
- Customer notice
- Required or optional status
- Recipients
- Region
- Retention period
- Deletion method
- Security classification

Legal basis must be reviewed for each jurisdiction. This architecture does not make a final legal determination.

Privacy notices must describe identity processing in clear language.

Notice and consent versions must be recorded with appropriate timestamps.

Withdrawal of optional consent must not disable processing that remains lawfully required for authentication, security, contract performance or legal obligations.

##### Region and Residency Model

Before production, every identity deployment must declare:

- `PRIMARY_IDENTITY_REGION`
- `SECURITY_EVIDENCE_REGION`
- `BACKUP_REGION`
- `DISASTER_RECOVERY_REGION`
- Support-access countries
- Provider processing locations
- Provider subprocessors
- Email-routing regions
- Notification-routing regions
- Analytics destinations
- Cross-border transfer mechanisms

The approved residency rules are:

- No silent cross-region replication.
- No optional analytics service may move identity data to another Region without review.
- Backups remain subject to the same classification and residency controls.
- Disaster-recovery replicas require documented approval.
- Remote administrative access from another country must be recorded as international access where applicable.
- Enterprise residency promises must not be offered until technically and contractually supported.
- Region changes require migration, security, privacy and customer-impact review.
- Provider regional claims must be verified against optional features and subprocessors.

LinkCraftor must not choose an AWS Region through R7.

The AWS Region decision remains part of the general AWS architecture dependency assessment.

##### Provider Regional Behaviour

Every provider candidate must document:

- Region in which the primary customer profile is stored
- Backup locations
- Replication behaviour
- Failover data flows
- Email-routing locations
- SMS-routing locations if ever enabled
- Analytics-routing locations
- Support-access locations
- Subprocessor locations
- Deletion propagation
- Export and migration behaviour

A regional user directory must not be assumed to keep every optional feature within the same Region.

Any candidate feature that exports identity events to a different Region must be disabled by default until approved.

##### International-Transfer Governance

LinkCraftor must maintain an international-transfer register containing:

- Data category
- Source country or Region
- Destination country or Region
- Controller
- Processor
- Subprocessor
- Purpose
- Legal mechanism
- Encryption controls
- Access controls
- Retention
- Transfer-risk assessment
- Approval
- Review date

Where applicable, an international transfer must use a valid mechanism such as:

- Adequacy decision
- Standard Contractual Clauses
- UK International Data Transfer Agreement
- Approved UK addendum
- Another applicable statutory or contractual safeguard

International access must not be treated as harmless merely because the data remains physically stored in its original Region.

Ghanaian processing must be assessed under the Data Protection Act, 2012 (Act 843), including applicable controller or processor registration obligations.

EU, UK, United States, Ghana and other relevant jurisdictional requirements must be recorded before production processing is authorized.

##### Identity-Data Security

All identity personal data must be protected through:

- Encryption in transit
- Encryption at rest
- Approved key management
- Least-privilege access
- Separation of duties
- Administrative step-up
- Access logging
- Secret redaction
- Environment separation
- Backup encryption
- Secure deletion
- Regular access review
- Provider security assessment
- Incident response
- Recovery testing

Highly sensitive fields must use field-level or envelope encryption where LinkCraftor controls storage and the risk requires it.

Encryption keys must remain logically separated from encrypted data.

Key management must include:

- Restricted administration
- Rotation
- Revocation
- Usage evidence
- Environment separation
- Backup
- Recovery
- Emergency-access controls

No employee, engineer, support operator or Owner Console user may view credential secrets merely because they can access an administrative interface.

##### Approved Default Retention Schedule

The approved architectural defaults are:

| Identity record | Default retention |
|---|---|
| Unverified signup | 30 days after creation |
| Active principal and profile | While account remains active |
| Principal or profile after approved deletion | Delete or anonymise from primary systems within 30 days |
| Password verifier | Only while the password method remains active |
| Active passkey credential record | While the passkey remains registered |
| Removed passkey public credential | Delete within 30 days while retaining only the required security event |
| TOTP seed | Only while the method remains active; delete when disabled |
| Recovery-code hashes | Until used, regenerated or account deleted |
| Verification, reset or recovery token hash | Until used, replaced or expired; operational purge within 24 hours |
| Active session record | While the session remains valid |
| Expired or revoked session metadata | 30 days |
| Raw IP and detailed device-security data | 90 days |
| Authentication and security-event metadata | 13 months |
| High-severity investigation evidence | 24 months after case closure |
| Support-assisted recovery case | 24 months after closure |
| Workspace invitation metadata | Pending period plus 90 days after terminal state |
| Consent and legal-notice acceptance | Account lifetime plus up to 7 years where legally justified |
| Encrypted backups containing identity data | Maximum 90-day rolling retention |
| Minimal deletion or security tombstone | Up to 13 months where required for fraud or deletion enforcement |
| Irreversibly anonymised aggregate metrics | May be retained without a fixed personal-data period |

These periods may be changed only when supported by:

- Applicable law
- Approved contract
- Documented security need
- Legal hold
- Privacy assessment
- Formal approval

Identity data must not be retained indefinitely merely because storage is inexpensive.

##### Automated Retention Enforcement

Every identity-data category must record:

- Named owner
- Purpose
- Classification
- System of record
- Region
- Retention trigger
- Retention period
- Deletion method
- Legal-hold behaviour
- Review frequency
- Evidence requirements

Automated retention processes must:

- Identify eligible records
- Respect approved legal holds
- Delete or anonymise records
- Prevent cross-tenant deletion
- Produce non-secret evidence
- Retry safely
- Alert on failure
- Be periodically tested
- Remain idempotent where possible
- Avoid restoring expired credentials

A failed retention process must create an operational and privacy alert.

R7 approves the policy only. It does not authorize a retention job to run.

##### Account-Deletion Journey

The approved customer account-deletion journey is:

1. The customer requests deletion.
2. LinkCraftor requires step-up authentication.
3. The frontend explains workspace, billing, plugin and data consequences.
4. Sole Owners must transfer or close their workspaces.
5. Active sessions and refresh authority are revoked.
6. New authentication is blocked.
7. Provider credentials are deleted or disabled.
8. Primary identity data is deleted or anonymised within 30 days.
9. Provider deletion is verified.
10. Backups expire within the approved 90-day window.
11. A deletion ledger prevents restored backups from resurrecting the account.
12. Completion is communicated where possible.

Account deletion must not:

- Delete another member's personal data
- Destroy shared workspace business records unlawfully
- Remove records owned by the billing or tax authority boundary
- Erase active legal-hold evidence
- Conceal a security incident
- Leave reusable credentials active
- Remove another workspace's membership records incorrectly
- Reassign ownership silently

Where records must remain, they must be:

- Minimized
- Isolated
- Access restricted
- Purpose limited
- Retention limited
- Included in the applicable privacy notice

##### Backup Deletion and Restoration

Individual identity records may not be immediately editable inside immutable backups.

The approved rules are:

- Identity-bearing backup retention is capped at 90 days.
- Deleted identities must not return to active use after restoration.
- A deletion ledger must be reapplied after every restore.
- Restored sessions and reusable credentials remain invalid.
- Backup access requires privileged approval.
- Restore operations generate security and privacy evidence.
- Expired backup media must be securely destroyed.
- Backup copies must preserve original classification and residency metadata.

A restore must not silently reverse:

- Account deletion
- Credential revocation
- Session revocation
- Membership removal
- Security containment
- Legal restrictions

##### Customer Privacy Rights

Where applicable, LinkCraftor must support:

- Access
- Correction
- Export
- Deletion
- Restriction
- Objection
- Consent withdrawal
- Complaint submission
- Human review of qualifying automated decisions

Privacy requests must:

- Be identity-verified proportionately
- Offer a controlled alternative when the normal authenticator is unavailable
- Avoid disclosing another person's data
- Avoid exposing confidential abuse-detection logic
- Follow applicable jurisdictional deadlines
- Produce auditable evidence
- Be communicated clearly
- Be tracked to completion

Exports must be structured and machine-readable where required.

Privacy-request verification must not become an uncontrolled recovery bypass.

##### Customer Privacy and Security Centre

The customer frontend must include:

**Privacy Overview**

- Identity-data categories held by LinkCraftor
- Purpose of each category
- Connected identity providers
- Region summary where available
- Retention summary
- Current privacy notice
- Notice and consent versions
- Relevant subprocessor information

**Customer Controls**

- Download identity and account data
- Correct profile information
- Change primary email through step-up
- Review Google connection
- Review passkeys and MFA
- Review active sessions
- Withdraw optional consent
- Request account deletion
- View deletion progress
- Submit a privacy request
- Report suspected misuse

**Deletion Interface**

- Clear consequences
- Workspace-ownership warning
- Connected WordPress installation warning
- Subscription impact
- Data scheduled for deletion
- Data that may lawfully remain
- Step-up challenge
- Final confirmation
- Pending state
- Completion state
- Route for reporting an unauthorized deletion request

The frontend must not claim deletion is complete until LinkCraftor and applicable provider workflows have reached the approved completion state.

The frontend must be responsive, keyboard accessible and screen-reader compatible.

##### Owner Control Tower Privacy UI

The future Owner Control Tower privacy view must include:

- Identity-data inventory
- Data classification
- Systems of record
- Processing purposes
- Primary and replica Regions
- Provider register
- Subprocessor register
- International-transfer register
- Retention schedule
- Retention-job status
- Deletion queue
- Failed deletions
- Backup-expiry status
- Privacy-request queue
- Legal holds
- Exceptional access
- Privacy incidents
- Provider-deletion verification
- Data-location drift alerts
- Registration and agreement status

Administrative interfaces must mask personal data unless full access is necessary and authorized.

Every reveal of restricted identity information must be justified and auditable.

##### Privacy Security Events

The authoritative event model must include:

- `privacy_request_received`
- `privacy_request_verified`
- `privacy_export_started`
- `privacy_export_completed`
- `privacy_correction_completed`
- `account_deletion_requested`
- `account_deletion_cancelled`
- `account_deletion_started`
- `account_deletion_completed`
- `provider_deletion_requested`
- `provider_deletion_verified`
- `retention_job_started`
- `retention_job_completed`
- `retention_job_failed`
- `legal_hold_applied`
- `legal_hold_released`
- `backup_deletion_completed`
- `restored_deletion_reapplied`
- `international_transfer_approved`
- `exceptional_identity_data_accessed`
- `privacy_incident_opened`

Privacy evidence must not contain the credential or secret value that the event concerns.

##### Cross-Architecture Integration Contract

R7 must later integrate with:

- Universal Data Architecture
- Security Data Asset Inventory
- Security Architecture
- Universal Runtime
- Observability
- SupportOps
- Billing
- Backup and Disaster Recovery
- Owner Control Tower

Every identity data asset must eventually receive canonical inventory metadata covering:

- Security data identifier
- Data owner
- Classification
- Purpose
- System of record
- Region
- Replication
- Controller
- Processor
- Subprocessor
- Retention
- Deletion
- Encryption
- Access controls
- Evidence state

This section defines the future contract only.

The deferred integration gate remains deferred.

No architecture integration is executed by approving R7.

##### Provider-Selection Requirements

Every identity-provider candidate must disclose or support:

- User-profile storage Region
- Backup locations
- Replication locations
- Optional-feature data flows
- Subprocessors
- Encryption
- Export
- Correction
- Deletion
- Deletion verification
- Retention controls
- DPA availability
- International-transfer safeguards
- Security-event access
- Incident-notification commitments
- Enterprise residency options
- Support-access locations
- Provider-exit and migration

A provider that cannot explain where identity data is stored or how identity data is deleted cannot pass provider evaluation.

##### Legal and Standards Basis

Implementation and provider evaluation must consider the applicable current versions of:

- Ghana Data Protection Act, 2012 (Act 843)
- EU General Data Protection Regulation where applicable
- UK data-protection requirements where applicable
- Applicable United States federal and state privacy requirements
- Applicable customer and enterprise contractual requirements
- LinkCraftor Security Architecture
- Universal Data Architecture
- Security Data Asset Inventory requirements

Requirements must be revalidated with qualified legal and privacy advice before production.

This architecture is not final legal advice and does not independently establish regulatory compliance.

##### Approval Limitation

This approval defines identity-data classification, location, privacy, retention and deletion requirements.

It does not:

- Select Cognito or another provider
- Select an AWS Region
- Create an identity database
- Move customer data
- Delete a customer account
- Register LinkCraftor with a regulator
- Sign a DPA or transfer agreement
- Configure encryption keys
- Run a retention job
- Create a privacy export
- Implement the frontend
- Execute the deferred integration gate
- Constitute final legal advice
- Complete Phase 2.1

<!-- PHASE_2_ITEM_2_1_APPROVED_AWS_ARCHITECTURE_DEPENDENCIES -->

#### Approved General AWS Architecture Dependency Contract

- Requirement status: `APPROVED`
- Requirement ID: `2.1-R8`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`
- General AWS architecture status: `INCOMPLETE`
- Provider dependency: `PROVIDER_NEUTRAL`
- Provider decision: `NOT_APPROVED`
- AWS Region decision: `NOT_SELECTED`
- AWS deployment authorization: `NONE`
- AWS-account creation authorization: `NONE`
- DNS-change authorization: `NONE`
- TLS-certificate authorization: `NONE`
- Datastore-deployment authorization: `NONE`
- KMS-key deployment authorization: `NONE`
- Secret-storage authorization: `NONE`
- SES configuration authorization: `NONE`
- Google configuration authorization: `NONE`
- Infrastructure-as-code deployment authorization: `NONE`
- Requirements-continuation gate: `PASS`
- Provider-decision gate: `CONDITIONAL`
- Implementation gate: `BLOCKED`
- Production gate: `BLOCKED`
- Integration-gate status: `DEFERRED`

##### Purpose

This contract defines what the Identity, Access and Account Security architecture requires from the unfinished general AWS architecture.

It does not claim that the AWS architecture is complete.

It allows requirements work, provider comparison and cost assessment to continue without pretending that the required AWS foundation already exists.

No identity implementation or production deployment may begin merely because this contract has been approved.

##### Separate Authorities

The following authorities must remain separate:

| Authority | Responsibility |
|---|---|
| Selected managed identity provider | Password verification, federated authentication, managed authenticators and provider-issued authentication assertions |
| LinkCraftor identity and authorization domain | Principals, provider bindings, workspaces, memberships, roles, entitlements, application sessions, recovery state and security policy |
| AWS IAM | Workforce and workload access to AWS resources |
| Google | External Google identity assertion within the approved authentication scope |

Customer identities must never be represented as AWS IAM users.

AWS IAM roles, users, policies and workload identities must not become the customer authentication authority.

LinkCraftor must translate a verified authentication assertion into its own immutable principal and authorization context.

##### Dependency-Gate Model

| Gate | Status | Meaning |
|---|---|---|
| Gate A — Requirements continuation | `PASS` | R9 provider comparison and R10 cost assessment may continue while the general AWS architecture is unfinished |
| Gate B — Final provider decision | `CONDITIONAL` | A provider may be approved only after its AWS account, Region, domain, passkey RP ID, email, secret, logging, capacity, backup, disaster-recovery and cost assumptions are documented |
| Gate C — Implementation | `BLOCKED` | No provider, runtime or supporting AWS infrastructure may be implemented until the required AWS foundations exist and a provider is explicitly approved |
| Gate D — Production | `BLOCKED` | Production requires both AWS and identity controls, quotas, monitoring, recovery, load testing, legal readiness and incident readiness |

Provider comparison does not require AWS resources to exist.

Provider implementation does require the applicable AWS foundation to exist.

##### AWS Account and Environment Foundation

Before implementation, the general AWS architecture must define:

- AWS Organization ownership
- Production, staging and development account separation
- Security and central-log account strategy
- Root-account protection
- Workforce administrator identity
- Service control policies
- Approved AWS Regions
- Central audit logging
- Emergency and break-glass access
- Billing ownership and cost controls
- Resource ownership and tagging
- Environment promotion rules

Production identity infrastructure must not be created in a personal, temporary or ungoverned AWS account.

Development credentials must not grant production identity access.

##### Region and Residency Inputs

The general AWS architecture must provide or approve:

- Primary application Region
- Primary identity Region
- Security-evidence Region
- Backup Region
- Disaster-recovery Region
- Permitted processing Regions
- International-transfer restrictions
- Enterprise residency commitments
- Service availability by Region
- Region-dependent cost assumptions

R8 does not select a Region.

The selected Region must satisfy the R7 privacy, residency, retention and transfer requirements.

##### Stable Authentication Domain

The conceptual authentication boundary is:

- `auth.linkcraftor.com`

This is a conceptual reservation only.

No DNS record, certificate, hosted zone or provider custom domain is created by this approval.

Before implementation, the architecture must approve:

- Final authentication hostname
- Environment-specific authentication hostnames
- OAuth and OIDC redirect URIs
- Sign-out URIs
- Allowed web origins
- Passkey relying-party ID
- Domain migration procedure
- Domain takeover protection
- Certificate ownership and renewal

The final passkey relying-party ID must be stable before passkey enrollment begins.

Hostinger-hosted marketing or PHP pages may redirect customers to the authentication boundary.

Hostinger must not collect, process, proxy, log or store LinkCraftor passwords, passkey material, TOTP secrets, recovery codes, OAuth authorization codes or session tokens.

##### DNS and TLS Dependencies

The general AWS architecture must define:

- Authoritative DNS ownership
- DNS change approval
- TLS certificate issuance
- Certificate renewal monitoring
- Certificate revocation
- Failover behaviour
- Subdomain takeover protection
- DNS security and audit evidence

Route 53, AWS Certificate Manager and CloudFront remain candidates only.

If Amazon Cognito custom domains are evaluated, the current requirement for the associated ACM certificate in `us-east-1` because of the CloudFront dependency must be revalidated before implementation.

##### Edge and Network Dependencies

The general AWS architecture must determine whether the identity boundary requires:

- AWS WAF
- AWS Shield
- CloudFront
- API Gateway
- Application Load Balancer
- VPC integration
- Private service connectivity
- Egress restrictions
- DDoS protection
- Bot management
- Edge rate limiting
- Health checking
- Regional or cross-Region failover

No edge or network service is selected by R8.

The final design must support the R6 authentication-capacity targets and the authentication-abuse controls defined by this domain.

##### Identity Runtime Dependencies

The LinkCraftor identity runtime must eventually provide:

- Identity-provider adapter
- OAuth and OIDC callbacks
- Token and assertion validation
- Principal resolution
- Application-session management
- Authorization-context construction
- Recovery workflow coordination
- Security-event production
- Customer security APIs
- Owner security-operation APIs

The general AWS architecture must select the applicable compute platform.

Lambda, ECS, EKS and EC2 remain candidates only.

Authentication decisions, token validation and authorization decisions are synchronous security operations.

They must not depend on the successful completion of an asynchronous queue.

The Universal Runtime may process asynchronous notification, audit, retention and deletion work, but it must not become the authority that approves a login.

##### Canonical Identity Datastore Dependency

The general data and AWS architectures must select and govern the datastore for:

- Principals
- Provider bindings
- Workspace memberships
- Roles and permissions
- Entitlements
- Invitations
- Application sessions
- Security events
- Recovery and containment state
- Privacy state
- Deletion ledger

No database technology is selected by R8.

The selected datastore must support:

- Encryption
- Least privilege
- Availability
- Conditional and atomic updates
- Backup and restore
- Retention enforcement
- Deletion propagation
- Capacity targets
- Auditability
- Regional requirements

##### Key and Secret Management Dependencies

The general AWS architecture must define:

- KMS key ownership
- Key administration separation
- Key rotation
- Key recovery and revocation
- Region-specific key requirements
- AWS Secrets Manager or equivalent secret authority
- Secret rotation
- Emergency secret replacement
- Secret-access evidence

Protected material may eventually include:

- Google OAuth client secret
- Enterprise OIDC secrets
- SAML signing or encryption material
- SCIM bearer secrets
- Email-provider credentials
- Webhook secrets
- Database credentials
- Provider-management credentials

Secrets must never be committed to source control, embedded in frontend code or written to logs.

No key or secret is created by R8.

##### Transactional Email Dependency

Amazon SES remains a candidate only.

Before implementation, the AWS and identity architectures must define:

- Sending-domain ownership
- SPF
- DKIM
- DMARC
- Bounce handling
- Complaint handling
- Suppression handling
- Sending quotas
- Region availability
- Sandbox-exit requirements
- Delivery monitoring
- Template ownership
- Abuse containment
- Failover behaviour

SMS and voice OTP remain disabled for the MVP.

No SES identity, domain, configuration set or sending authorization is created by R8.

##### Google Authentication Dependency

Before Google authentication is implemented, the architecture must approve:

- Google Cloud project ownership
- Environment separation
- OAuth consent-screen ownership
- Exact redirect URIs
- Exact JavaScript origins
- Authentication domain
- Client-secret storage
- Secret rotation
- Incident revocation
- Approved scopes

A personal Google Cloud project must not own production authentication.

The authentication scope remains limited to:

- `openid`
- `email`
- `profile`

No Google project or OAuth credential is created by R8.

##### Logging and Security-Evidence Dependencies

The AWS architecture must provide an approved route for:

- AWS control-plane audit events
- Authentication events
- Administrative identity changes
- Authorization denials
- Recovery events
- Suspicious-login events
- Provider failures
- WAF and edge events
- Email delivery failures
- Backup and restore evidence
- Retention and deletion evidence

CloudTrail, CloudWatch, S3, Security Lake, EventBridge and an external SIEM remain candidates only.

Logs must exclude passwords, private keys, TOTP secrets, raw recovery codes, raw tokens, OAuth authorization codes and secret-bearing URLs.

Logging failure must produce monitoring and containment behaviour; it must not silently erase required evidence.

##### Event and Queue Dependencies

EventBridge, SQS, SNS and the Universal Runtime remain candidates for asynchronous identity work.

Identity events must be:

- Durable where required
- Idempotent
- Versioned
- Traceable
- Redacted
- Replay-safe
- Retention-governed
- Protected from unauthorized producers and consumers

Queues must not contain reusable credentials.

Queue failure must not cause a login to be approved.

##### Capacity and Quota Dependencies

The general AWS architecture must incorporate the approved R6 targets:

- 25,000 concurrent authenticated sessions
- Growth to 100,000 sessions without identity redesign
- 100 sustained login starts per second
- 250 burst login starts per second
- 5,000 sustained token validations per second
- 10,000 burst token validations per second

Capacity evaluation must include:

- Identity-provider quotas
- Federation quotas
- Recovery quotas
- Email quotas
- WAF and edge limits
- Runtime concurrency
- Datastore capacity
- Event throughput
- Log-ingestion capacity
- Backup and restore capacity

No quota request, reservation, provisioned capacity purchase or load test is authorized by R8.

##### Backup and Disaster-Recovery Dependencies

The general AWS architecture must define:

- Encrypted backup authority
- R7 maximum backup-retention period of 90 days
- Recovery point objective
- Recovery time objective
- Regional recovery model
- Deletion-ledger replay
- Deleted-account handling in restored data
- Session invalidation after recovery
- DNS failover
- Provider failover
- Restore testing
- Recovery evidence

Backups must not silently restore deleted credentials or reactivate deleted accounts.

Disaster-recovery design must preserve the separation between provider authentication and LinkCraftor authorization.

##### Amazon Cognito Multi-Region Candidate Observation

Amazon Cognito User Pools remains only a leading candidate.

Its current multi-Region resilience capability must be revalidated during R9 and again before implementation.

The observed constraints include:

- Applicable feature-tier requirements
- Customer-managed multi-Region key requirements
- A primary Region and one secondary Region
- Secondary-Region limitations for signup, password reset and profile operations
- TOTP limitations in the secondary Region
- Prior-primary-sign-in requirements affecting some federated users
- Failed-attempt counters that may not be synchronized between Regions

These observations do not approve Cognito or its multi-Region feature.

The provider comparison must determine whether these constraints satisfy LinkCraftor's recovery, security, user-experience and cost requirements.

##### Infrastructure-as-Code Dependency

Terraform, AWS CDK and CloudFormation remain candidates only.

Before implementation, the selected infrastructure-as-code process must provide:

- Code review
- Protected state
- Secret exclusion
- Change preview
- Approval controls
- Environment separation
- Drift detection
- Rollback
- Resource tagging
- Evidence retention

No infrastructure-as-code platform is selected or executed by R8.

##### Inputs Required from the General AWS Architecture

The identity architecture requires:

- Governed AWS accounts
- Approved Regions
- DNS and certificate ownership
- Compute platform
- Network and edge pattern
- Datastore pattern
- KMS and secret-management pattern
- Email-delivery pattern
- Logging and monitoring pattern
- Backup and disaster-recovery pattern
- Infrastructure-as-code pattern
- Cost and quota ownership
- Incident-response integration

##### Outputs Supplied by the Identity Architecture

This domain supplies:

- Identity trust boundaries
- Authentication journeys
- Assurance levels
- MFA and passkey requirements
- Recovery requirements
- Authorization ownership
- Session requirements
- Privacy and retention rules
- Capacity targets
- Security-event requirements
- Customer UI requirements
- Owner security-operation requirements
- Provider-evaluation criteria

The general AWS architecture must host and protect these requirements without taking ownership of customer credentials or application authorization.

##### Frontend UI Design

The customer authentication interface must use a stable, branded LinkCraftor authentication boundary.

The UI must:

- Keep AWS implementation details hidden from customers
- Never expose AWS access keys, secrets, Regions or internal resource identifiers
- Send authentication requests only through approved identity interfaces
- Preserve environment separation
- Use exact approved callback and redirect destinations
- Support the previously approved email/password and Google journeys
- Support the previously approved MFA, passkey, recovery and step-up journeys
- Present neutral error messages that do not disclose whether an account exists
- Show service interruption and retry states safely
- Provide accessible and responsive layouts
- Link customers to the Customer Security Centre after authentication

The conceptual `auth.linkcraftor.com` boundary must not be displayed as operational until DNS, TLS, provider and security readiness have been validated.

##### Owner Control Tower AWS Readiness UI

The Owner Console must eventually provide a read-only readiness view for:

- AWS account foundation
- Environment separation
- Approved Regions
- Authentication domain
- DNS status
- Certificate status
- Passkey relying-party ID
- Identity-provider status
- Runtime status
- Datastore status
- KMS status
- Secret-management status
- Email status
- Quota status
- Logging status
- Backup status
- Disaster-recovery status
- Load-test status
- Cost status
- Production blockers

The interface must distinguish:

- `NOT_SELECTED`
- `NOT_STARTED`
- `BLOCKED`
- `IN_PROGRESS`
- `READY`
- `FAILED`
- `DEFERRED`

Readiness display must not expose secret values or grant deployment authority.

##### Approval Limitation

This approval does not:

- Complete the general AWS architecture
- Approve an identity provider
- Select an AWS Region
- Create an AWS account
- Create AWS resources
- Reserve or configure DNS
- Issue a certificate
- Configure Google authentication
- Configure SES
- Create KMS keys
- Store secrets
- Select or create a database
- Enable Cognito multi-Region resilience
- Select an infrastructure-as-code platform
- Perform integration
- Authorize implementation
- Authorize production

The Phase 1 integration gate remains deferred.

<!-- PHASE_2_ITEM_2_1_APPROVED_MANAGED_IDENTITY_PROVIDER_COMPARISON -->

#### Approved Managed Identity-Provider Comparison

- Requirement status: `APPROVED`
- Requirement ID: `2.1-R9`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`
- Comparison observation date: `2026-11-03`
- Comparison validity: `POINT_IN_TIME_REVALIDATION_REQUIRED`
- Provider decision: `NOT_APPROVED`
- Selected provider: `NONE`
- Leading candidate: `AMAZON_COGNITO_USER_POOLS_PLUS`
- Alternative finalist: `AUTH0_B2B_OR_ENTERPRISE`
- Reserve candidate: `WORKOS_AUTHKIT`
- Reserve-candidate status: `DUE_DILIGENCE_HOLD`
- Microsoft Entra External ID outcome: `NOT_ADVANCED`
- Clerk outcome: `NOT_ADVANCED`
- Provider-account authorization: `NONE`
- Subscription-purchase authorization: `NONE`
- SDK-installation authorization: `NONE`
- Customer-migration authorization: `NONE`
- AWS deployment authorization: `NONE`
- DNS-change authorization: `NONE`
- Integration-gate status: `DEFERRED`
- Implementation gate: `BLOCKED`
- Production gate: `BLOCKED`

##### Purpose

This requirement records a point-in-time comparison of managed customer-identity providers against the approved LinkCraftor identity, security, privacy, scale, enterprise and frontend requirements.

Approval of this comparison does not approve, purchase or deploy any provider.

Provider capabilities, limits, pricing, security posture and contractual terms must be revalidated during R10 and again before implementation.

##### Evaluation Principles

The comparison follows these rules:

- LinkCraftor remains the canonical authority for principals, workspaces, memberships, roles, permissions and entitlements.
- A managed identity provider verifies authentication factors and issues authentication assertions.
- AWS IAM remains limited to workforce and workload access to AWS.
- Customer identities must never become AWS IAM users.
- Provider-native organizations must not replace LinkCraftor workspace authority.
- Provider-native threat protection is one security layer, not LinkCraftor's complete account-takeover authority.
- Provider marketing claims do not satisfy architectural gates without documented technical and contractual evidence.
- A provider must meet the approved R6 scale targets with headroom.
- A provider must satisfy the R7 privacy, residency, retention and deletion requirements.
- Cost is not finalized in R9.
- No provider may be selected before R10 and explicit Founder approval.

##### Mandatory Provider Gates

A provider cannot receive final approval unless it demonstrates:

1. Email and password signup and login.
2. Google signup and login.
3. Email verification.
4. User-verifying passkeys.
5. TOTP MFA.
6. Recovery codes or an approved equivalent.
7. Safe account recovery.
8. Step-up authentication.
9. Brute-force protection.
10. Credential-stuffing protection.
11. Account-takeover risk signals.
12. Account containment and session revocation.
13. Account-enumeration-resistant responses.
14. Custom authentication-domain support.
15. Standards-based OAuth 2.0 and OpenID Connect.
16. Local JWT validation.
17. Security-event export.
18. R6 capacity and approved headroom.
19. R7 privacy, residency and deletion compliance.
20. Enterprise SAML or OIDC federation.
21. An approved SCIM or enterprise-lifecycle path.
22. Provider migration and exit procedures.
23. Backup and disaster-recovery compatibility.
24. Contractual availability and incident support.
25. Provider-neutral frontend integration.

A missing hard gate requires either:

- A documented compensating LinkCraftor control
- A contractual provider commitment
- Explicit architectural acceptance of the residual risk

##### Comparison Outcome

| Provider | R9 classification | Principal strengths | Principal conditions or blockers |
|---|---|---|---|
| Amazon Cognito User Pools Plus | `FINALIST_LEADING_CANDIDATE_NOT_APPROVED` | Strong AWS alignment, regional user pools, Google federation, passkeys, TOTP, adaptive authentication, compromised-credential detection and event export | Quota increases, WAF, full LinkCraftor account-takeover controls, custom Security Centre, enterprise lifecycle path and multi-Region limitations |
| Auth0 B2B or Enterprise | `FINALIST_NOT_APPROVED` | Mature CIAM, attack protection, adaptive MFA, enterprise federation, Organizations, inbound SCIM and regional deployment choices | Appropriate capacity tier, cost, passkey login-page limitations, residency contract and external-provider operational dependency |
| WorkOS AuthKit | `RESERVE_DUE_DILIGENCE_HOLD` | Passwords, social login, passkeys, TOTP, organizations, enterprise SSO and Directory Sync | Open security-incident review as observed on the comparison date, residency review, contractual capacity confirmation and hosted passkey-management limitations |
| Microsoft Entra External ID | `NOT_ADVANCED_CURRENT_CONSTRAINTS` | Google federation, passkeys, external-tenant security and enterprise identity capabilities | Documented tenant request limit conflicts with the approved R6 burst target unless Microsoft provides an approved capacity arrangement |
| Clerk | `NOT_ADVANCED_CURRENT_CONSTRAINTS` | Strong developer experience, passkeys, MFA, organizations, SSO and frontend components | No present regional residency selection, enterprise-residency concerns and required capacity and recovery confirmation |

##### Amazon Cognito User Pools Plus Assessment

Amazon Cognito User Pools with the Plus feature plan remains the leading candidate because it aligns most directly with the planned AWS environment.

The Plus plan is the evaluated plan because the approved architecture requires:

- Adaptive authentication
- Compromised-credential detection
- Authentication-event export
- Passkeys
- Managed or API-driven authentication
- Google federation
- TOTP MFA

The following conditions remain:

- Default quotas are not accepted as proof of R6 readiness.
- Required quota increases must be approved before load testing.
- AWS WAF or an equivalent edge control is required for volumetric abuse.
- Provider threat protection does not replace LinkCraftor account-takeover detection.
- Google-federated sessions still require LinkCraftor session and behavioural risk controls.
- LinkCraftor must own workspaces, memberships, roles and entitlements.
- A customer-facing Security Centre must be built by LinkCraftor.
- Multi-Region limitations must be accepted or mitigated.
- Provider export and migration limitations must be evaluated.
- Cognito Plus pricing and supporting AWS costs must be calculated in R10.

Cognito remains a candidate and is not approved for deployment.

##### Auth0 B2B or Enterprise Assessment

Auth0 advances as the formal alternative finalist because it provides strong customer-identity and enterprise capabilities.

Its evaluated strengths include:

- Brute-force protection
- Suspicious-IP throttling
- Bot detection
- Breached-password detection
- Adaptive MFA
- Passkeys
- Organizations
- Enterprise connections
- Inbound SCIM
- Custom domains
- Public and private deployment choices

The following conditions remain:

- The selected plan must contractually satisfy the R6 capacity targets.
- Required high-capacity or private-cloud pricing must be included in R10.
- Passkey dependence on the supported Universal Login experience must be assessed against the LinkCraftor frontend design.
- Regional storage and failover terms must satisfy R7.
- LinkCraftor must not surrender workspace authorization to Auth0 Organizations.
- Provider exit, user export and credential-migration limitations must be documented.
- Contractual availability, support and incident response must be priced.

Auth0 remains a finalist and is not approved for deployment.

##### WorkOS AuthKit Assessment

WorkOS AuthKit remains a reserve candidate because it offers a strong B2B-oriented feature set.

Its evaluated strengths include:

- Email and password authentication
- Social login
- Passkeys
- TOTP MFA
- Organizations
- Enterprise SSO
- Directory Sync
- Bot and abuse protection
- Provider-managed sessions

It is placed on `DUE_DILIGENCE_HOLD` because:

- A vendor security incident remained under investigation on the comparison date.
- The incident and its final remediation require review.
- Residency and international-transfer suitability require review.
- R6 capacity requires written confirmation.
- Hosted passkey self-service limitations require assessment.
- LinkCraftor's canonical workspace authority must be preserved.
- Pricing and contractual availability require R10 validation.

The hold is point-in-time and must be reviewed when authoritative incident information changes.

WorkOS is not approved for deployment.

##### Microsoft Entra External ID Assessment

Microsoft Entra External ID is not advanced to the primary R10 finalists at this time.

It provides relevant capabilities including:

- Google federation
- Passkeys
- External-tenant MFA
- Brute-force controls
- Conditional Access options
- Enterprise identity integration

Its documented external-tenant request ceiling does not presently demonstrate compliance with the approved R6 target of 250 burst login starts per second with headroom.

It may be reconsidered if Microsoft provides:

- An approved higher-capacity arrangement
- A satisfactory residency model
- A complete cost model
- Evidence that the full authentication journey satisfies R6

This is not a permanent vendor prohibition.

##### Clerk Assessment

Clerk is not advanced to the primary R10 finalists at this time.

It provides relevant capabilities including:

- Email and social authentication
- Passkeys
- TOTP MFA
- Backup codes
- Organizations
- Enterprise connections
- Bot protection
- Prebuilt frontend components

Its present lack of selectable regional data residency conflicts with the flexibility required by R7 and future enterprise residency commitments.

It may be reconsidered if:

- Regional data residency becomes available
- R6 capacity is contractually confirmed
- Enterprise recovery and security-event requirements are satisfied
- Provider exit and data-deletion controls are accepted

This is not a permanent vendor prohibition.

##### Approved R10 Candidate Set

R10 must perform the primary cost and high-availability comparison for:

1. Amazon Cognito User Pools Plus
2. Auth0 B2B or Enterprise

R10 must retain WorkOS AuthKit as a reserve cost benchmark while its due-diligence hold remains active.

Microsoft Entra External ID and Clerk do not require full R10 cost modelling unless their current blockers materially change.

##### Security-Control Composition

No provider will independently satisfy the complete LinkCraftor security architecture.

The final implementation must combine:

- Provider credential verification
- Provider MFA and passkey support
- Provider threat signals
- LinkCraftor principal resolution
- LinkCraftor session controls
- LinkCraftor workspace authorization
- LinkCraftor security-event correlation
- LinkCraftor account-takeover detection
- LinkCraftor containment decisions
- Edge rate limiting and bot controls
- Owner security operations
- Customer Security Centre controls

Provider threat protection must not be treated as the only account-takeover control.

Federated Google authentication must receive LinkCraftor session-risk monitoring even when the password is protected by Google.

##### Capacity Decision Rule

No provider receives final approval until its capacity evidence covers:

- 25,000 concurrent authenticated sessions
- Growth to 100,000 sessions without identity redesign
- 100 sustained login starts per second
- 250 burst login starts per second
- 5,000 sustained token validations per second
- 10,000 burst token validations per second
- Signup, recovery and refresh-storm targets
- At least the approved provider-capacity headroom

Local JWT validation must prevent ordinary LinkCraftor API requests from calling the identity provider.

Capacity approval may require:

- Quota increases
- Enterprise contract
- Reserved or provisioned capacity
- Private deployment
- Multi-Region design
- Load-test certification

No capacity request or purchase is authorized by R9.

##### Privacy and Residency Decision Rule

The final provider must disclose and contractually support:

- Primary identity-data location
- Replication locations
- Backup locations
- Disaster-recovery locations
- Support-access locations
- Subprocessors
- International-transfer mechanisms
- Security-event destinations
- Email-processing locations
- Deletion propagation
- Export and migration procedures

A provider cannot pass R7 merely because it advertises a regional endpoint.

Optional features, support access, logging, email and subprocessors must also be evaluated.

##### Enterprise Identity Rule

Enterprise SAML, OIDC and SCIM features must integrate with LinkCraftor workspace authority.

The provider may:

- Verify an enterprise identity
- Normalize provider attributes
- Receive provisioning events
- Supply federation metadata

LinkCraftor must remain responsible for:

- Workspace ownership
- Membership status
- Role assignment
- Entitlements
- Invitation acceptance
- Suspension
- Deprovisioning effects
- Authorization decisions
- Audit evidence

Provider organizations must not silently become the canonical LinkCraftor workspace registry.

##### Provider Migration and Exit Rule

Before final approval, each finalist must document:

- User export capabilities
- Password-verifier portability
- Passkey portability limitations
- TOTP migration limitations
- Social-identity mapping
- Enterprise-connection migration
- Session invalidation
- Recovery-state migration
- Security-event export
- Deletion verification
- Cutover strategy
- Rollback strategy
- Customer communication requirements

The architecture must assume that some credential material may not be portable.

Provider bindings must therefore be separated from LinkCraftor's immutable principal IDs.

##### Frontend UI Design

The frontend must remain provider-neutral.

The approved customer interface is:

- `/signup`
- `/login`
- `/verify-email`
- `/mfa`
- `/passkeys`
- `/step-up`
- `/recovery`
- `/security`
- `/security/sessions`
- `/security/history`

The interface must support:

- Email and password
- Continue with Google
- Passkey registration and login
- TOTP enrollment and verification
- Recovery-code display and regeneration
- Account recovery
- Step-up authentication
- Active-session review
- Session revocation
- Security-event review

Customer-facing pages must use LinkCraftor language and branding.

They must not expose:

- AWS implementation details
- Cognito terminology
- Auth0 terminology
- WorkOS terminology
- Provider tenant identifiers
- AWS Regions
- Client secrets
- Internal resource identifiers

The frontend must communicate through an approved LinkCraftor identity adapter.

Provider-specific SDK code must not be scattered across unrelated product pages.

If a provider requires a hosted authentication page for a capability, it must use:

- Approved custom domain
- Approved branding
- Approved redirect destinations
- Accessible interaction
- Secure OAuth authorization-code flow
- PKCE where applicable
- Account-enumeration-resistant errors

##### Owner Control Tower Provider-Evaluation UI

The Owner Console must eventually display:

- Candidate provider
- Evaluated plan
- Comparison status
- Evidence observation date
- Evidence expiry or revalidation status
- Required capabilities
- Passed gates
- Conditional gates
- Blocking gaps
- Regions
- Capacity limits
- Required quota increases
- Availability commitment
- Enterprise SSO status
- SCIM status
- Passkey status
- Threat-protection status
- Data-residency status
- Incident and due-diligence status
- Exit and migration status
- Estimated cost
- Final approval status

The interface must distinguish:

- `LEADING_CANDIDATE`
- `FINALIST`
- `RESERVE`
- `DUE_DILIGENCE_HOLD`
- `NOT_ADVANCED`
- `NOT_APPROVED`
- `APPROVED`
- `REVALIDATION_REQUIRED`

The interface must not expose provider secrets or grant deployment authority.

##### R10 Handoff

R10 must calculate provider, messaging, security and high-availability costs using explicit usage scenarios.

The calculation must include:

- Monthly active users
- Enterprise-federated users
- Enterprise connections
- SCIM or Directory Sync connections
- Authentication request capacity
- Quota increases
- Threat-protection tier
- Email delivery
- WAF and bot protection
- Logging and event export
- Data storage
- Backup
- Disaster recovery
- Multi-Region operation
- Contractual support
- Load testing
- Migration
- Incident-response support
- Applicable taxes and currency assumptions

R10 must separate:

- Required launch cost
- Growth cost
- Enterprise cost
- High-availability cost
- Optional future cost

##### Evidence Freshness

This comparison is a point-in-time architectural record dated `2026-11-03`.

Before final provider approval, R10 must revalidate:

- Feature availability
- Plan entitlements
- Pricing
- Quotas
- Regional availability
- Data residency
- SLA
- Security incidents
- Provider documentation
- Contractual terms

A stale comparison cannot authorize deployment.

##### Approval Limitation

This approval does not:

- Select a provider
- Approve Cognito
- Approve Auth0
- Approve WorkOS
- Purchase a subscription
- Create a provider tenant
- Create an AWS user pool
- Install an authentication SDK
- Configure Google OAuth
- Configure enterprise SSO
- Configure SCIM
- Configure DNS
- Issue a certificate
- Select a Region
- Request a quota increase
- Execute a load test
- Move customer data
- Integrate the runtime
- Authorize implementation
- Authorize production

The provider decision remains `NOT_APPROVED`.

The integration gate remains `DEFERRED`.

<!-- PHASE_2_ITEM_2_1_APPROVED_SIMPLIFIED_R10 -->

#### Approved Simplified Preliminary Cost and Availability Record

- Requirement ID: `2.1-R10`
- Status: `APPROVED`
- Approval date: `2026-11-03`
- Current architecture-created cost: `USD_0`
- New charges authorized: `NO`
- Budget approved: `NO`
- Provider selected: `NO`
- AWS identity Region selected: `NO`
- AWS or provider resources created: `NO`
- Runtime integration authorized: `NO`
- Frontend implementation authorized: `NO`

R10 is an architecture-planning record only. It is not an AWS bill, provider purchase, deployment authorization or production forecast.

Amazon Cognito remains a possible candidate, not an approved or deployed service. Auth0 and WorkOS also remain unapproved alternatives.

Exact pricing and capacity modelling are deferred until the general AWS architecture, deployment Regions, realistic traffic assumptions, provider quotations and availability design are ready.

The approved frontend authentication, security-status, outage, recovery and Owner cost-capacity interface requirements remain preserved for later implementation.

The final provider decision is deferred and requires separate founder approval.

<!-- PHASE_2_ITEM_2_1_FINAL_PROVIDER_GATE_DEFERRED -->

#### Approved Final Provider Decision Gate

- Gate outcome: `PROVIDER_DECISION_DEFERRED`
- Phase 2.1 architecture status: `COMPLETE`
- Selected provider: `NONE`
- Provider approval: `NONE`
- AWS identity Region: `NOT_SELECTED`
- New charges authorized: `NO`
- Resources created: `NO`
- Runtime integration: `DEFERRED`
- Frontend implementation: `DEFERRED`
- Production authorization: `BLOCKED`

Phase 2.1 requirements R1 through R10 are complete at the architecture level.

No identity provider is selected. Provider selection remains deferred until the AWS architecture, Regions, realistic traffic, quotations, capacity, availability and recovery evidence are ready.

This gate does not authorize Cognito, Auth0, WorkOS or another provider. It does not create infrastructure, approve spending, integrate runtime services or implement frontend interfaces.

Phase 2.2 may proceed while the provider-selection and integration gates remain deferred.

#### Deferred Work

The following work remains outside the completed Phase 2.1 architecture scope:

1. Select and approve an identity provider after the required evidence is available.
2. Complete runtime, data, AWS and frontend integration through their later approved gates.

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

<!-- PHASE_2_ITEM_2_2_PROVIDER_NEUTRAL_ARCHITECTURE -->

### 2.2 Provider-Neutral Architecture

- Item status: `IN_PROGRESS`
- Provider decision: `DEFERRED`
- Selected provider: `NONE`
- AWS deployment status: `NOT_STARTED`
- Runtime integration: `DEFERRED`
- Frontend implementation: `DEFERRED`

<!-- PHASE_2_ITEM_2_2_R1_APPROVED_AUTHORITY_BOUNDARY -->

#### Approved R1 — Provider-Neutral Authority Boundary

- Requirement ID: `2.2-R1`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

The identity provider may verify customer identity, protect credentials, issue authentication results and perform approved authentication-factor ceremonies.

LinkCraftor remains the canonical authority for permanent principals, account status, workspace membership, roles, permissions, subscriptions and business-access decisions.

| Responsibility | Canonical authority |
|---|---|
| Permanent LinkCraftor principal ID | LinkCraftor |
| Password, passkey and MFA verification | Future identity provider |
| Google identity verification | Google through the future provider |
| Authentication-token issuance | Future identity provider |
| Authentication-token validation | LinkCraftor Identity Service |
| Account suspension and containment | LinkCraftor |
| Workspace membership and roles | LinkCraftor Authorization Service |
| Document and feature permissions | LinkCraftor Authorization Service |
| Subscription entitlements | LinkCraftor billing authority |
| AWS infrastructure permissions | AWS IAM, separately |
| Provider-specific subject ID | Mapping reference only |

Mandatory rules:

- LinkCraftor must not store customer passwords in ordinary application databases.
- Provider identifiers must not become LinkCraftor business-record identifiers.
- Providers must not assign workspace roles, permissions or subscription entitlements.
- Business services must not call provider administration APIs directly.
- Authentication results must be validated before LinkCraftor accepts them.
- AWS IAM identities must remain separate from customer identities.
- Replacing a provider must not change LinkCraftor principal identifiers.
- Authentication or identity-mapping uncertainty must fail securely.

The frontend must use LinkCraftor-controlled identity routes. Required protocol redirects may reach Google or the future provider, but business logic must remain provider-neutral.

Provider-specific failures must be normalized into LinkCraftor-controlled authentication, verification, restriction and service-availability states.

R1 records architecture requirements only. It does not select a provider, create AWS resources, integrate runtime services or implement frontend interfaces.

<!-- PHASE_2_ITEM_2_2_R2_APPROVED_PRINCIPAL_IDENTIFIERS -->

#### Approved R2 — LinkCraftor-Controlled Principal Identifiers

- Requirement ID: `2.2-R2`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

Every canonical principal identifier must be generated and controlled by LinkCraftor.

Approved conceptual formats are:

- Customer principal: `lc_customer_<UUID>`
- Staff principal: `lc_staff_<UUID>`
- Machine or installation principal: `lc_machine_<UUID>`

The final UUID version and storage encoding will be confirmed during implementation review. UUIDv7 is the preferred implementation candidate.

Principal identifiers are immutable, opaque, non-recycled references. They are not passwords, session tokens or proof of authorization.

Email addresses, usernames, telephone numbers, provider subjects and workspace roles must not become permanent principal identifiers.

Changing email, password, Google identity, passkeys, provider, workspace membership or product access must not change the canonical principal.

One customer principal may use the WordPress Plugin, Editor, billing, subscription management and Customer Security Centre, subject to independent authorization and entitlement.

Customer, Staff, and Machine and Installation principals must remain separate. A person with customer and staff access must use separate security contexts.

Matching email addresses alone must never automatically merge principals. Deleted principal identifiers must never be assigned to another actor.

<!-- PHASE_2_ITEM_2_2_R3_APPROVED_EXTERNAL_IDENTITY_MAPPING -->

#### Approved R3 — External-Provider Identity Mapping

- Requirement ID: `2.2-R3`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

Provider identities must connect to canonical LinkCraftor principals through explicit identity bindings.

Each binding must record the LinkCraftor principal, realm, provider, issuer, provider tenant, provider subject, verification state, binding state and security evidence.

The combination of provider issuer, provider tenant and provider subject must be unique. One provider identity may map to only one LinkCraftor principal.

One LinkCraftor principal may have several securely linked authentication methods, including password, Google, passkey and enterprise SSO.

Identity linking requires control of the existing account and proof of the new identity. Sensitive linking and unlinking require fresh step-up authentication.

Email equality, even when verified, must not automatically merge accounts. Conflicting mappings must fail securely and enter controlled resolution.

A customer must not remove their final usable authentication or recovery method until a replacement is verified.

Provider migration must create a controlled replacement binding while preserving the canonical principal. Old bindings must be migrated, revoked or retained only under approved policy.

Every link, unlink, conflict, migration and administrative resolution must be auditable.

The Customer Security Centre must eventually display understandable connected sign-in methods without exposing raw provider subject identifiers.

<!-- PHASE_2_ITEM_2_2_R4_APPROVED_PROVIDER_ADAPTER_INTERFACE -->

#### Approved R4 — Canonical Provider-Adapter Interface

- Requirement ID: `2.2-R4`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

LinkCraftor must expose one canonical provider-adapter contract independent of Cognito, Auth0 or another future provider.

The contract must support canonical operations for:

- Provider capability and availability discovery
- Signup initiation and confirmation
- Login initiation and challenge completion
- Google and enterprise authentication initiation
- Secure authentication-callback processing
- Passkey enrolment, listing and removal
- MFA enrolment, verification and removal
- Recovery initiation and completion
- Session refresh and revocation
- Single-session and global logout
- Authentication-result validation
- Authentication-assurance retrieval
- Risk and security-event receipt
- Account authentication containment

Frontends and business services must not call provider SDKs or administrative APIs directly.

Provider SDK objects, claims, errors and administrative responses must not escape the adapter boundary.

The adapter must return canonical LinkCraftor results and error codes, declare supported capabilities, fail securely for unsupported operations, and preserve correlation and audit evidence.

State-changing operations must support safe retry or idempotency where required.

Provider secrets and administrative credentials must remain in approved secret storage and must not be delivered to customer-facing code.

Every provider adapter must be independently versioned and pass the same contract-certification suite.

The frontend must call LinkCraftor identity endpoints. Approved browser redirects to Google or the selected provider may occur only as part of controlled authentication protocols.

Business authorization, workspace roles and subscription entitlements remain outside the provider adapter.

R2-R4 record architecture requirements only. They do not create principals, link real accounts, install an SDK, select a provider or authorize implementation.

<!-- PHASE_2_ITEM_2_2_R5_APPROVED_SIGNUP_LOGIN_LOGOUT_CONTRACTS -->

#### Approved R5 — Signup, Login and Logout Contracts

- Requirement ID: `2.2-R5`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

LinkCraftor must expose provider-neutral contracts for email-and-password signup, Google signup and login, verification, authentication challenges, login completion, current-session logout and all-session logout.

Every authentication transaction must return canonical LinkCraftor fields including transaction ID, correlation ID, status, next action, expiration, permitted methods, retry guidance and safe error code.

Authentication transactions must be short-lived, single-purpose, bound to their initiating client and protected against replay, tampering and unauthorized redirect.

OAuth and OIDC flows must use Authorization Code with PKCE S256, state, nonce, strict redirect allowlists and controlled callback processing.

State-changing operations must support idempotency or safe retry where required.

Signup and login responses must resist account enumeration. Public messages must not reveal whether another person owns an account.

Passwords and provider credential secrets must not be written to LinkCraftor logs, analytics, ordinary databases or support interfaces.

Logout must distinguish current-session revocation from all-session revocation and must provide authoritative completion or truthful partial-failure status.

The frontend journey must use LinkCraftor-controlled states: enter details, verify identity, complete challenge, authentication successful, safely retryable failure, and service unavailable.

<!-- PHASE_2_ITEM_2_2_R6_APPROVED_FACTOR_RECOVERY_SESSION_CONTRACTS -->

#### Approved R6 — MFA, Passkey, Recovery and Session Contracts

- Requirement ID: `2.2-R6`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

LinkCraftor must expose provider-neutral contracts for passkey enrolment, naming, listing and removal; TOTP enrolment, verification and removal; recovery-code generation and replacement; account recovery; step-up authentication; session listing, refresh and revocation; and compromised-account containment.

The approved assurance model and policies from Phase 2.1 remain authoritative.

User-verifying passkeys remain the preferred AAL2 method. TOTP remains the approved fallback. SMS and voice OTP remain disabled for the MVP.

Recovery codes must remain hashed, single-use and replaceable. Email recovery alone must not grant high assurance or bypass mandatory step-up.

Passkey private keys must remain on the customer authenticator. LinkCraftor must not store them.

Owners, Administrators and Billing Administrators must satisfy the previously approved strong-authentication requirements.

Sensitive factor changes, recovery changes, session-wide revocation and account-security actions require fresh step-up authentication.

Refresh credentials must be rotated and protected against replay. Detected replay must revoke the affected token family or broader sessions according to approved risk policy.

The existing Phase 2.1 concurrent-session ceilings and revocation rules remain authoritative.

The Customer Security Centre must eventually show passkeys, MFA methods, recovery readiness, active sessions and security-relevant changes.

<!-- PHASE_2_ITEM_2_2_R7_APPROVED_NORMALIZATION_CONTRACTS -->

#### Approved R7 — Claims, Errors and Security-Event Normalization

- Requirement ID: `2.2-R7`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

Provider claims, errors and events must be translated into LinkCraftor-controlled canonical contracts.

Canonical identity context may include principal ID, identity realm, session ID, authentication time, authentication methods, assurance level, verification state and security state.

Provider roles, groups or entitlements must not directly grant LinkCraftor workspace roles, permissions or subscription access.

Canonical public error codes include verification required, challenge required, step-up required, account restricted, session expired, recovery restricted, rate limited and authentication unavailable.

Public errors must be safe against account enumeration and must not expose provider internals, credential status or sensitive risk logic.

Canonical security events include signup completed, login succeeded, login failed, MFA changed, passkey added, passkey removed, recovery started, recovery completed, session revoked, risk detected and account contained.

Every security event must carry an event ID, occurrence time, correlation ID, source, outcome and appropriate principal, session, device and risk context when lawfully available.

IP and device information must follow the approved privacy, minimization and retention rules.

Raw provider payloads must remain restricted evidence and must not become the normal business-event contract.

Customer-facing messages and future Owner security interfaces must consume canonical LinkCraftor states rather than provider-specific codes.

R5-R7 record architecture requirements only. They do not create accounts, send messages, install SDKs, issue tokens, modify factors, create sessions or implement frontend interfaces.

<!-- PHASE_2_ITEM_2_2_R8_APPROVED_AUTHORIZATION_SEPARATION -->

#### Approved R8 — Business-Authorization Separation

- Requirement ID: `2.2-R8`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

Authentication proves identity. LinkCraftor authorization determines permitted workspaces, products, resources and actions.

Provider groups, roles and entitlements must not directly grant LinkCraftor workspace membership, roles, permissions, product access or subscription benefits.

Every protected backend operation must enforce LinkCraftor authorization using canonical principal, realm, workspace, resource, action, role, entitlement, assurance and security-state context.

Authorization must default to deny. Missing, conflicting, stale or unverified authorization information must not produce access.

Workspace roles are workspace-scoped. A role in one workspace must not grant access to another workspace.

Frontend visibility, disabled controls and hidden buttons are usability features, not authorization controls.

Authorization decisions must not require a provider network call for every valid application request. Provider tokens must be validated through approved local or controlled verification, then mapped to LinkCraftor authorization context.

Authorization caches must be bounded, versioned and invalidated when membership, role, entitlement, suspension, revocation or containment changes.

Customer, Staff, and Machine and Installation realms must remain separated. Machine access requires independently scoped machine authorization.

Authorization outcomes must be canonical LinkCraftor decisions such as allow, deny or step-up required and must produce suitable audit evidence.

<!-- PHASE_2_ITEM_2_2_R9_APPROVED_FRONTEND_UI_DESIGN -->

#### Approved R9 — Provider-Neutral Frontend UI Design

- Requirement ID: `2.2-R9`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

Customer authentication and account-security interfaces must use LinkCraftor-controlled routes, branding, states, copy and accessibility requirements.

The authentication area must eventually provide Create Account, Verify Email, Log In, Continue with Google, Passkey Challenge, MFA Challenge, Recovery, Step-Up Authentication, Log Out and Authentication Service Status interfaces.

The Customer Security Centre must eventually provide Sign-In Methods, Connected Identities, Passkeys, MFA Methods, Recovery Readiness, Recovery Codes, Active Sessions, Security Activity and Account Security Status interfaces.

Approved Google branding may appear for Google authentication. The underlying managed identity-provider brand must not control LinkCraftor business journeys.

The frontend must consume canonical LinkCraftor claims, next actions, errors and service states. Raw provider errors, subject identifiers, administrative APIs and secrets must not be exposed.

The frontend must implement safe loading, timeout, retry, degraded, secondary-failover and outage states without bypassing security controls.

Account-enumeration-safe messages are mandatory. Password-manager compatibility and WebAuthn-compatible passkey journeys must be preserved.

Long-lived authentication secrets must not be stored in insecure browser storage. Session transport and browser-storage choices require later security certification.

Every interface must support keyboard use, accessible labels, responsive layouts, visible focus, comprehensible security guidance and safe cancellation.

Frontend controls must not be treated as backend authorization. Every protected action remains server-authorized.

Provider-specific SDK or business logic must not spread through LinkCraftor frontend modules.

<!-- PHASE_2_ITEM_2_2_R10_APPROVED_PROVIDER_MIGRATION_REPLACEMENT -->

#### Approved R10 — Provider Migration and Emergency Replacement

- Requirement ID: `2.2-R10`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

LinkCraftor must support planned provider migration and controlled emergency replacement without changing canonical principal identifiers, workspace memberships, permissions, subscriptions or business records.

Migration review may be triggered by outage, breach, unacceptable price, SLA failure, missing capability, compliance or residency concern, product retirement or founder-approved strategy.

Every migration requires an approved target adapter, capability comparison, data inventory, binding-conversion plan, session and token cutover plan, customer-impact assessment, communication plan, test evidence, rollback plan and final approval.

Provider bindings must transition through controlled states. Old bindings must be migrated, revoked or retained only under approved policy.

Token issuers, audiences and signing keys require explicit allowlists and time-bounded cutover. Old-provider tokens must be rejected after the approved transition window.

Passwords, passkeys, TOTP secrets and recovery methods must not be assumed portable. Customers may require secure reauthentication, password reset, passkey re-enrolment or MFA re-enrolment.

No migration or emergency condition permits an MFA bypass, password bypass, account-enumeration disclosure or manual declaration that a person is authenticated.

Support personnel must not attach an external identity to a principal without the approved proof, step-up, recovery and audit requirements.

High-risk linking, recovery or factor changes may be temporarily frozen during migration or incident containment.

Customer communication, truthful service status, reconciliation, rollback, audit evidence and old-provider data-deletion or exit evidence are mandatory.

The future Owner Console must display provider health, migration phase, binding progress, failures, customers requiring action, token-cutover readiness, rollback readiness and final evidence.

R8-R10 record architecture requirements only. They do not modify permissions, build interfaces, migrate accounts, select a provider or authorize production.

<!-- PHASE_2_ITEM_2_2_R11_VALIDATED_ARCHITECTURE_COMPLETE -->

#### Approved R11 — Phase 2.2 Validation and Closure

- Requirement ID: `2.2-R11`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`
- Validation status: `PASSED`
- Phase 2.2 status: `ARCHITECTURE_COMPLETE`
- Completion scope: `PHASE_2_2_ARCHITECTURE_ONLY`
- Provider decision: `DEFERRED`
- Selected provider: `NONE`
- Integration gate: `DEFERRED`
- Implementation gate: `BLOCKED`
- Production gate: `BLOCKED`

The Phase 2.2 validation confirmed that:

- LinkCraftor owns canonical principals and business authorization.
- External provider identities remain replaceable mappings.
- Email equality cannot automatically merge accounts.
- Provider-specific code remains behind the canonical adapter.
- Signup, login, logout, MFA, passkey, recovery and session contracts are defined.
- Provider claims, errors and security events are normalized.
- Customer, Staff, and Machine and Installation security realms remain separated.
- Provider-neutral customer authentication and Security Centre interfaces are defined.
- Planned migration and controlled emergency replacement requirements are defined.
- No implementation or production effects were authorized or executed.

Phase 2.2 is complete at the architecture level.

This closure does not select Cognito, Auth0, WorkOS or another provider. It does not create AWS resources, accounts, credentials, sessions, tokens or frontend interfaces. It does not install an SDK, integrate runtime services, execute a migration or authorize spending.

Provider selection, AWS deployment, runtime integration, data integration, frontend implementation, certification and production authorization remain controlled by their later gates.

The next architecture item is `2.3 — OIDC/OAuth 2.0 Protocol Foundation`.

<!-- PHASE_2_ITEM_2_3_OIDC_OAUTH_PROTOCOL_FOUNDATION -->

### 2.3 OIDC/OAuth 2.0 Protocol Foundation

- Item status: `IN_PROGRESS`
- Provider decision: `DEFERRED`
- Selected provider: `NONE`
- AWS deployment status: `NOT_STARTED`
- Runtime integration: `DEFERRED`
- Frontend implementation: `DEFERRED`
- Implementation gate: `BLOCKED`
- Production gate: `BLOCKED`

<!-- PHASE_2_ITEM_2_3_R1_APPROVED_PROTOCOL_BASELINE -->

#### Approved R1 — Protocol Purpose, Ownership and Security Baseline

- Requirement ID: `2.3-R1`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

The canonical user-authentication protocol between LinkCraftor and a future managed identity provider is OpenID Connect 1.0.

The canonical delegated API-access protocol is OAuth 2.0, governed by the current approved OAuth security profile.

The approved standards baseline is:

- OpenID Connect Core 1.0 incorporating Errata Set 2
- OAuth 2.0 RFC 6749 as updated by RFC 9700 Security Best Current Practice
- Proof Key for Code Exchange RFC 7636
- Authorization Server Issuer Identification RFC 9207

OpenID Connect establishes authenticated identity. OAuth access tokens authorize access to specifically approved APIs. Neither protocol transfers LinkCraftor business-authorization authority to the identity provider.

LinkCraftor remains authoritative for permanent principals, account status, workspace membership, roles, permissions, subscriptions, business entitlements, step-up requirements, suspension and protected-operation decisions.

The required interactive user flow is Authorization Code Flow with transaction-specific PKCE using `S256`.

The OAuth Implicit Grant, Resource Owner Password Credentials Grant, PKCE `plain`, access tokens in URI query parameters and unvalidated authentication responses are prohibited.

Every interactive authentication transaction must use fresh and unpredictable transaction state, PKCE verifier, PKCE challenge and OpenID Connect nonce values.

Redirect URIs must be explicitly registered and exactly matched. Production callbacks must use HTTPS. Development exceptions must be separately controlled and must never weaken production callback policy.

Issuer, audience, signature, authorized party, nonce, time validity, transaction binding and permitted cryptographic algorithm must be validated before an authentication result is accepted.

Issuer mismatch, audience mismatch, signature failure, expired tokens, nonce mismatch, transaction mismatch, replay, unsupported algorithm or ambiguous provider identity must fail securely.

Token purposes must remain separated:

- ID tokens are authentication evidence and must not authorize LinkCraftor APIs.
- Access tokens authorize approved APIs and must not be treated as proof of the permanent LinkCraftor principal without validated mapping.
- Refresh tokens obtain replacement tokens under later rotation and replay controls.
- LinkCraftor browser sessions remain separately governed LinkCraftor security objects.

Provider subject identifiers remain external identity mappings. They must not replace permanent LinkCraftor principal identifiers.

Google authentication is an approved future OpenID Connect method through the canonical provider-adapter boundary. Google identity does not directly assign LinkCraftor roles, permissions or subscriptions.

Customer, Staff, and Plugin or Machine authentication must use separated clients, audiences, scopes and security contexts.

AWS IAM identities and runtime job identities remain outside this customer-identity protocol authority.

Frontend interfaces must use LinkCraftor-controlled identity routes and canonical protocol states. Provider administrative credentials, raw provider errors and provider-specific business logic must not enter customer-facing code.

R1 records architecture requirements only. It does not select a provider, register an OAuth client, create Google credentials, create AWS resources, install an SDK, create an account, issue a token, create a session or implement a frontend or backend route.

<!-- PHASE_2_ITEM_2_3_R2_APPROVED_CLIENT_TRUST_BOUNDARIES -->

#### Approved R2 — Client Types and Trust Boundaries

- Requirement ID: `2.3-R2`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

Every OAuth or OpenID Connect client must be classified according to its actual ability to protect credentials.

The approved client classifications are:

| LinkCraftor component | Classification | Required security boundary |
|---|---|---|
| Customer Web Editor | Confidential web/BFF client | Provider tokens remain on the trusted backend |
| Customer Security Centre | Customer BFF boundary | Browser receives protected LinkCraftor session state only |
| WordPress Plugin | Public installation client by default | No shared secret embedded in distributed plugin code |
| Future mobile application | Public native client | External browser and PKCE required |
| Future desktop application | Public native client | External browser and PKCE required |
| Owner and Staff Console | Separate confidential web/BFF client | Separate privileged registration, session and assurance policy |
| Customer installation identity | Separately scoped machine client | No inherited customer or staff authority |
| Internal backend service | Confidential machine client | Separate service identity and restricted audience |
| Marketing homepage | Not an authentication authority | May redirect only to canonical LinkCraftor identity routes |

The Customer Web Editor and Customer Security Centre must use a backend-for-frontend boundary. Provider secrets, refresh tokens, long-lived access tokens, provider administrative credentials and raw provider security responses must not be delivered to browser code.

The distributed WordPress Plugin must not contain a universal reusable client secret. Each installation requires its own LinkCraftor installation identity and independent revocation.

A WordPress installation may be treated as confidential only after unique per-installation credential provisioning, protected storage, rotation and revocation have passed later certification.

Native applications must use an external system browser, PKCE and separately registered callbacks. Embedded authentication webviews and reusable embedded secrets are prohibited.

Customer, Staff, Plugin, Machine and internal-service security contexts must remain separated.

Development, testing, staging and production require separate client identifiers, credentials, callbacks, issuer allowlists, audiences, scopes and session namespaces.

A component is confidential only when it can genuinely protect its credentials from users, browsers, plugin administrators, device owners and untrusted software.

<!-- PHASE_2_ITEM_2_3_R3_APPROVED_AUTHORIZATION_CODE_PKCE_TRANSACTION -->

#### Approved R3 — Authorization Code and PKCE Transaction

- Requirement ID: `2.3-R3`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

Every interactive authentication must begin with a new LinkCraftor-controlled authentication transaction.

The transaction must contain a transaction ID, correlation ID, client identity, expected issuer, exact callback, requested scopes, browser or device binding, creation time, expiration time, random state, random OpenID Connect nonce, random PKCE verifier and derived `S256` challenge.

The LinkCraftor authentication-transaction lifetime must not exceed ten minutes.

The authorization request must use `response_type=code`, the approved client identifier, an exact registered redirect URI, minimum approved scopes beginning with `openid`, transaction-specific state, transaction-specific nonce, a PKCE challenge and `code_challenge_method=S256`.

The authorization response must return only an authorization code and required response metadata. Access tokens and refresh tokens must not be returned through browser URLs.

Before code exchange, LinkCraftor must validate the active transaction, state, expected issuer, callback, client, expiration and single-use status.

The code exchange must use the original transaction-bound PKCE verifier. Confidential clients must also use their later approved client-authentication method.

Authorization codes, state values, nonce values and transactions are single use. Retrying authentication requires a new transaction.

No LinkCraftor session may be created until token-response and identity validation succeed.

Authorization codes, PKCE verifiers, tokens and provider secrets must not enter normal logs, analytics, browser history or error messages.

After callback processing, LinkCraftor must redirect to a clean internal URL that does not retain protocol parameters.

Concurrent tabs and devices must use separate transactions and must not overwrite or consume one another.

PKCE downgrade, missing challenge binding, expired transactions, replay and mismatched client or callback must fail securely.

<!-- PHASE_2_ITEM_2_3_R4_APPROVED_DISCOVERY_ISSUER_ENDPOINT_VALIDATION -->

#### Approved R4 — Provider Discovery, Issuer and Endpoint Validation

- Requirement ID: `2.3-R4`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

LinkCraftor must maintain an explicit environment-specific allowlist of approved identity issuers.

Trusted OpenID Connect or OAuth metadata may provide the issuer, authorization endpoint, token endpoint, JWKS location, UserInfo endpoint when required, supported response types, grant types, PKCE methods, signing algorithms and authorization-response issuer support.

Discovery and metadata retrieval must use HTTPS. The returned issuer must exactly equal the configured issuer used to locate the metadata.

An issuer must not be accepted from customer input, email domains, arbitrary URL parameters, unvalidated token claims or callback parameters.

Authorization, token, UserInfo and JWKS endpoints must come from validated trusted metadata or approved static configuration.

Token-controlled URLs such as untrusted `jku`, `x5u` or equivalent header locations must not become trusted key sources.

Metadata and JWKS retrieval require destination allowlisting, DNS and IP safety checks, redirect restrictions, response-size limits, timeouts and protection against server-side request forgery.

Metadata and public signing keys may be cached only for bounded periods under approved cache policy.

An unknown signing-key identifier may trigger a controlled refresh only from the already trusted JWKS location. Failure to retrieve or validate the key must not cause token acceptance.

Key rotation must permit an approved overlap period without disabling signature, issuer, audience or algorithm validation.

New authentication must fail securely when trusted metadata or required keys cannot be safely obtained. Existing sessions remain governed by the separately approved session policy.

Provider discovery remains configuration driven and provider neutral. R4 does not select or deploy a provider.

<!-- PHASE_2_ITEM_2_3_R5_APPROVED_CALLBACK_STATE_NONCE_MIXUP_PROTECTION -->

#### Approved R5 — Redirect, Callback, State, Nonce and Mix-Up Protection

- Requirement ID: `2.3-R5`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

Production redirect and callback URIs must use HTTPS, be explicitly registered and use exact string matching.

Wildcard callbacks, arbitrary callback construction and open redirectors are prohibited.

Native loopback callback exceptions may be used only under a later certified native-application profile.

State and nonce values must each contain at least 128 bits of cryptographically secure randomness, be bound to one transaction and browser or device context, expire within ten minutes and be accepted only once.

State must not contain unprotected credentials, tokens, personal data or sensitive navigation information.

The nonce in the validated ID token must exactly match the transaction nonce before any token or identity result is used.

The authorization-response issuer must match the expected approved issuer, trusted metadata and validated ID token.

A response from one issuer must never be sent to another issuer token endpoint. Multiple providers require independently bound transactions.

Callbacks must reject missing required fields, duplicate or ambiguous parameters, conflicting success and error values, unsupported response modes, unsolicited callbacks, expired transactions, callback mismatch and replay.

ID tokens, access tokens and refresh tokens delivered through query parameters or URL fragments must be rejected.

Post-authentication destinations must use internal destination identifiers or an explicit LinkCraftor allowlist. Arbitrary `return_to` URLs must not control redirection.

Callback responses must prevent caching and referrer leakage and must remove protocol parameters from the visible URL.

Raw provider failures must be normalized into safe LinkCraftor states. Issuer mismatch, replay and transaction-validation failure must produce security events without exposing sensitive details.

Frontend callback states must support returning, validating, successful, safely retryable, cancelled and authentication-unavailable outcomes without bypassing server validation.

R2-R5 record architecture requirements only. They do not register clients, generate secrets, create Google credentials, modify the WordPress Plugin, create AWS resources, issue accounts or tokens, build frontend or backend routes, or authorize production.

<!-- PHASE_2_ITEM_2_3_R6_APPROVED_ID_TOKEN_VALIDATION -->

#### Approved R6 — ID-Token Validation

- Requirement ID: `2.3-R6`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

An ID token is authentication evidence. It must not authorize LinkCraftor APIs or directly grant LinkCraftor business access.

ID-token validation must use a dedicated validation context that cannot confuse an ID token with an access token, logout token, security-event token or another JWT type.

Every accepted ID token must have a valid signature produced by an approved key belonging to the exact trusted issuer.

LinkCraftor must use an explicit cryptographic-algorithm allowlist. The `none` algorithm, algorithm substitution, unapproved symmetric verification and token-selected untrusted key sources are prohibited.

The validated issuer must exactly equal the transaction issuer and approved provider metadata.

The audience must contain the registered client identifier. Additional untrusted audiences are prohibited, and `azp` must be validated when multiple audiences are present.

Expiration, issued-at time, not-before time when present and centrally bounded clock skew must be validated. Clock-skew allowances must not expand automatically after failures.

The ID-token nonce must exactly equal the active single-use transaction nonce.

Authentication time must be validated when recent authentication, maximum age or step-up was requested.

Required assurance and method evidence such as `acr` and `amr` must be checked before an assurance-dependent action is allowed.

The subject must be non-empty and stable within the validated issuer. The issuer, provider tenant and subject form the external identity-binding key.

Email, username or telephone equality must not replace the issuer-subject binding and must not automatically merge accounts.

Provider roles, groups and entitlements must not grant LinkCraftor roles, permissions, workspace membership or subscriptions.

The `at_hash` value must be validated when present and applicable to the approved response profile.

No LinkCraftor session or identity binding may be created until all required validation succeeds. Any uncertainty must fail securely.

<!-- PHASE_2_ITEM_2_3_R7_APPROVED_ACCESS_TOKEN_API_VALIDATION -->

#### Approved R7 — Access-Token and API Validation

- Requirement ID: `2.3-R7`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

LinkCraftor must support provider-neutral validation of signed JWT access tokens and opaque access tokens.

For a JWT access token, the receiving API must validate the signature, approved algorithm, trusted issuer, exact intended resource audience, expiration, not-before and issued-at values when present, client identifier, approved scopes, token type and sender-constraining evidence when required.

When the provider uses the RFC 9068 access-token profile, the token must follow its required access-token type and claim rules.

For an opaque access token, the receiving protected service must use an authenticated HTTPS introspection endpoint obtained from trusted configuration or metadata.

An opaque token must be active and valid for the expected client, audience, scope, time window and protected resource.

Introspection results may be cached only for a bounded period that does not defeat expiration, revocation or containment.

An ID token must never be accepted as an API access token.

Browser session cookies must be accepted only by the intended BFF session boundary and must not become general API bearer credentials.

Access tokens must be transmitted through the approved authorization header. Access tokens in query parameters, fragments or normal logs are prohibited.

Every protected API requires an explicit audience. Wildcard audiences, unrestricted all-API scopes and cross-environment token acceptance are prohibited.

Customer, Staff, Plugin, Machine and internal-service audiences and scopes must remain separated.

Scopes restrict protocol-level access but do not replace LinkCraftor workspace, role, entitlement, resource and action authorization.

Validated external identity context must map to the canonical LinkCraftor principal before business authorization.

Signed access tokens may be validated locally using bounded caches of trusted public keys to support high request volumes without a provider network call for every valid request.

Token-validation failures must produce safe canonical errors and appropriate security evidence without exposing token contents or sensitive validation details.

<!-- PHASE_2_ITEM_2_3_R8_APPROVED_REFRESH_ROTATION_REPLAY_REVOCATION -->

#### Approved R8 — Refresh Rotation, Replay Detection and Revocation

- Requirement ID: `2.3-R8`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

Refresh tokens may be issued only when the approved client and risk policy require them.

Web Editor, Customer Security Centre and Staff Console refresh tokens must remain behind their trusted server-side BFF boundaries and must not be delivered to browser code.

Every refresh token must remain bound to its client, principal, session, token family, approved scopes, approved audiences and appropriate device or installation context.

Refresh must not increase scopes, audiences, roles, permissions, workspace access or entitlements.

Refresh-token rotation is required. Every successful refresh must issue a replacement token and invalidate the previous token.

LinkCraftor and the provider boundary must retain sufficient token-family lineage to detect reuse of an invalidated token.

Concurrent refresh attempts must be serialized or safely coordinated so normal client concurrency cannot bypass rotation or create false replay handling.

Confirmed reuse must revoke the active token family and affected session, produce a security event, trigger risk evaluation and require fresh authentication.

Public clients require approved rotation or sender-constraining. Rotation is the default requirement, with sender-constraining added when supported and certified.

Refresh-token inactivity and absolute expiration must remain within the previously approved Phase 2.1 ceilings.

Provider refresh tokens must be encrypted within approved backend or native secure storage and must not enter logs, analytics, crash reports or unencrypted backups.

Revocation must support current logout, global logout, individual-session termination, plugin disconnection, installation revocation, password change, recovery completion, factor-security changes, suspension, account-takeover containment, provider migration and emergency containment.

Revocation endpoints must use trusted HTTPS metadata or approved configuration. Clients must stop using a token immediately after confirmed revocation.

Revocation propagation delays must be minimized and bounded. LinkCraftor containment remains authoritative even when provider propagation is incomplete.

<!-- PHASE_2_ITEM_2_3_R9_APPROVED_BROWSER_SESSION_TOKEN_CUSTODY -->

#### Approved R9 — Browser Session and Token Custody

- Requirement ID: `2.3-R9`
- Status: `APPROVED`
- Approval authority: `FOUNDER_OWNER`
- Approval date: `2026-11-03`

The approved customer and staff web architecture is the Backend for Frontend pattern.

The BFF is the confidential OAuth client, manages provider access and refresh tokens on the server and forwards approved API requests with the appropriate access token.

Browser code receives only an opaque LinkCraftor session identifier. Provider access tokens, refresh tokens, client secrets and administrative credentials must not be delivered to browser JavaScript.

The primary authenticated session cookie must use `Secure`, `HttpOnly`, `SameSite=Strict` by default, `Path=/`, no `Domain` attribute and the `__Host-` prefix.

A separate short-lived authentication-transaction cookie may use the least-permissive certified setting required for a cross-site callback. It must never become the authenticated session cookie.

Session identifiers must be unpredictable, rejected when caller supplied and rotated after login, step-up authentication and privilege elevation.

Authoritative session state must remain server-side and include the canonical principal, realm, authentication time, assurance, token references, security state, session version and applicable expirations.

Every state-changing browser operation requires CSRF protection and appropriate Origin, Referer and Fetch Metadata validation where available.

The BFF must use explicit upstream destinations, methods and route policies and must not become an unrestricted proxy or server-side request-forgery channel.

Sensitive responses must use no-store caching policy.

Provider tokens and long-lived authentication credentials are prohibited in localStorage, sessionStorage, IndexedDB, JavaScript-readable cookies, URLs and frontend logs.

Logout must destroy the server session, clear the browser cookie and revoke the associated refresh grant. Global logout must revoke every applicable session and grant.

Customer and Staff cookies, session namespaces and security boundaries must remain separate.

The previously approved Phase 2.1 idle, absolute, concurrency, revocation and containment limits remain authoritative.

Distributed session infrastructure must support atomic revocation, safe concurrency and scalable validation for thousands of simultaneous users.

Provider, token-store or session-state uncertainty must fail securely.

R6-R9 record architecture requirements only. They do not issue tokens, create session storage, set cookies, build the BFF, modify frontend code, create AWS resources, select a provider or authorize production.

#### Phase 2.3 Progress

R1 through R9 are approved. The next requirement is `2.3-R10 — Google OIDC Federation and Account Binding`.