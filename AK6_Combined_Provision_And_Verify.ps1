#requires -Version 5.1
<#
AK.6 combined Windows operational provisioning (staged / inactive).
Never generates issuer keys, never starts a worker, never executes production jobs.
Requires real independently controlled Ed25519 public key and approved SCM-compatible service binary.
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]{3,64}$')][string]$ServiceName,
  [Parameter(Mandatory=$true)][string]$ServiceBinary,
  [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-fA-F]{64}$')][string]$ApprovedServiceBinarySha256,
  [Parameter(Mandatory=$true)][string]$IssuerPublicKeyFile,
  [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-fA-F]{64}$')][string]$ApprovedIssuerKeySha256,
  [string]$ProjectRoot = (Get-Location).Path
)
$ErrorActionPreference = 'Stop'
$reportPath = Join-Path $ProjectRoot 'AK6_COMBINED_PROVISION_REPORT.json'
$events = New-Object 'System.Collections.Generic.List[object]'
$createdService = $false
$createdRoot = $false
$createdFiles = New-Object 'System.Collections.Generic.List[string]'
$committed = $false
function Log([string]$Name,[string]$Status,[string]$Detail) {
  $events.Add([pscustomobject]@{check=$Name;status=$Status;detail=$Detail})
  Write-Host ("{0}: {1} - {2}" -f $Status,$Name,$Detail)
}
function Assert([bool]$Okay,[string]$Message) { if (-not $Okay) { throw $Message } }
function Sha256Bytes([byte[]]$Bytes) {
  $hash = [Security.Cryptography.SHA256]::Create()
  try { return ([BitConverter]::ToString($hash.ComputeHash($Bytes))).Replace('-','').ToLowerInvariant() }
  finally { $hash.Dispose() }
}
function RequireNative([string]$Program,[string[]]$Arguments) {
  & $Program @Arguments | Out-Null
  if ($LASTEXITCODE -ne 0) { throw ("Command failed (exit {0}): {1} {2}" -f $LASTEXITCODE,$Program,($Arguments -join ' ')) }
}
function ResolveSid([string]$Account) {
  if($Account -match '^S-1-[0-9-]+$') { return $Account }
  return (New-Object Security.Principal.NTAccount($Account)).Translate([Security.Principal.SecurityIdentifier]).Value
}
function AssertAcl([string]$Path,[string[]]$Writers,[bool]$RequireProtected=$true) {
  $acl=Get-Acl -LiteralPath $Path
  if ($RequireProtected) { Assert $acl.AreAccessRulesProtected ("ACL inheritance enabled: " + $Path) }
  $owner=([string]$acl.Owner)
  $ownerSid=ResolveSid $owner
  Assert (($ownerSid -in @('S-1-5-18','S-1-5-32-544')) -or ($owner -match 'TrustedInstaller')) ("Untrusted ACL owner: " + $Path)
  foreach($rule in $acl.Access) {
    if ($rule.AccessControlType -ne [Security.AccessControl.AccessControlType]::Allow) { continue }
    $writes = [Security.AccessControl.FileSystemRights]::Write -bor [Security.AccessControl.FileSystemRights]::Modify -bor [Security.AccessControl.FileSystemRights]::FullControl -bor [Security.AccessControl.FileSystemRights]::ChangePermissions -bor [Security.AccessControl.FileSystemRights]::TakeOwnership
    if (($rule.FileSystemRights -band $writes) -ne 0) {
      $sid=$rule.IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value
      Assert ($sid -in $Writers) ("Unauthorized ACL writer " + $sid + " at " + $Path)
    }
  }
}
function SetProtectedAcl([string]$Path,[string]$WorkerSid,[bool]$WorkerCanWrite,[bool]$Directory) {
  if ($Directory) {
    $admin='*S-1-5-32-544:(OI)(CI)F'; $system='*S-1-5-18:(OI)(CI)F'
    $worker=if($WorkerCanWrite){('*'+$WorkerSid+':(OI)(CI)M')}else{('*'+$WorkerSid+':(OI)(CI)R')}
  } else {
    $admin='*S-1-5-32-544:F'; $system='*S-1-5-18:F'; $worker='*'+$WorkerSid+':R'
  }
  RequireNative 'icacls.exe' @($Path,'/inheritance:r','/grant:r',$system,$admin,$worker)
  $writers=@('S-1-5-18','S-1-5-32-544')
  if($WorkerCanWrite){$writers+= $WorkerSid}
  AssertAcl $Path $writers
}
try {
  $root=[IO.Path]::GetFullPath($ProjectRoot)
  Assert ((Split-Path $root -Leaf) -eq 'LinkCraftor') 'Must run from LinkCraftor project root'
  $reportPath=Join-Path $root 'AK6_COMBINED_PROVISION_REPORT.json'
  $identity=[Security.Principal.WindowsIdentity]::GetCurrent()
  $principal=New-Object Security.Principal.WindowsPrincipal($identity)
  Assert $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) 'Run this script in an elevated Windows PowerShell window'
  Assert ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT) 'Windows host required'
  Log 'administrator' 'PASS' 'Elevated Windows operator verified'
  $expected=@(
    'backend/server/runtime/security/ak6_operational_trust.py',
    'backend/server/runtime/security/ak6_signed_execution_grants.py',
    'backend/server/orchestration/queue.py',
    'backend/server/runtime/universal_runtime_registration.py',
    'test_ak6_four_controls.py'
  )
  foreach($rel in $expected){Assert (Test-Path -LiteralPath (Join-Path $root $rel) -PathType Leaf) ('Missing AK.6 file: '+$rel)}
  $module=[IO.File]::ReadAllText((Join-Path $root 'backend/server/runtime/security/ak6_operational_trust.py'))
  $queue=[IO.File]::ReadAllText((Join-Path $root 'backend/server/orchestration/queue.py'))
  $handler=[IO.File]::ReadAllText((Join-Path $root 'backend/server/runtime/universal_runtime_registration.py'))
  Assert ($module.Contains('def require_operational_ak6_trust') -and $queue.Contains('AK6_SIGNED_EXECUTION_AUTHORITY_INTEGRATED') -and $handler.Contains('AK6_FOUR_CONTROLS_OPERATIONAL_BOUNDARY')) 'AK.6 runtime integration does not match expected protected layout'
  Log 'installed_runtime' 'PASS' 'Existing authorization code present; no source changes'
  & python (Join-Path $root 'test_ak6_four_controls.py') | Out-Host
  Assert ($LASTEXITCODE -eq 0) 'Existing AK.6 isolated tests failed'
  Log 'isolated_tests' 'PASS' 'AK.6 isolated test suite completed'

  $binary=[IO.Path]::GetFullPath($ServiceBinary)
  Assert (Test-Path -LiteralPath $binary -PathType Leaf) 'SCM-compatible Windows service executable not found'
  Assert ($binary -notmatch '[\x22\x0a\x0d]') 'Invalid service executable path'
  $exeHash=(Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash.ToLowerInvariant()
  Assert ($exeHash -eq $ApprovedServiceBinarySha256.ToLowerInvariant()) 'Service binary SHA256 does not match independently approved value'
  $exeSig=Get-AuthenticodeSignature -LiteralPath $binary
  Assert ($exeSig.Status -eq 'Valid') 'Service executable must have a valid Authenticode signature'
  # Neither the binary nor its containing directory may be writable by a regular user.
  AssertAcl $binary @('S-1-5-18','S-1-5-32-544') $false
  AssertAcl (Split-Path $binary -Parent) @('S-1-5-18','S-1-5-32-544') $false
  Log 'service_binary' 'PASS' ('Approved signed executable: '+$exeHash)
  $keyFile=[IO.Path]::GetFullPath($IssuerPublicKeyFile)
  Assert (Test-Path -LiteralPath $keyFile -PathType Leaf) 'External issuer PUBLIC key file does not exist'
  $keyText=[IO.File]::ReadAllText($keyFile).Trim()
  $keyBytes=[Convert]::FromBase64String($keyText)
  Assert ($keyBytes.Length -eq 32) 'Expected 32-byte Ed25519 public key encoded as base64'
  $issuerHash=Sha256Bytes $keyBytes
  Assert ($issuerHash -eq $ApprovedIssuerKeySha256.ToLowerInvariant()) 'Issuer key fingerprint does not match independently approved value'
  Log 'issuer_public_key' 'PASS' ('Public key fingerprint matches approved value: '+$issuerHash)

  $svc=Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
  Assert ($null -eq $svc) 'Service name already exists; refusing to overwrite or change it'
  $trustRoot='C:\ProgramData\LinkCraftor\AK6'
  $authority=Join-Path $trustRoot 'authority'
  $state=Join-Path $trustRoot 'state'
  $keyTarget=Join-Path $authority 'issuer_ed25519_public.b64'
  $sidTarget=Join-Path $authority 'worker_token_sid.txt'
  Assert (-not (Test-Path -LiteralPath $trustRoot)) 'AK.6 trust root already exists; refusing to overwrite or rotate'
  Log 'preflight' 'PASS' 'All required external inputs verified before system changes'

  # Register a DISABLED service. Approved binary must implement Windows SCM protocol.
  # Account is a dedicated Windows virtual service account; never LocalSystem.
  $account='NT SERVICE\'+$ServiceName
  $binPath='"'+$binary+'"'
  RequireNative 'sc.exe' @('create',$ServiceName,'binPath=',$binPath,'start=','disabled','obj=',$account,'type=','own','DisplayName=','LinkCraftor AK6 Worker (INACTIVE)')
  $createdService=$true
  RequireNative 'sc.exe' @('sidtype',$ServiceName,'unrestricted')
  $service=Get-CimInstance Win32_Service -Filter ("Name='"+$ServiceName+"'") -ErrorAction Stop
  Assert ($null -ne $service) 'Registered service not visible through Windows SCM'
  Assert ($service.StartMode -eq 'Disabled') 'Service unexpectedly enabled'
  Assert ($service.State -eq 'Stopped') 'Service unexpectedly running'
  Assert ($service.StartName -ieq $account) ('Unexpected service run-as identity: '+$service.StartName)
  $sid=ResolveSid $account
  Assert ($sid.StartsWith('S-1-5-80-')) 'Expected a dedicated NT SERVICE virtual account SID'
  Log 'dedicated_worker_service' 'PASS' ('Registered DISABLED: '+$ServiceName+'; SID '+$sid)

  New-Item -ItemType Directory -Path $trustRoot -ErrorAction Stop | Out-Null
  $createdRoot=$true
  New-Item -ItemType Directory -Path $authority,$state -ErrorAction Stop | Out-Null
  # Parent is restricted to SYSTEM/admins, worker read/traverse; state grants worker modify.
  foreach($dir in @($trustRoot,$authority,$state)) {
    RequireNative 'icacls.exe' @($dir,'/setowner','*S-1-5-32-544')
  }
  SetProtectedAcl $trustRoot $sid $false $true
  SetProtectedAcl $authority $sid $false $true
  SetProtectedAcl $state $sid $true $true
  [IO.File]::WriteAllText($keyTarget,$keyText,[Text.Encoding]::ASCII)
  $createdFiles.Add($keyTarget)
  [IO.File]::WriteAllText($sidTarget,$sid,[Text.Encoding]::ASCII)
  $createdFiles.Add($sidTarget)
  foreach($file in @($keyTarget,$sidTarget)) {
    RequireNative 'icacls.exe' @($file,'/setowner','*S-1-5-32-544')
  }
  SetProtectedAcl $keyTarget $sid $false $false
  SetProtectedAcl $sidTarget $sid $false $false
  $pinned=[Convert]::FromBase64String(([IO.File]::ReadAllText($keyTarget)).Trim())
  Assert ((Sha256Bytes $pinned) -eq $issuerHash) 'Pinned issuer key changed during provisioning'
  Assert (([IO.File]::ReadAllText($sidTarget)).Trim() -eq $sid) 'Pinned worker SID mismatch'
  Log 'trust_anchor' 'PASS' 'Public key and worker SID pinned to ACL-protected authority directory'
  Log 'durable_state' 'PASS' 'Protected state directory prepared for durable nonce ledger (worker-write only)'

  # Real process-token attestation requires actual service execution. Do NOT start
  # an unvalidated service here, because service binaries may execute live jobs.
  Log 'live_service_token' 'BLOCKED' 'Service deliberately remains stopped; actual process-token attestation required under controlled AK.7 run'
  Log 'real_issuer_signed_grant' 'BLOCKED' 'Public key pinned; verify a real issuer-signed grant during AK.7'
  Log 'ak7_integrated_tests' 'BLOCKED' 'Need isolated end-to-end execution with real service identity, issuer and disposable job store'
  $committed=$true
}
catch {
  Log 'failure' 'BLOCKED' $_.Exception.Message
  if (-not $committed) {
    if ($createdRoot -and (Test-Path -LiteralPath $trustRoot)) {
      try { Remove-Item -LiteralPath $trustRoot -Recurse -Force -ErrorAction Stop; Log 'rollback_trust_root' 'PASS' 'Newly created trust root removed' }
      catch { Log 'rollback_trust_root' 'BLOCKED' 'Manual administrator cleanup needed; verify protected files before retry' }
    }
    if ($createdService) {
      try { RequireNative 'sc.exe' @('delete',$ServiceName); Log 'rollback_service' 'PASS' 'Newly registered inactive service deleted' }
      catch { Log 'rollback_service' 'BLOCKED' 'Manual administrator service cleanup needed' }
    }
  }
}
finally {
  $report=[pscustomobject]@{
    report='AK6_COMBINED_PROVISION_REPORT'; created_utc=[DateTime]::UtcNow.ToString('o');
    service_name=$ServiceName; provisioned=$committed; production_activation='NO-GO';
    production_jobs_executed=$false; worker_started=$false;
    checks=@($events.ToArray())
  }
  try { [IO.File]::WriteAllText($reportPath,($report | ConvertTo-Json -Depth 6),[Text.Encoding]::UTF8); Write-Host ('REPORT: '+$reportPath) }
  catch { Write-Warning ('Unable to write report: '+$_.Exception.Message) }
}
if (-not $committed) { throw 'AK.6 combined provisioning stopped safely. See report.' }
Write-Host 'AK.6 COMBINED MACHINE PROVISIONING: STAGED (SERVICE DISABLED)'
Write-Host 'AK.7 LIVE IDENTITY, REAL ISSUER GRANT AND END-TO-END CERTIFICATION: PENDING'
Write-Host 'PRODUCTION ACTIVATION: NO-GO'
