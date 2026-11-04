# Administrator-only, manual, no private signing key is created or imported.
# Run only after a dedicated non-interactive Windows service account exists.
param(
  [Parameter(Mandatory=$true)][string]$WorkerAccount,
  [Parameter(Mandatory=$true)][string]$PublicKeyB64File
)
$ErrorActionPreference = 'Stop'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  throw 'STOP: run elevated as Administrator'
}
try {
  $workerSid = (New-Object System.Security.Principal.NTAccount($WorkerAccount)).Translate(
    [System.Security.Principal.SecurityIdentifier]).Value
} catch { throw 'STOP: dedicated worker account does not exist' }
if ($workerSid -eq $identity.User.Value) { throw 'STOP: interactive administrator cannot be the worker identity' }
if (-not $workerSid.StartsWith('S-1-5-')) { throw 'STOP: invalid service account SID' }
$keyString = (Get-Content -LiteralPath $PublicKeyB64File -Raw).Trim()
try { $key = [Convert]::FromBase64String($keyString) } catch { throw 'STOP: invalid public key' }
if ($key.Length -ne 32) { throw 'STOP: expected Ed25519 32-byte public key' }
$root = 'C:\ProgramData\LinkCraftor\AK6'
$authority = Join-Path $root 'authority'
$state = Join-Path $root 'state'
$keyTarget = Join-Path $authority 'issuer_ed25519_public.b64'
$sidTarget = Join-Path $authority 'worker_token_sid.txt'
if ((Test-Path $keyTarget) -or (Test-Path $sidTarget)) {
  throw 'STOP: trust anchor already provisioned; rotation requires separate reviewed procedure'
}
New-Item -ItemType Directory -Force -Path $root,$authority,$state | Out-Null
# The authority directory and children are writable only by OS administrators.
# The dedicated worker receives read access to authority, modify to state.
& icacls.exe $authority /inheritance:r /grant:r 'SYSTEM:(OI)(CI)F' 'Administrators:(OI)(CI)F' "${WorkerAccount}:(OI)(CI)R" | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'STOP: authority ACL failed' }
& icacls.exe $state /inheritance:r /grant:r 'SYSTEM:(OI)(CI)F' 'Administrators:(OI)(CI)F' "${WorkerAccount}:(OI)(CI)M" | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'STOP: state ACL failed' }
[IO.File]::WriteAllText($keyTarget, $keyString, [Text.Encoding]::ASCII)
[IO.File]::WriteAllText($sidTarget, $workerSid, [Text.Encoding]::ASCII)
foreach ($file in @($keyTarget,$sidTarget)) {
  & icacls.exe $file /inheritance:r /grant:r 'SYSTEM:F' 'Administrators:F' "${WorkerAccount}:R" | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'STOP: authority file ACL failed' }
}
Write-Host 'AK.6 MACHINE TRUST: PROVISIONED (local ACL configuration only)'
Write-Host "Dedicated worker SID: $workerSid"
Write-Host 'EXTERNAL ISSUER PRIVATE KEY: NOT STORED HERE'
Write-Host 'WORKER SERVICE CONFIGURATION / IDENTITY: MUST BE VERIFIED SEPARATELY'
Write-Host 'PRODUCTION ACTIVATION: NO-GO'
