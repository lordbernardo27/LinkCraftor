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

digest = hashlib.sha256(
    canonical.encode("utf-8")
).hexdigest().upper()

print(
    "PATCHED STALE WORKER AST SHA256:",
    digest,
)
