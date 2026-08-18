import ast
import hashlib
from pathlib import Path

path = Path(
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\runtime\universal_worker\drain.py"
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
    "629AA6B5D9269B3164A1524F3C176B2EA34CB4952A0D32F5E2EE4A7C6984FA78"
)

print(
    "WORKER DRAIN AST SHA256:",
    actual,
)

if actual != expected:

    raise SystemExit(
        "Worker Drain production authority changed unexpectedly."
    )
