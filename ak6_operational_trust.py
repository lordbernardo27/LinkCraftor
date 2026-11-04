"""AK.6 operational trust extension for canonical Connected Domain jobs.

Production is fail-closed unless an administrator provisions the machine trust
root, a dedicated Windows worker security principal, and an external issuer.
The worker never creates signing keys or grants.

Three-step durable grant protocol:
  claim       reserve unique nonce before queue mutation (fail closed on failure)
  pre_execute verify reserved nonce before outer execution mutates job state
  dispatch    atomically consume reserved nonce before invoking the handler

A failed claim may strand a nonce. This is intentional; issue a fresh grant
rather than weakening the at-most-once authorization invariant.
"""
from __future__ import annotations

import base64
import ctypes
import hmac
import os
import sqlite3
from contextlib import closing
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_TRUST = Path(r'C:\ProgramData\LinkCraftor\AK6\authority')
_LEDGER = Path(r'C:\ProgramData\LinkCraftor\AK6\state\grants.sqlite3')
_ISSUER_KEY = 'issuer_ed25519_public.b64'
_WORKER_SID = 'worker_token_sid.txt'


def _current_token_sid():
    """Get token USER SID from the Windows kernel; never from caller arguments."""
    if sys.platform != 'win32':
        raise PermissionError('AK6_DENY_WINDOWS_SERVICE_REQUIRED')
    from ctypes import wintypes
    advapi = ctypes.WinDLL('advapi32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    advapi.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    advapi.OpenProcessToken.restype = wintypes.BOOL
    advapi.GetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    advapi.GetTokenInformation.restype = wintypes.BOOL
    advapi.ConvertSidToStringSidW.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.LPWSTR)]
    advapi.ConvertSidToStringSidW.restype = wintypes.BOOL
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.LocalFree.argtypes = [wintypes.HLOCAL]
    kernel.LocalFree.restype = wintypes.HLOCAL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    token = wintypes.HANDLE()
    TOKEN_QUERY = 0x0008
    if not advapi.OpenProcessToken(kernel.GetCurrentProcess(), TOKEN_QUERY, ctypes.byref(token)):
        raise PermissionError('AK6_DENY_PROCESS_TOKEN')
    try:
        needed = wintypes.DWORD()
        advapi.GetTokenInformation(token, 1, None, 0, ctypes.byref(needed))
        if not 0 < needed.value <= 16384:
            raise PermissionError('AK6_DENY_TOKEN_LENGTH')
        buff = ctypes.create_string_buffer(needed.value)
        if not advapi.GetTokenInformation(token, 1, buff, needed, ctypes.byref(needed)):
            raise PermissionError('AK6_DENY_TOKEN_INFO')
        sid_pointer = ctypes.cast(buff, ctypes.POINTER(ctypes.c_void_p))[0]
        string_sid = wintypes.LPWSTR()
        if not advapi.ConvertSidToStringSidW(sid_pointer, ctypes.byref(string_sid)):
            raise PermissionError('AK6_DENY_TOKEN_SID')
        try:
            return string_sid.value
        finally:
            kernel.LocalFree(string_sid)
    finally:
        kernel.CloseHandle(token)


def _require_protected_authority_dir(path):
    """Check Windows ACLs for authority root and files; error => deny.

    Authority must be provisioned by local administrator, allow modifications
    only for SYSTEM/Administrators, and allow worker READ only. The rule is
    conservative: unknown write grants are denied.
    """
    if sys.platform != 'win32':
        raise PermissionError('AK6_DENY_WINDOWS_SERVICE_REQUIRED')
    script = r'''
$ErrorActionPreference='Stop'
$p=$args[0]
$a=Get-Acl -LiteralPath $p
$owner=$a.Owner
if ($owner -notmatch '(?i)(Administrators|SYSTEM|S-1-5-32-544|S-1-5-18)') { throw 'AK6 untrusted ACL owner' }
if (-not $a.AreAccessRulesProtected) { throw 'AK6 ACL inheritance is enabled' }
foreach($r in $a.Access) {
  if ($r.AccessControlType -ne [System.Security.AccessControl.AccessControlType]::Allow) { continue }
  $writeBits=[System.Security.AccessControl.FileSystemRights]::Write -bor
    [System.Security.AccessControl.FileSystemRights]::Modify -bor
    [System.Security.AccessControl.FileSystemRights]::FullControl -bor
    [System.Security.AccessControl.FileSystemRights]::ChangePermissions -bor
    [System.Security.AccessControl.FileSystemRights]::TakeOwnership
  if (($r.FileSystemRights -band $writeBits) -ne 0) {
    if ([string]$r.IdentityReference -notmatch '(?i)(^NT AUTHORITY\\SYSTEM$|^BUILTIN\\Administrators$|^S-1-5-18$|^S-1-5-32-544$)') {
      throw ('AK6 unauthorized write principal: '+$r.IdentityReference)
    }
  }
}
'PASS'
'''
    try:
        r = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive',
                            '-Command', script, str(path)],
                           capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PermissionError('AK6_DENY_ACL_INSPECTION_UNAVAILABLE') from exc
    if r.returncode or r.stdout.strip() != 'PASS':
        raise PermissionError('AK6_DENY_AUTHORITY_ACL')


