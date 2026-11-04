# LinkCraftor AK.6/AK.7 operational trust audit — read only.
# Windows PowerShell 5.1 / PowerShell 7; no elevated permissions required for initial assessment.
# Does not provision identities, keys, ACLs, workers, queues, or production jobs.
[CmdletBinding()]
param(
    [string]$WorkerServiceName = '',
    [string]$IssuerPublicKeyFile = '',
    [string]$ProjectRoot = (Get-Location).Path
)
$ErrorActionPreference = 'Stop'
$checks = New-Object 'System.Collections.Generic.List[object]'
function Record([string]$Name, [string]$Status, [string]$Detail) {
    $checks.Add([pscustomobject]@{ requirement=$Name; status=$Status; detail=$Detail })
    $color = if ($Status -eq 'PASS') { 'Green' } elseif ($Status -eq 'BLOCKED') { 'Yellow' } else { 'Red' }
    Write-Host ("{0}: {1} — {2}" -f $Status, $Name, $Detail) -ForegroundColor $color
}
function Get-Sid([string]$Account) {
    try { return (New-Object System.Security.Principal.NTAccount($Account)).Translate([System.Security.Principal.SecurityIdentifier]).Value }
    catch { return $null }
}
function Test-RestrictedAcl([string]$Target, [string]$WorkerSid, [bool]$AllowWorkerWrite) {
    try {
        $acl = Get-Acl -LiteralPath $Target
        if (-not $acl.AreAccessRulesProtected) { return 'ACL inheritance is enabled' }
        $ownerSid = Get-Sid $acl.Owner
        if ($ownerSid -notin @('S-1-5-18','S-1-5-32-544')) { return 'ACL owner is not SYSTEM or Administrators' }
        $allowed = @('S-1-5-18','S-1-5-32-544')
        if ($AllowWorkerWrite -and $WorkerSid) { $allowed += $WorkerSid }
        $rights = [System.Security.AccessControl.FileSystemRights]::Write -bor
                  [System.Security.AccessControl.FileSystemRights]::Modify -bor
                  [System.Security.AccessControl.FileSystemRights]::FullControl -bor
                  [System.Security.AccessControl.FileSystemRights]::ChangePermissions -bor
                  [System.Security.AccessControl.FileSystemRights]::TakeOwnership
        foreach ($rule in $acl.Access) {
            if ($rule.AccessControlType -ne [System.Security.AccessControl.AccessControlType]::Allow) { continue }
            if (($rule.FileSystemRights -band $rights) -eq 0) { continue }
            $ruleSid = Get-Sid $rule.IdentityReference.Value
            if (-not $ruleSid -or $ruleSid -notin $allowed) { return ('Untrusted writer: ' + $rule.IdentityReference.Value) }
        }
        return $null
    } catch { return ('Could not verify ACL: ' + $_.Exception.GetType().Name) }
}

Write-Host 'LINKCRAFTOR AK.6 / AK.7 — OPERATIONAL TRUST AUDIT (READ ONLY)' -ForegroundColor Cyan
$root = [IO.Path]::GetFullPath($ProjectRoot)
if ((Split-Path $root -Leaf) -ne 'LinkCraftor') { throw 'Run from the LinkCraftor project root or specify -ProjectRoot' }
$mod = Join-Path $root 'backend\server\runtime\security\ak6_operational_trust.py'
$signed = Join-Path $root 'backend\server\runtime\security\ak6_signed_execution_grants.py'
$handler = Join-Path $root 'backend\server\runtime\universal_runtime_registration.py'
$queue = Join-Path $root 'backend\server\orchestration\queue.py'
$auth = 'C:\ProgramData\LinkCraftor\AK6\authority'
$state = 'C:\ProgramData\LinkCraftor\AK6\state'
$keyPath = Join-Path $auth 'issuer_ed25519_public.b64'
$sidPath = Join-Path $auth 'worker_token_sid.txt'
$serviceSid = $null
$issuerBytes = $null
$pinnedBytes = $null

