from pathlib import Path
import re

path = Path(
    "backend/server/workers/universal_knowledge_queue_runner.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)

required_imports = """
from datetime import datetime, timezone
import uuid
"""

if "import uuid" not in text:
    text = required_imports + "\n" + text


scheduler_helpers = """

def _queue_priority(job):
    return int(job.get("priority",999))


def _claim_lease(job):
    job["lease_owner"] = str(uuid.uuid4())
    job["lease_started_at"] = datetime.now(
        timezone.utc
    ).isoformat()


def _release_lease(job):
    job["lease_owner"] = None
    job["lease_finished_at"] = datetime.now(
        timezone.utc
    ).isoformat()


def _sort_queue(queue):
    return sorted(
        queue,
        key=_queue_priority
    )
"""

if "_queue_priority" not in text:
    text += scheduler_helpers


pattern = re.compile(
    r"queue\s*=\s*read_queue\([^)]*\)"
)

text = pattern.sub(
    "queue = _sort_queue(read_queue())",
    text,
    count=1
)

path.write_text(
    text,
    encoding="utf-8"
)

print("QUEUE PATCH: PASS")