def _require_protected_state_dir(path, allowed_sid):
    """Ensure the state directory has no inherited or broadly writable ACL."""
    if sys.platform != 'win32':
        raise PermissionError('AK6_DENY_WINDOWS_SERVICE_REQUIRED')
    script = r'''
$ErrorActionPreference='Stop'
$a=Get-Acl -LiteralPath $args[0]
$allowed=$args[1]
if (-not $a.AreAccessRulesProtected) { throw 'AK6 state ACL inherits permissions' }
foreach ($r in $a.Access) {
  if ($r.AccessControlType -ne [System.Security.AccessControl.AccessControlType]::Allow) { continue }
  $writeBits=[System.Security.AccessControl.FileSystemRights]::Write -bor
    [System.Security.AccessControl.FileSystemRights]::Modify -bor
    [System.Security.AccessControl.FileSystemRights]::FullControl
  if (($r.FileSystemRights -band $writeBits) -ne 0) {
    $id=[string]$r.IdentityReference
    try {
      $sid=($r.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier])).Value
    } catch { throw ('AK6 state ACL principal cannot be resolved: '+$id) }
    if ($sid -notin @('S-1-5-18','S-1-5-32-544',$allowed)) {
      throw ('AK6 unauthorized state writer: '+$id)
    }
  }
}
'PASS'
'''
    try:
        result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive',
                                 '-Command', script, str(path), allowed_sid],
                                capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PermissionError('AK6_DENY_STATE_ACL_UNAVAILABLE') from exc
    if result.returncode or result.stdout.strip() != 'PASS':
        raise PermissionError('AK6_DENY_STATE_ACL')


def _trusted_context(*, public_key_bytes, trust_dir=None, worker_sid_provider=None):
    """Compare signed grant's verifier key with protected, machine-pinned key.

    Override parameters exist for isolated testing only. Production callers
    MUST invoke without overrides; the public integration has no such inputs.
    """
    root = _TRUST if trust_dir is None else Path(trust_dir)
    if trust_dir is None:
        for path in (root, root / _ISSUER_KEY, root / _WORKER_SID):
            _require_protected_authority_dir(path)
    try:
        pinned = base64.b64decode((root / _ISSUER_KEY).read_text(encoding='ascii').strip(), validate=True)
        allowed_sid = (root / _WORKER_SID).read_text(encoding='ascii').strip()
    except (OSError, ValueError) as exc:
        raise PermissionError('AK6_DENY_AUTHORITY_NOT_PROVISIONED') from exc
    if len(pinned) != 32 or not allowed_sid.startswith('S-1-5-') or len(allowed_sid) > 150:
        raise PermissionError('AK6_DENY_AUTHORITY_CONFIG')
    actual_sid = (worker_sid_provider or _current_token_sid)()
    if not isinstance(actual_sid, str) or not hmac.compare_digest(allowed_sid, actual_sid):
        raise PermissionError('AK6_DENY_UNAUTHENTICATED_WORKER')
    if not hmac.compare_digest(pinned, public_key_bytes):
        raise PermissionError('AK6_DENY_UNTRUSTED_ISSUER_KEY')
    return actual_sid