if (-not [Environment]::OSVersion.Platform.ToString().StartsWith('Win')) {
    Record 'windows_host' 'BLOCKED' 'Windows host required'
} else { Record 'windows_host' 'PASS' 'Windows detected' }
$sourceMissing = @(@($mod,$signed,$handler,$queue) | Where-Object { -not (Test-Path -LiteralPath $_ -PathType Leaf) })
if ($sourceMissing.Count) { Record 'integrated_runtime_source' 'BLOCKED' ('Missing source files: ' + ($sourceMissing -join '; ')) }
else {
    $verifierText = [IO.File]::ReadAllText($signed)
    $handlerText = [IO.File]::ReadAllText($handler)
    $queueText = [IO.File]::ReadAllText($queue)
    if ($verifierText.Contains('AK6_FOUR_CONTROLS_OPERATIONAL_BOUNDARY') -and $handlerText.Contains('AK6_FOUR_CONTROLS_OPERATIONAL_BOUNDARY') -and $queueText.Contains('AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED')) {
        Record 'integrated_runtime_source' 'PASS' 'Four-control and queue/handler integration markers present (not execution certification)'
    } else { Record 'integrated_runtime_source' 'BLOCKED' 'Expected integration markers not all present' }
}

if (-not $WorkerServiceName) {
    $matches = @()
    try { $matches = @(Get-CimInstance Win32_Service -ErrorAction Stop | Where-Object { $_.Name -match 'LinkCraftor|UniversalRuntime' } | Select-Object -First 10 Name, StartName, State) }
    catch { }
    $hint = if ($matches.Count) { ($matches | ForEach-Object { $_.Name + ' (run-as ' + $_.StartName + ')' }) -join '; ' } else { 'No matching service auto-detected' }
    Record 'dedicated_worker_service' 'BLOCKED' ('Specify -WorkerServiceName after service registration. ' + $hint)
} else {
    try {
        $svc = Get-CimInstance Win32_Service -Filter ("Name='" + $WorkerServiceName.Replace("'","''") + "'") -ErrorAction Stop
        if (-not $svc) { Record 'dedicated_worker_service' 'BLOCKED' ('Service not registered: ' + $WorkerServiceName) }
        else {
            $serviceSid = Get-Sid $svc.StartName
            if (-not $serviceSid) { Record 'dedicated_worker_service' 'BLOCKED' ('Run-as account SID cannot be resolved: ' + $svc.StartName) }
            elseif ($serviceSid -in @('S-1-5-18','S-1-5-19','S-1-5-20')) { Record 'dedicated_worker_service' 'BLOCKED' 'Service uses built-in shared service identity rather than a dedicated worker account' }
            else { Record 'dedicated_worker_service' 'PASS' ('Registered service ' + $svc.Name + ', run-as ' + $svc.StartName + ', state ' + $svc.State + '; real process-token attestation still required') }
        }
    } catch { Record 'dedicated_worker_service' 'BLOCKED' ('Cannot inspect Windows service: ' + $_.Exception.Message) }
}

if (-not $IssuerPublicKeyFile) { Record 'issuer_public_key' 'BLOCKED' 'No external issuer public key file specified; supply -IssuerPublicKeyFile (not a private key)' }
elseif (-not (Test-Path -LiteralPath $IssuerPublicKeyFile -PathType Leaf)) { Record 'issuer_public_key' 'BLOCKED' 'Public key file not found' }
else {
    try {
        $issuerBytes = [Convert]::FromBase64String(([IO.File]::ReadAllText([IO.Path]::GetFullPath($IssuerPublicKeyFile))).Trim())
        if ($issuerBytes.Length -ne 32) { throw 'Ed25519 public key must be exactly 32 bytes' }
        $sha = [System.Security.Cryptography.SHA256]::Create()
        try { $fingerprint = [BitConverter]::ToString($sha.ComputeHash($issuerBytes)).Replace('-','').ToLowerInvariant() }
        finally { $sha.Dispose() }
        Record 'issuer_public_key' 'PASS' ('Ed25519 32-byte public key file present; SHA-256=' + $fingerprint + '; issuer operational ownership not certified')
    } catch { Record 'issuer_public_key' 'BLOCKED' ('Invalid external public key: ' + $_.Exception.Message) }
}

