import ast
import hashlib
import re
from pathlib import Path

root = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
)

stale_path = (
    root
    / "backend"
    / "server"
    / "runtime"
    / "universal_worker"
    / "stale.py"
)

runner_path = (
    root
    / "backend"
    / "server"
    / "data"
    / "reports"
    / "_phase_4_1_11_stale_worker_regression_runner.py"
)

source = stale_path.read_text(
    encoding="utf-8-sig"
)

tree = ast.parse(
    source
)

canonical = ast.dump(
    tree,
    annotate_fields=True,
    include_attributes=False,
)

new_ast = hashlib.sha256(
    canonical.encode("utf-8")
).hexdigest().upper()

runner = runner_path.read_text(
    encoding="utf-8-sig"
)

pattern = re.compile(
    r'EXPECTED_STALE_AST = \(\s*"[A-F0-9]{64}"\s*\)',
    re.MULTILINE,
)

replacement = (
    'EXPECTED_STALE_AST = (\n'
    '    "'
    + new_ast
    + '"\n'
    ')'
)

updated, count = pattern.subn(
    replacement,
    runner,
    count=1,
)

if count != 1:
    raise SystemExit(
        "Could not update EXPECTED_STALE_AST "
        "in adversarial regression runner."
    )

runner_path.write_text(
    updated,
    encoding="utf-8",
)

print(
    "Regression runner expected AST updated to:",
    new_ast,
)