def _ledger_step(*, ledger, nonce, job_id, worker_sid, phase, expires_at, lease_id):
    if phase not in ('claim', 'pre_execute', 'dispatch'):
        raise PermissionError('AK6_DENY_PHASE')
    if not isinstance(nonce, str) or len(nonce) < 32 or len(nonce) > 512:
        raise PermissionError('AK6_DENY_NONCE')
    if not isinstance(job_id, str) or not isinstance(worker_sid, str):
        raise PermissionError('AK6_DENY_LEDGER_IDENTITY')
    if type(expires_at) is not int:
        raise PermissionError('AK6_DENY_LEDGER_EXPIRY')
    from time import time
    if int(time()) >= expires_at:
        raise PermissionError('AK6_DENY_LEDGER_EXPIRED')
    # The ledger directory must be restricted to the dedicated worker and admins.
    # The database is NOT supplied by the job, env or a caller.
    try:
        with closing(sqlite3.connect(str(ledger), timeout=5, isolation_level=None)) as db:
            db.execute('PRAGMA busy_timeout=5000')
            db.execute('PRAGMA synchronous=FULL')
            db.execute('BEGIN IMMEDIATE')
            db.execute('''CREATE TABLE IF NOT EXISTS grant_ledger (
                nonce TEXT PRIMARY KEY, job_id TEXT NOT NULL, worker_sid TEXT NOT NULL,
                expires_at INTEGER NOT NULL, state TEXT NOT NULL,
                lease_id TEXT, revoked INTEGER NOT NULL DEFAULT 0,
                changed_utc TEXT NOT NULL)''')
            row = db.execute('SELECT job_id,worker_sid,expires_at,state,lease_id,revoked '
                             'FROM grant_ledger WHERE nonce=?', (nonce,)).fetchone()
            now = datetime.now(timezone.utc).isoformat()
            if phase == 'claim':
                if row is not None:
                    raise PermissionError('AK6_DENY_NONCE_REPLAY')
                db.execute('INSERT INTO grant_ledger VALUES (?,?,?,?,?,?,?,?)',
                           (nonce, job_id, worker_sid, expires_at, 'reserved', None, 0, now))
            else:
                if row is None:
                    raise PermissionError('AK6_DENY_UNRESERVED_GRANT')
                j, sid, exp, state, stored_lease, revoked = row
                if (revoked or j != job_id or sid != worker_sid or exp != expires_at
                    or state != 'reserved'):
                    raise PermissionError('AK6_DENY_REPLAY_REVOKED_OR_MISMATCH')
                if not isinstance(lease_id, str) or not lease_id:
                    raise PermissionError('AK6_DENY_MISSING_LEASE')
                if stored_lease not in (None, lease_id):
                    raise PermissionError('AK6_DENY_LEASE_MISMATCH')
                if phase == 'pre_execute':
                    db.execute('UPDATE grant_ledger SET lease_id=?,changed_utc=? WHERE nonce=?',
                               (lease_id, now, nonce))
                else:
                    if stored_lease != lease_id:
                        raise PermissionError('AK6_DENY_LEASE_NOT_BOUND')
                    db.execute('UPDATE grant_ledger SET state=?,changed_utc=? WHERE nonce=?',
                               ('consumed', now, nonce))
            db.execute('COMMIT')
    except PermissionError:
        raise
    except (sqlite3.Error, OSError) as exc:
        raise PermissionError('AK6_DENY_LEDGER_UNAVAILABLE') from exc


def require_operational_ak6_trust(*, job, worker_id, action, phase, payload, public_key_bytes,
                                  nonce):
    """Production enforcement; accepts no caller-supplied identity, ledger or trust root."""
    from collections.abc import Mapping
    if action not in ('claim', 'execute') or worker_id != 'universal_runtime_worker_v1':
        raise PermissionError('AK6_DENY_ACTION_OR_WORKER')
    if action == 'claim' and phase != 'claim':
        raise PermissionError('AK6_DENY_CLAIM_PHASE')
    if action == 'execute' and phase not in ('pre_execute', 'dispatch'):
        raise PermissionError('AK6_DENY_EXECUTION_PHASE')
    if not isinstance(payload, Mapping) or not isinstance(job, Mapping) and action == 'execute':
        raise PermissionError('AK6_DENY_OPERATIONAL_INPUT')
    worker_sid = _trusted_context(public_key_bytes=public_key_bytes)
    if not _LEDGER.parent.is_dir():
        raise PermissionError('AK6_DENY_LEDGER_NOT_PROVISIONED')
    _require_protected_state_dir(_LEDGER.parent, worker_sid)
    # worker needs write access to its state directory, but others must not.
    # Admin-led deployment must ensure this ACL; this check requires a dedicated
    # ops attestation for ledger ACL before GO (AK.7).
    metadata = job.get('metadata', {}) if isinstance(job, Mapping) else getattr(job, 'metadata', {})
    lease_id = metadata.get('lease_id') if isinstance(metadata, Mapping) else None
    _ledger_step(ledger=_LEDGER, nonce=nonce, job_id=payload['job_id'],
                 worker_sid=worker_sid, phase=phase, expires_at=payload['expires_at'],
                 lease_id=lease_id)
    return nonce