if ((Test-Path $keyPath -PathType Leaf) -and (Test-Path $sidPath -PathType Leaf)) {
    try {
        $pinnedBytes = [Convert]::FromBase64String(([IO.File]::ReadAllText($keyPath)).Trim())
        $pinnedSid = ([IO.File]::ReadAllText($sidPath)).Trim()
        if ($pinnedBytes.Length -ne 32 -or -not $pinnedSid.StartsWith('S-1-5-')) { throw 'Pinned key/SID malformed' }
        if ($issuerBytes -and ([Convert]::ToBase64String($issuerBytes) -ne [Convert]::ToBase64String($pinnedBytes))) { throw 'Pinned public key differs from external issuer key' }
        if ($serviceSid -and $pinnedSid -ne $serviceSid) { throw 'Pinned worker SID differs from service run-as SID' }
        $errors = @()
        foreach ($p in @($auth,$keyPath,$sidPath)) {
            $problem = Test-RestrictedAcl $p $pinnedSid $false
            if ($problem) { $errors += ($p + ': ' + $problem) }
        }
        if ($errors.Count) { throw ($errors -join '; ') }
        Record 'machine_pinned_authority' 'PASS' 'Pinned key, worker SID and strict authority ACLs verified (ownership of issuer remains separate)'
    } catch { Record 'machine_pinned_authority' 'BLOCKED' $_.Exception.Message }
} else { Record 'machine_pinned_authority' 'BLOCKED' 'Protected issuer key and/or worker SID not provisioned' }

if (-not (Test-Path $state -PathType Container)) { Record 'durable_nonce_state' 'BLOCKED' 'Protected state directory not provisioned' }
else {
    $sidForAcl = if ($serviceSid) { $serviceSid } elseif (Test-Path $sidPath) { ([IO.File]::ReadAllText($sidPath)).Trim() } else { '' }
    $problem = Test-RestrictedAcl $state $sidForAcl $true
    if ($problem) { Record 'durable_nonce_state' 'BLOCKED' $problem }
    else { Record 'durable_nonce_state' 'PASS' 'State directory ACLs verified; cross-process concurrency and restart tests still required' }
}
Record 'independent_live_worker_attestation' 'BLOCKED' 'Must run authorization tests under actual dedicated Windows service token; config inspection is insufficient'
Record 'actual_issuer_signed_grant' 'BLOCKED' 'Must verify a grant issued by the real external authority; test keys do not qualify'
Record 'ak7_integrated_certification' 'BLOCKED' 'Disposable cloned job store, real service identity, signer, lease, replay/revocation, restart and six-stage tests not yet executed'

$report = [pscustomobject]@{
    report_type='AK6_AK7_OPERATOR_TRUST_AUDIT'
    generated_utc=[DateTime]::UtcNow.ToString('o')
    read_only=$true
    production_jobs_executed=$false
    production_files_changed=$false
    production_activation='NO-GO'
    checks=@($checks.ToArray())
}
$out = Join-Path $root 'AK6_AK7_OPERATOR_TRUST_AUDIT.json'
$json = $report | ConvertTo-Json -Depth 6
[IO.File]::WriteAllText($out, $json, [Text.Encoding]::UTF8)
Write-Host ('REPORT: '+$out) -ForegroundColor Cyan
Write-Host 'PRODUCTION ACTIVATION: NO-GO. No workers, jobs, or trust configuration changed.' -ForegroundColor Yellow
