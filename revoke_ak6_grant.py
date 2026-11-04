"""Privileged AK.6 grant nonce revocation; invoke from admin-only console.

Does not enable production. Run on the host holding the operational ledger.
For a nonce not yet reserved, create a permanent tombstone to block future use.
"""
from __future__ import annotations
import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

LEDGER = Path(r'C:\ProgramData\LinkCraftor\AK6\state\grants.sqlite3')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--nonce',required=True)
    args=parser.parse_args()
    if sys.platform!='win32':
        raise SystemExit('STOP: Windows-only operational command')
    if not 32 <= len(args.nonce) <= 512:
        raise SystemExit('STOP: invalid nonce length')
    if not LEDGER.is_file():
        raise SystemExit('STOP: ledger absent; no changes')
    from backend.server.runtime.security.ak6_operational_trust import _require_protected_state_dir
    from backend.server.runtime.security.ak6_operational_trust import _trusted_context
    # Administrator revocation is checked by the OS deployment boundary.
    # Verify state ACL independently using the configured worker token SID.
    worker_sid = Path(r"C:\ProgramData\LinkCraftor\AK6\authority\worker_token_sid.txt").read_text(encoding="ascii").strip()
    _require_protected_state_dir(LEDGER.parent, worker_sid)
    with sqlite3.connect(LEDGER, timeout=5, isolation_level=None) as cx:
        cx.execute('PRAGMA synchronous=FULL')
        cx.execute('BEGIN IMMEDIATE')
        cx.execute('''INSERT OR IGNORE INTO grant_ledger
            (nonce, job_id, worker_sid, expires_at, state, lease_id, revoked, changed_utc)
            VALUES (?, '', '', 0, 'revoked', NULL, 1, ?)''',
            (args.nonce,datetime.now(timezone.utc).isoformat()))
        cx.execute('UPDATE grant_ledger SET revoked=1, changed_utc=? WHERE nonce=?',
                   (datetime.now(timezone.utc).isoformat(),args.nonce))
        cx.execute('COMMIT')
    print('PASS: nonce revoked and durably recorded')

if __name__=='__main__':
    main()
