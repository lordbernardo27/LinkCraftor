from pathlib import Path
import hashlib

P = Path(
    "backend/server/runtime/universal_job_submission.py"
)

EXPECTED_OLD_SHA = (
    "07BA2DA8C0A2CFA899DE696D7892652A0AA6D56939B364C8C6B7F0B741B05704"
)

before = P.read_bytes()
before_sha = hashlib.sha256(before).hexdigest().upper()

if before_sha != EXPECTED_OLD_SHA:
    raise SystemExit(
        "CORRECTION REFUSED: universal_job_submission.py "
        f"SHA mismatch: {before_sha}"
    )

S = before.decode("utf-8")

old_import = '''from backend.server.runtime.universal_jobs.creation_engine import (
    UniversalJobCreationResult,
    create_universal_job,
)
'''

new_import = '''from backend.server.runtime.universal_jobs.creation_engine import (
    UniversalJobCreationResult,
    create_universal_job,
)
from backend.server.runtime.universal_jobs.priority import (
    UniversalJobPriorityError,
    normalize_universal_job_priority,
)
'''

if old_import not in S:
    raise SystemExit(
        "CORRECTION REFUSED: expected import anchor not found."
    )

S = S.replace(
    old_import,
    new_import,
    1,
)

start = S.index(
    "def _canonical_orchestration_priority("
)

end = S.index(
    "\ndef _build_orchestration_metadata(",
    start,
)

old_helper = S[start:end]

new_helper = '''def _canonical_orchestration_priority(
    value: Any,
) -> int:
    """
    Project an already-normalized Universal Job priority into the
    current orchestration store's integer priority representation.

    Canonical priority semantics remain owned by Universal Job
    priority normalization. This boundary only converts the canonical
    priority member to the integer representation required by the
    orchestration store.
    """

    try:
        canonical_priority = (
            normalize_universal_job_priority(
                value
            )
        )

    except UniversalJobPriorityError as exc:
        raise UniversalJobSubmissionError(
            (
                "Canonical Universal Job priority cannot be "
                "projected into the orchestration integer "
                "priority field."
            ),
            code="invalid_orchestration_priority",
        ) from exc

    return int(
        canonical_priority
    )


'''

S = (
    S[:start]
    + new_helper
    + S[end + 1:]
)

P.write_text(
    S,
    encoding="utf-8",
)

after_sha = hashlib.sha256(
    P.read_bytes()
).hexdigest().upper()

print("CONTROLLED PRIORITY PROJECTION CORRECTION INSTALLED")
print("Historical SHA:", before_sha)
print("Corrected SHA :", after_sha)
print("File          :", P)
