from pathlib import Path
import re

path = Path(
    "backend/server/workers/universal_knowledge_queue_runner.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)

#
# ------------------------------------------------------------------
# Remove record_job_failure import
# ------------------------------------------------------------------
#

text = re.sub(
    r"\s*record_job_failure,\r?\n",
    "",
    text,
    count=1,
)

#
# ------------------------------------------------------------------
# Replace exception block
# ------------------------------------------------------------------
#

old = re.compile(
    r"""
except\ Exception\ as\ e:
.*?
finally:
""",
    re.DOTALL | re.VERBOSE,
)

new = """except Exception as e:
        result = {
            "ok": False,
            "job_id": job_id,
            "workspace_id": ws,
            "job_type": jt,
            "error": str(e),
        }
    finally:
"""

text, count = old.subn(
    new,
    text,
    count=1,
)

if count != 1:
    raise RuntimeError(
        "Could not replace exception block."
    )

#
# ------------------------------------------------------------------
# Add completion progress
# ------------------------------------------------------------------
#

marker = """
    result["lease_finished_at"] = job.get("lease_finished_at")
"""

replacement = """
    update_job_progress(
        workspace_id=ws,
        job_id=job_id,
        percent=100,
        message="Queue runner finished.",
        step="runner_finished",
    )

    result["lease_finished_at"] = job.get("lease_finished_at")
"""

if marker not in text:
    raise RuntimeError(
        "Completion marker not found."
    )

text = text.replace(
    marker,
    replacement,
    1,
)

#
# ------------------------------------------------------------------
# Freeze priority
# ------------------------------------------------------------------
#

text = text.replace(
    "DEFAULT_PRIORITY = 999",
    "DEFAULT_PRIORITY = 1000",
)

path.write_text(
    text,
    encoding="utf-8",
)

print("PHASE 3E REVIEW PATCH: PASS")
