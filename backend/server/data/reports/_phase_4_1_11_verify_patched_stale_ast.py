import ast
import hashlib
from pathlib import Path

path = Path(
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\runtime\universal_worker\stale.py"
)

source = path.read_text(
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

actual = hashlib.sha256(
    canonical.encode("utf-8")
).hexdigest().upper()

expected = (
    "22105ACBF984E26019080E53939617CE14BDF51BF5A9B149BD39E10B6B87B9DD"
)

print(
    "STALE WORKER AST SHA256:",
    actual,
)

if actual != expected:
    raise SystemExit(
        "Production Stale Worker AST changed unexpectedly."
    )
