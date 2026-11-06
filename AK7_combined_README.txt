LinkCraftor AK.7 — Combined Isolated Development Certification

Copy ak7_combined_dev_certification.py into the existing LinkCraftor repository root.
With your .venv active run:

  python .\ak7_combined_dev_certification.py

The runner checks currently installed source guards and syntax, runs the three
existing AK.6 test suites, and tests SQLite nonce claim/pre-execute/dispatch,
replay rejection, revocation and process restart through separate Python processes.
It writes AK7_COMBINED_DEVELOPMENT_CERTIFICATION.json.

This batch DOES NOT provision a real issuer or authenticate a production worker.
It never starts the worker, changes runtime code, accesses live jobs, activates
queue claims or authorizes production. Passing cannot complete AK.6 or AK.7
production certification. Windows service provisioning has been deliberately
excluded: the actual existing Universal Runtime Worker is Python-based and
a Windows service executable does not exist. Align production identity with
the eventual AWS hosting environment before operational activation.
