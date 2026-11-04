AK.6 trusted authority discovery — corrected guard verification

Fix: Previous version counted the guard definition plus two call sites and incorrectly expected 2 occurrences. This version uses AST to check the first executable statement in each protected handler entry point.

Extract ak6_authority_discovery.py into the LinkCraftor project root, overwriting the previous discovery script only. Run: python .\ak6_authority_discovery.py

This is read-only with respect to production source and job execution. It creates a discovery JSON report. It does not establish production authorization.
