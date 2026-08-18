from __future__ import annotations

import ast
import hashlib
from pathlib import Path


path = Path(
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\runtime\universal_worker\capability.py"
)

expected = (
    "200A42478283CDAC92965EAF0DEDFAB3FAB8834F5FB734E3A4874F1EE571C51D"
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


print(
    "WORKER CAPABILITY AST SHA256:",
    actual,
)


if actual != expected:

    raise SystemExit(
        (
            "Worker Capability production authority "
            "changed unexpectedly.\n"
            "EXPECTED: "
            + expected
            + "\nACTUAL:   "
            + actual
        )
    )


print(
    "WORKER CAPABILITY PRODUCTION AST: UNCHANGED"
)
