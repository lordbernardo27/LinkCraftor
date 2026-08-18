from pathlib import Path

path = Path(
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\data\reports\_phase_4_1_11_stale_worker_regression_runner.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)

old = '''check(
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.heartbeat",
    ],
    backend_imports,
)
'''

new = '''check(
    "backend_imports_exact",
    backend_imports
    == [
        "backend.server.runtime.universal_worker.heartbeat",
        "backend.server.runtime.universal_worker.registration",
    ],
    backend_imports,
)
'''

if old not in text:
    raise SystemExit(
        "Expected backend_imports_exact block not found. "
        "Regression runner was not modified."
    )

text = text.replace(
    old,
    new,
    1,
)

path.write_text(
    text,
    encoding="utf-8",
)

print(
    "4.1.11 regression import expectation updated."
)
