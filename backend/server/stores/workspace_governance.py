from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List
from backend.server.stores.upload_phrase_pool_builder import build_upload_phrase_pool
from backend.server.stores.active_phrase_pool_builder import build_active_phrase_pool
from backend.server.stores.reload_governance import queue_reload_event, process_reload_queue


INFO = "INFO"
HEALTHY = "HEALTHY"
WARNING = "WARNING"
STALE = "STALE"
DRIFTED = "DRIFTED"
REPAIR_REQUIRED = "REPAIR_REQUIRED"


GOVERNANCE_SEVERITY_ORDER = {
    INFO: 0,
    HEALTHY: 1,
    WARNING: 2,
    STALE: 3,
    DRIFTED: 4,
    REPAIR_REQUIRED: 5,
}


HEALTH_SCORE_RANGES = {
    INFO: {"min": 100, "max": 100},
    HEALTHY: {"min": 100, "max": 100},
    WARNING: {"min": 70, "max": 99},
    STALE: {"min": 40, "max": 69},
    DRIFTED: {"min": 20, "max": 39},
    REPAIR_REQUIRED: {"min": 0, "max": 19},
}


WORKSPACE_GOVERNANCE_RULES = {
    "statuses": [INFO, HEALTHY, WARNING, STALE, DRIFTED, REPAIR_REQUIRED],
    "severity_order": GOVERNANCE_SEVERITY_ORDER,
    "health_score_ranges": HEALTH_SCORE_RANGES,
    "automatic_sweep": {
        "enabled": True,
        "interval_seconds": 180,
        "blind_rebuild_allowed": False,
        "blind_reload_allowed": False,
        "blind_repair_allowed": False,
    },
    "status_actions": {
        HEALTHY: "no_action",
        WARNING: "log_warning",
        STALE: "recommend_reload_or_rebuild",
        DRIFTED: "queue_validation_or_repair",
        REPAIR_REQUIRED: "queue_repair_workflow",
    },
}


@dataclass(frozen=True)
class GovernanceIssue:
    code: str
    status: str
    message: str
    source: str = "workspace_governance"


@dataclass(frozen=True)
class GovernanceSummary:
    workspace_id: str
    status: str
    health_score: int
    issues: List[Dict[str, Any]]
    recommended_action: str
    checked_at: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def choose_most_severe_status(statuses: List[str]) -> str:
    if not statuses:
        return HEALTHY

    valid_statuses = [
        status for status in statuses
        if status in GOVERNANCE_SEVERITY_ORDER
    ]

    if not valid_statuses:
        return HEALTHY

    return max(
        valid_statuses,
        key=lambda status: GOVERNANCE_SEVERITY_ORDER[status],
    )


def score_for_status(status: str) -> int:
    if status == HEALTHY:
        return 100
    if status == WARNING:
        return 85
    if status == STALE:
        return 55
    if status == DRIFTED:
        return 30
    if status == REPAIR_REQUIRED:
        return 10
    return 0


def recommended_action_for_status(status: str) -> str:
    return WORKSPACE_GOVERNANCE_RULES["status_actions"].get(
        status,
        "unknown_action",
    )


def classify_workspace_status(issues: List[GovernanceIssue]) -> str:
    if not issues:
        return HEALTHY

    return choose_most_severe_status([issue.status for issue in issues])


def build_governance_summary(
    workspace_id: str,
    issues: List[GovernanceIssue] | None = None,
) -> Dict[str, Any]:
    issue_list = issues or []
    status = classify_workspace_status(issue_list)

    summary = GovernanceSummary(
        workspace_id=workspace_id,
        status=status,
        health_score=score_for_status(status),
        issues=[asdict(issue) for issue in issue_list],
        recommended_action=recommended_action_for_status(status),
        checked_at=utc_now_iso(),
    )

    return asdict(summary)


def get_workspace_governance_rules() -> Dict[str, Any]:
    return WORKSPACE_GOVERNANCE_RULES

from pathlib import Path
import json


WORKSPACE_GOVERNANCE_DATA_DIR = Path("backend/server/data/workspace_governance")


def ensure_workspace_governance_data_dir() -> Path:
    WORKSPACE_GOVERNANCE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return WORKSPACE_GOVERNANCE_DATA_DIR


def workspace_state_path(workspace_id: str) -> Path:
    safe_workspace_id = str(workspace_id or "").strip()
    if not safe_workspace_id:
        safe_workspace_id = "default"
    return ensure_workspace_governance_data_dir() / f"{safe_workspace_id}_state.json"


def default_workspace_state(workspace_id: str) -> Dict[str, Any]:
    now = utc_now_iso()
    return {
        "workspace_id": workspace_id,
        "current_status": HEALTHY,
        "health_score": 100,
        "last_checked_at": now,
        "last_validation_at": None,
        "last_repair_recommendation": None,
        "issues": [],
        "sweep_count": 0,
        "created_at": now,
        "updated_at": now,
    }


def load_workspace_state(workspace_id: str) -> Dict[str, Any]:
    path = workspace_state_path(workspace_id)

    if not path.exists():
        return default_workspace_state(workspace_id)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return default_workspace_state(workspace_id)
        return data
    except Exception:
        return default_workspace_state(workspace_id)


def save_workspace_state(workspace_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
    path = workspace_state_path(workspace_id)

    clean_state = dict(state or {})
    clean_state["workspace_id"] = workspace_id
    clean_state["updated_at"] = utc_now_iso()

    path.write_text(
        json.dumps(clean_state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return clean_state


def update_workspace_state(
    workspace_id: str,
    summary: Dict[str, Any],
    validation_at: str | None = None,
) -> Dict[str, Any]:
    previous = load_workspace_state(workspace_id)

    sweep_count = int(previous.get("sweep_count") or 0) + 1

    state = {
        **previous,
        "workspace_id": workspace_id,
        "current_status": summary.get("status", HEALTHY),
        "health_score": int(summary.get("health_score", 100) or 100),
        "last_checked_at": summary.get("checked_at") or utc_now_iso(),
        "last_validation_at": validation_at or previous.get("last_validation_at"),
        "last_repair_recommendation": summary.get("recommended_action"),
        "issues": summary.get("issues", []),
        "sweep_count": sweep_count,
        "updated_at": utc_now_iso(),
    }

    return save_workspace_state(workspace_id, state)


def file_info(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "exists": False,
            "modified_at": None,
            "size_bytes": 0,
        }

    stat = path.stat()
    return {
        "exists": True,
        "modified_at": datetime.fromtimestamp(
            stat.st_mtime,
            timezone.utc,
        ).isoformat(),
        "size_bytes": stat.st_size,
    }


def build_workspace_state_snapshot(workspace_id: str) -> Dict[str, Any]:
    workspace_id = str(workspace_id or "").strip()

    upload_struct_path = Path(f"backend/server/data/upload_struct_{workspace_id}.json")

    upload_phrase_pool_path = Path(
        f"backend/server/data/phrase_pools/upload/upload_phrase_pool_{workspace_id}.json"
    )

    active_phrase_set_path = Path(
        f"backend/server/data/phrase_pools/active/active_phrase_set_{workspace_id}.json"
    )

    active_phrase_pool_path = Path(
        f"backend/server/data/phrase_pools/active/active_phrase_pool_{workspace_id}.json"
    )

    target_pool_dir = Path("backend/server/data/target_pools")

    target_pool_files = []
    if target_pool_dir.exists():
        target_pool_files = [
            str(path)
            for path in target_pool_dir.glob(f"*{workspace_id}*.json")
            if path.is_file()
        ]

    snapshot = {
        "workspace_id": workspace_id,
        "snapshot_at": utc_now_iso(),
        "upload_structure": file_info(upload_struct_path),
        "upload_phrase_pool": file_info(upload_phrase_pool_path),
        "active_phrase_set": file_info(active_phrase_set_path),
        "active_phrase_pool": file_info(active_phrase_pool_path),
        "target_pools": {
            "directory_exists": target_pool_dir.exists(),
            "file_count": len(target_pool_files),
            "files": target_pool_files,
        },
    }

    return snapshot


def update_workspace_snapshot(workspace_id: str) -> Dict[str, Any]:
    state = load_workspace_state(workspace_id)
    snapshot = build_workspace_state_snapshot(workspace_id)

    state["last_snapshot"] = snapshot
    state["last_snapshot_at"] = snapshot.get("snapshot_at")
    state["updated_at"] = utc_now_iso()

    return save_workspace_state(workspace_id, state)


def status_from_health_score(score: int) -> str:
    score = int(score or 0)

    if score >= 100:
        return HEALTHY
    if score >= 70:
        return WARNING
    if score >= 40:
        return STALE
    if score >= 20:
        return DRIFTED
    return REPAIR_REQUIRED


def build_health_issues(snapshot: Dict[str, Any]) -> List[GovernanceIssue]:
    issues: List[GovernanceIssue] = []

    if not snapshot:
        issues.append(
            GovernanceIssue(
                code="snapshot_missing",
                status=REPAIR_REQUIRED,
                message="Workspace snapshot is missing.",
            )
        )
        return issues

    if not snapshot.get("upload_structure", {}).get("exists"):
        issues.append(
            GovernanceIssue(
                code="upload_structure_missing",
                status=REPAIR_REQUIRED,
                message="Upload structure file is missing.",
            )
        )

    if not snapshot.get("upload_phrase_pool", {}).get("exists"):
        issues.append(
            GovernanceIssue(
                code="upload_phrase_pool_missing",
                status=STALE,
                message="Upload phrase pool file is missing.",
            )
        )

    if not snapshot.get("active_phrase_set", {}).get("exists"):
        issues.append(
            GovernanceIssue(
                code="active_phrase_set_missing",
                status=DRIFTED,
                message="Active phrase set file is missing.",
            )
        )

    if not snapshot.get("active_phrase_pool", {}).get("exists"):
        issues.append(
            GovernanceIssue(
                code="active_phrase_pool_missing",
                status=DRIFTED,
                message="Active phrase pool file is missing.",
            )
        )

    target_pools = snapshot.get("target_pools", {}) or {}
    if not target_pools.get("directory_exists"):
        issues.append(
            GovernanceIssue(
                code="target_pool_directory_missing",
                status=WARNING,
                message="Target pool directory is missing.",
            )
        )
    elif int(target_pools.get("file_count") or 0) <= 0:
        issues.append(
            GovernanceIssue(
                code="target_pool_files_missing",
                status=WARNING,
                message="No target pool files were found for this workspace.",
            )
        )

    return issues


def health_score_from_snapshot(snapshot: Dict[str, Any]) -> int:
    score = 100

    if not snapshot:
        return 10

    if not snapshot.get("upload_structure", {}).get("exists"):
        score -= 50

    if not snapshot.get("upload_phrase_pool", {}).get("exists"):
        score -= 30

    if not snapshot.get("active_phrase_set", {}).get("exists"):
        score -= 30

    if not snapshot.get("active_phrase_pool", {}).get("exists"):
        score -= 30

    target_pools = snapshot.get("target_pools", {}) or {}
    if not target_pools.get("directory_exists"):
        score -= 10
    elif int(target_pools.get("file_count") or 0) <= 0:
        score -= 10

    return max(0, min(100, score))


def evaluate_workspace_health(workspace_id: str) -> Dict[str, Any]:
    snapshot = build_workspace_state_snapshot(workspace_id)
    issues = build_health_issues(snapshot)
    health_score = health_score_from_snapshot(snapshot)

    issue_status = classify_workspace_status(issues)
    score_status = status_from_health_score(health_score)

    final_status = choose_most_severe_status([issue_status, score_status])

    return {
        "workspace_id": workspace_id,
        "status": final_status,
        "health_score": health_score,
        "issues": [asdict(issue) for issue in issues],
        "recommended_action": recommended_action_for_status(final_status),
        "checked_at": utc_now_iso(),
        "snapshot": snapshot,
    }


def update_workspace_health(workspace_id: str) -> Dict[str, Any]:
    health = evaluate_workspace_health(workspace_id)

    state = update_workspace_state(
        workspace_id=workspace_id,
        summary=health,
    )

    state["last_snapshot"] = health.get("snapshot")
    state["last_snapshot_at"] = health.get("snapshot", {}).get("snapshot_at")
    state["last_health"] = health
    state["last_health_at"] = health.get("checked_at")
    state["updated_at"] = utc_now_iso()

    return save_workspace_state(workspace_id, state)


def mark_workspace_validation(
    workspace_id: str,
    passed: bool,
    error: str | None = None,
) -> Dict[str, Any]:
    state = load_workspace_state(workspace_id)

    now = utc_now_iso()
    previous_count = int(state.get("validation_count") or 0)

    state["last_validation_at"] = now
    state["last_validation_status"] = "passed" if passed else "failed"
    state["last_validation_passed"] = bool(passed)
    state["validation_count"] = previous_count + 1

    if passed:
        state["last_validation_failed_at"] = state.get("last_validation_failed_at")
        state["last_validation_error"] = None
    else:
        state["last_validation_failed_at"] = now
        state["last_validation_error"] = str(error or "Validation failed.")

    state["updated_at"] = now

    return save_workspace_state(workspace_id, state)


def mark_workspace_validation_passed(workspace_id: str) -> Dict[str, Any]:
    return mark_workspace_validation(
        workspace_id=workspace_id,
        passed=True,
        error=None,
    )


def mark_workspace_validation_failed(
    workspace_id: str,
    error: str | None = None,
) -> Dict[str, Any]:
    return mark_workspace_validation(
        workspace_id=workspace_id,
        passed=False,
        error=error,
    )


def get_workspace_validation_state(workspace_id: str) -> Dict[str, Any]:
    state = load_workspace_state(workspace_id)

    return {
        "workspace_id": workspace_id,
        "last_validation_at": state.get("last_validation_at"),
        "last_validation_status": state.get("last_validation_status"),
        "last_validation_passed": state.get("last_validation_passed"),
        "last_validation_failed_at": state.get("last_validation_failed_at"),
        "last_validation_error": state.get("last_validation_error"),
        "validation_count": int(state.get("validation_count") or 0),
    }


def detect_upload_structure_drift(
    workspace_id: str,
) -> List[GovernanceIssue]:
    state = load_workspace_state(workspace_id)

    previous_snapshot = (
        state.get("last_snapshot") or {}
    )

    current_snapshot = build_workspace_state_snapshot(workspace_id)

    previous_upload = (
        previous_snapshot.get("upload_structure") or {}
    )

    current_upload = (
        current_snapshot.get("upload_structure") or {}
    )

    issues: List[GovernanceIssue] = []

    previous_exists = bool(previous_upload.get("exists"))
    current_exists = bool(current_upload.get("exists"))

    if previous_exists and not current_exists:
        issues.append(
            GovernanceIssue(
                code="upload_structure_missing_drift",
                status=DRIFTED,
                message="Upload structure existed previously but is now missing.",
            )
        )

    elif not previous_exists and current_exists:
        issues.append(
            GovernanceIssue(
                code="upload_structure_created_drift",
                status=INFO,
                message="Upload structure was previously missing but now exists.",
            )
        )

    previous_modified = previous_upload.get("modified_at")
    current_modified = current_upload.get("modified_at")

    if (
        previous_modified
        and current_modified
        and previous_modified != current_modified
    ):
        issues.append(
            GovernanceIssue(
                code="upload_structure_modified_drift",
                status=INFO,
                message="Upload structure modification timestamp changed.",
            )
        )

    previous_size = int(previous_upload.get("size_bytes") or 0)
    current_size = int(current_upload.get("size_bytes") or 0)

    if (
        previous_size > 0
        and current_size > 0
        and previous_size != current_size
    ):
        issues.append(
            GovernanceIssue(
                code="upload_structure_size_drift",
                status=INFO,
                message="Upload structure file size changed.",
            )
        )

    return issues


def detect_upload_phrase_pool_drift(
    workspace_id: str,
) -> List[GovernanceIssue]:
    state = load_workspace_state(workspace_id)

    previous_snapshot = state.get("last_snapshot") or {}
    current_snapshot = build_workspace_state_snapshot(workspace_id)

    previous_pool = previous_snapshot.get("upload_phrase_pool") or {}
    current_pool = current_snapshot.get("upload_phrase_pool") or {}

    issues: List[GovernanceIssue] = []

    previous_exists = bool(previous_pool.get("exists"))
    current_exists = bool(current_pool.get("exists"))

    if previous_exists and not current_exists:
        issues.append(
            GovernanceIssue(
                code="upload_phrase_pool_missing_drift",
                status=DRIFTED,
                message="Upload phrase pool existed previously but is now missing.",
            )
        )

    elif not previous_exists and current_exists:
        issues.append(
            GovernanceIssue(
                code="upload_phrase_pool_created_drift",
                status=INFO,
                message="Upload phrase pool was previously missing but now exists.",
            )
        )

    previous_modified = previous_pool.get("modified_at")
    current_modified = current_pool.get("modified_at")

    if (
        previous_modified
        and current_modified
        and previous_modified != current_modified
    ):
        issues.append(
            GovernanceIssue(
                code="upload_phrase_pool_modified_drift",
                status=INFO,
                message="Upload phrase pool modification timestamp changed.",
            )
        )

    previous_size = int(previous_pool.get("size_bytes") or 0)
    current_size = int(current_pool.get("size_bytes") or 0)

    if (
        previous_size > 0
        and current_size > 0
        and previous_size != current_size
    ):
        issues.append(
            GovernanceIssue(
                code="upload_phrase_pool_size_drift",
                status=INFO,
                message="Upload phrase pool file size changed.",
            )
        )

    return issues


def detect_active_phrase_set_drift(
    workspace_id: str,
) -> List[GovernanceIssue]:
    state = load_workspace_state(workspace_id)

    previous_snapshot = state.get("last_snapshot") or {}
    current_snapshot = build_workspace_state_snapshot(workspace_id)

    previous_set = previous_snapshot.get("active_phrase_set") or {}
    current_set = current_snapshot.get("active_phrase_set") or {}

    issues: List[GovernanceIssue] = []

    previous_exists = bool(previous_set.get("exists"))
    current_exists = bool(current_set.get("exists"))

    if previous_exists and not current_exists:
        issues.append(
            GovernanceIssue(
                code="active_phrase_set_missing_drift",
                status=DRIFTED,
                message="Active phrase set existed previously but is now missing.",
            )
        )

    elif not previous_exists and current_exists:
        issues.append(
            GovernanceIssue(
                code="active_phrase_set_created_drift",
                status=INFO,
                message="Active phrase set was previously missing but now exists.",
            )
        )

    previous_modified = previous_set.get("modified_at")
    current_modified = current_set.get("modified_at")

    if (
        previous_modified
        and current_modified
        and previous_modified != current_modified
    ):
        issues.append(
            GovernanceIssue(
                code="active_phrase_set_modified_drift",
                status=INFO,
                message="Active phrase set modification timestamp changed.",
            )
        )

    previous_size = int(previous_set.get("size_bytes") or 0)
    current_size = int(current_set.get("size_bytes") or 0)

    if (
        previous_size > 0
        and current_size > 0
        and previous_size != current_size
    ):
        issues.append(
            GovernanceIssue(
                code="active_phrase_set_size_drift",
                status=INFO,
                message="Active phrase set file size changed.",
            )
        )

    return issues


def detect_active_phrase_pool_drift(
    workspace_id: str,
) -> List[GovernanceIssue]:
    state = load_workspace_state(workspace_id)

    previous_snapshot = state.get("last_snapshot") or {}
    current_snapshot = build_workspace_state_snapshot(workspace_id)

    previous_pool = previous_snapshot.get("active_phrase_pool") or {}
    current_pool = current_snapshot.get("active_phrase_pool") or {}

    issues: List[GovernanceIssue] = []

    previous_exists = bool(previous_pool.get("exists"))
    current_exists = bool(current_pool.get("exists"))

    if previous_exists and not current_exists:
        issues.append(
            GovernanceIssue(
                code="active_phrase_pool_missing_drift",
                status=DRIFTED,
                message="Active phrase pool existed previously but is now missing.",
            )
        )

    elif not previous_exists and current_exists:
        issues.append(
            GovernanceIssue(
                code="active_phrase_pool_created_drift",
                status=INFO,
                message="Active phrase pool was previously missing but now exists.",
            )
        )

    previous_modified = previous_pool.get("modified_at")
    current_modified = current_pool.get("modified_at")

    if (
        previous_modified
        and current_modified
        and previous_modified != current_modified
    ):
        issues.append(
            GovernanceIssue(
                code="active_phrase_pool_modified_drift",
                status=INFO,
                message="Active phrase pool modification timestamp changed.",
            )
        )

    previous_size = int(previous_pool.get("size_bytes") or 0)
    current_size = int(current_pool.get("size_bytes") or 0)

    if (
        previous_size > 0
        and current_size > 0
        and previous_size != current_size
    ):
        issues.append(
            GovernanceIssue(
                code="active_phrase_pool_size_drift",
                status=INFO,
                message="Active phrase pool file size changed.",
            )
        )

    return issues


def detect_target_pool_drift(
    workspace_id: str,
) -> List[GovernanceIssue]:
    state = load_workspace_state(workspace_id)

    previous_snapshot = state.get("last_snapshot") or {}
    current_snapshot = build_workspace_state_snapshot(workspace_id)

    previous_target = previous_snapshot.get("target_pools") or {}
    current_target = current_snapshot.get("target_pools") or {}

    issues: List[GovernanceIssue] = []

    previous_dir_exists = bool(previous_target.get("directory_exists"))
    current_dir_exists = bool(current_target.get("directory_exists"))

    if previous_dir_exists and not current_dir_exists:
        issues.append(
            GovernanceIssue(
                code="target_pool_directory_missing_drift",
                status=DRIFTED,
                message="Target pool directory existed previously but is now missing.",
            )
        )

    elif not previous_dir_exists and current_dir_exists:
        issues.append(
            GovernanceIssue(
                code="target_pool_directory_created_drift",
                status=INFO,
                message="Target pool directory was previously missing but now exists.",
            )
        )

    previous_count = int(previous_target.get("file_count") or 0)
    current_count = int(current_target.get("file_count") or 0)

    if previous_count != current_count:
        issues.append(
            GovernanceIssue(
                code="target_pool_file_count_drift",
                status=INFO,
                message="Target pool file count changed.",
            )
        )

    previous_files = sorted(previous_target.get("files") or [])
    current_files = sorted(current_target.get("files") or [])

    if previous_files != current_files:
        issues.append(
            GovernanceIssue(
                code="target_pool_file_list_drift",
                status=INFO,
                message="Target pool file list changed.",
            )
        )

    return issues


def build_decision_cache_snapshot(workspace_id: str) -> Dict[str, Any]:
    decisions_log_path = Path("backend/server/data/decisions.jsonl")
    workspace_decisions_path = Path(
        f"backend/server/data/link_decisions/{workspace_id}.json"
    )

    return {
        "global_decisions_log": file_info(decisions_log_path),
        "workspace_link_decisions": file_info(workspace_decisions_path),
    }


def detect_decision_cache_drift(
    workspace_id: str,
) -> List[GovernanceIssue]:
    state = load_workspace_state(workspace_id)

    previous_snapshot = state.get("last_snapshot") or {}
    previous_cache = previous_snapshot.get("decision_cache") or {}

    current_cache = build_decision_cache_snapshot(workspace_id)

    issues: List[GovernanceIssue] = []

    cache_keys = [
        "global_decisions_log",
        "workspace_link_decisions",
    ]

    for key in cache_keys:
        previous_info = previous_cache.get(key) or {}
        current_info = current_cache.get(key) or {}

        previous_exists = bool(previous_info.get("exists"))
        current_exists = bool(current_info.get("exists"))

        if previous_exists and not current_exists:
            issues.append(
                GovernanceIssue(
                    code=f"{key}_missing_drift",
                    status=DRIFTED,
                    message=f"{key} existed previously but is now missing.",
                )
            )

        elif not previous_exists and current_exists:
            issues.append(
                GovernanceIssue(
                    code=f"{key}_created_drift",
                    status=INFO,
                    message=f"{key} was previously missing but now exists.",
                )
            )

        previous_modified = previous_info.get("modified_at")
        current_modified = current_info.get("modified_at")

        if (
            previous_modified
            and current_modified
            and previous_modified != current_modified
        ):
            issues.append(
                GovernanceIssue(
                    code=f"{key}_modified_drift",
                    status=INFO,
                    message=f"{key} modification timestamp changed.",
                )
            )

        previous_size = int(previous_info.get("size_bytes") or 0)
        current_size = int(current_info.get("size_bytes") or 0)

        if (
            previous_size > 0
            and current_size > 0
            and previous_size != current_size
        ):
            issues.append(
                GovernanceIssue(
                    code=f"{key}_size_drift",
                    status=INFO,
                    message=f"{key} file size changed.",
                )
            )

    return issues


def generate_workspace_drift_report(workspace_id: str) -> Dict[str, Any]:
    issues: List[GovernanceIssue] = []

    issues.extend(detect_upload_structure_drift(workspace_id))
    issues.extend(detect_upload_phrase_pool_drift(workspace_id))
    issues.extend(detect_active_phrase_set_drift(workspace_id))
    issues.extend(detect_active_phrase_pool_drift(workspace_id))
    issues.extend(detect_target_pool_drift(workspace_id))
    issues.extend(detect_decision_cache_drift(workspace_id))

    blocking_issues = [
        issue for issue in issues
        if issue.status in {DRIFTED, REPAIR_REQUIRED}
    ]

    info_issues = [
        issue for issue in issues
        if issue.status == INFO
    ]

    drift_detected = len(blocking_issues) > 0
    info_detected = len(info_issues) > 0

    status = classify_workspace_status(blocking_issues)

    if not drift_detected:
        status = HEALTHY

    report = {
        "workspace_id": workspace_id,
        "status": status,
        "health_score": score_for_status(status),
        "drift_detected": drift_detected,
        "info_detected": info_detected,
        "issue_count": len(issues),
        "blocking_issue_count": len(blocking_issues),
        "info_issue_count": len(info_issues),
        "issues": [asdict(issue) for issue in issues],
        "recommended_action": recommended_action_for_status(status),
        "checked_at": utc_now_iso(),
    }

    state = update_workspace_state(
        workspace_id=workspace_id,
        summary=report,
    )

    state["last_drift_report"] = report
    state["last_drift_checked_at"] = report.get("checked_at")
    state["last_drift_detected"] = drift_detected
    state["updated_at"] = utc_now_iso()

    save_workspace_state(workspace_id, state)

    return report


def parse_governance_datetime(value: str | None):
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def is_datetime_newer(left: str | None, right: str | None) -> bool:
    left_dt = parse_governance_datetime(left)
    right_dt = parse_governance_datetime(right)

    if not left_dt or not right_dt:
        return False

    return left_dt > right_dt


def detect_stale_upload_structure(
    workspace_id: str,
) -> List[GovernanceIssue]:
    state = load_workspace_state(workspace_id)
    snapshot = build_workspace_state_snapshot(workspace_id)

    upload_info = snapshot.get("upload_structure") or {}
    upload_modified_at = upload_info.get("modified_at")

    last_validation_at = state.get("last_validation_at")
    last_snapshot_at = state.get("last_snapshot_at")

    issues: List[GovernanceIssue] = []

    if is_datetime_newer(upload_modified_at, last_validation_at):
        issues.append(
            GovernanceIssue(
                code="stale_upload_structure_validation",
                status=STALE,
                message="Upload structure was modified after the last validation.",
            )
        )

    if is_datetime_newer(upload_modified_at, last_snapshot_at):
        issues.append(
            GovernanceIssue(
                code="stale_upload_structure_snapshot",
                status=STALE,
                message="Upload structure was modified after the last saved snapshot.",
            )
        )

    return issues


def detect_stale_upload_phrase_pool(
    workspace_id: str,
) -> List[GovernanceIssue]:
    snapshot = build_workspace_state_snapshot(workspace_id)

    upload_structure = snapshot.get("upload_structure") or {}
    upload_phrase_pool = snapshot.get("upload_phrase_pool") or {}

    upload_structure_modified_at = upload_structure.get("modified_at")
    upload_phrase_pool_modified_at = upload_phrase_pool.get("modified_at")

    issues: List[GovernanceIssue] = []

    if is_datetime_newer(
        upload_structure_modified_at,
        upload_phrase_pool_modified_at,
    ):
        issues.append(
            GovernanceIssue(
                code="stale_upload_phrase_pool_from_upload_structure",
                status=STALE,
                message="Upload phrase pool is older than the upload structure.",
            )
        )

    return issues


def detect_stale_active_phrase_set(
    workspace_id: str,
) -> List[GovernanceIssue]:
    snapshot = build_workspace_state_snapshot(workspace_id)

    upload_phrase_pool = snapshot.get("upload_phrase_pool") or {}
    active_phrase_set = snapshot.get("active_phrase_set") or {}

    upload_phrase_pool_modified_at = upload_phrase_pool.get("modified_at")
    active_phrase_set_modified_at = active_phrase_set.get("modified_at")

    issues: List[GovernanceIssue] = []

    if is_datetime_newer(
        upload_phrase_pool_modified_at,
        active_phrase_set_modified_at,
    ):
        issues.append(
            GovernanceIssue(
                code="stale_active_phrase_set_from_upload_phrase_pool",
                status=STALE,
                message="Active phrase set is older than the upload phrase pool.",
            )
        )

    return issues


def detect_stale_active_phrase_pool(
    workspace_id: str,
) -> List[GovernanceIssue]:
    snapshot = build_workspace_state_snapshot(workspace_id)

    active_phrase_set = snapshot.get("active_phrase_set") or {}
    active_phrase_pool = snapshot.get("active_phrase_pool") or {}

    active_phrase_set_modified_at = active_phrase_set.get("modified_at")
    active_phrase_pool_modified_at = active_phrase_pool.get("modified_at")

    issues: List[GovernanceIssue] = []

    if is_datetime_newer(
        active_phrase_set_modified_at,
        active_phrase_pool_modified_at,
    ):
        issues.append(
            GovernanceIssue(
                code="stale_active_phrase_pool_from_active_phrase_set",
                status=STALE,
                message="Active phrase pool is older than the active phrase set.",
            )
        )

    return issues


def detect_stale_target_pools(
    workspace_id: str,
) -> List[GovernanceIssue]:
    snapshot = build_workspace_state_snapshot(workspace_id)

    active_phrase_pool = snapshot.get("active_phrase_pool") or {}
    active_phrase_pool_modified_at = active_phrase_pool.get("modified_at")

    target_pools = snapshot.get("target_pools") or {}
    target_files = target_pools.get("files") or []

    issues: List[GovernanceIssue] = []

    if not target_files:
        return issues

    for target_file in target_files:
        target_info = file_info(Path(target_file))
        target_modified_at = target_info.get("modified_at")

        if is_datetime_newer(
            active_phrase_pool_modified_at,
            target_modified_at,
        ):
            issues.append(
                GovernanceIssue(
                    code="stale_target_pool_from_active_phrase_pool",
                    status=STALE,
                    message=f"Target pool is older than the active phrase pool: {target_file}",
                )
            )

    return issues


def build_runtime_state_snapshot(workspace_id: str) -> Dict[str, Any]:
    runtime_state_path = Path(
        f"backend/server/data/runtime_state_{workspace_id}.json"
    )

    runtime_cache_path = Path(
        f"backend/server/data/runtime_cache_{workspace_id}.json"
    )

    return {
        "runtime_state": file_info(runtime_state_path),
        "runtime_cache": file_info(runtime_cache_path),
    }


def detect_stale_runtime_state(
    workspace_id: str,
) -> List[GovernanceIssue]:
    snapshot = build_workspace_state_snapshot(workspace_id)
    runtime_snapshot = build_runtime_state_snapshot(workspace_id)

    active_phrase_pool = snapshot.get("active_phrase_pool") or {}
    active_phrase_pool_modified_at = active_phrase_pool.get("modified_at")

    issues: List[GovernanceIssue] = []

    runtime_state = runtime_snapshot.get("runtime_state") or {}
    runtime_cache = runtime_snapshot.get("runtime_cache") or {}

    runtime_state_modified_at = runtime_state.get("modified_at")
    runtime_cache_modified_at = runtime_cache.get("modified_at")

    if runtime_state.get("exists") and is_datetime_newer(
        active_phrase_pool_modified_at,
        runtime_state_modified_at,
    ):
        issues.append(
            GovernanceIssue(
                code="stale_runtime_state_from_active_phrase_pool",
                status=STALE,
                message="Runtime state is older than the active phrase pool.",
            )
        )

    if runtime_cache.get("exists") and is_datetime_newer(
        active_phrase_pool_modified_at,
        runtime_cache_modified_at,
    ):
        issues.append(
            GovernanceIssue(
                code="stale_runtime_cache_from_active_phrase_pool",
                status=STALE,
                message="Runtime cache is older than the active phrase pool.",
            )
        )

    return issues




def classify_stale_issue_severity(issue: GovernanceIssue) -> str:
    code = str(issue.code or "")

    info_codes = {
        "stale_upload_structure_validation",
        "stale_upload_structure_snapshot",
    }

    warning_codes = {
        "stale_active_phrase_set_from_upload_phrase_pool",
        "stale_target_pool_from_active_phrase_pool",
        "stale_runtime_state_from_active_phrase_pool",
        "stale_runtime_cache_from_active_phrase_pool",
    }

    blocking_codes = {
        "stale_upload_phrase_pool_from_upload_structure",
        "stale_active_phrase_pool_from_active_phrase_set",
    }

    if code in blocking_codes:
        return "BLOCKING"
    if code in warning_codes:
        return "WARNING"
    if code in info_codes:
        return "INFO"

    return "WARNING"


def decorate_stale_issues(issues: List[GovernanceIssue]) -> List[Dict[str, Any]]:
    decorated = []
    for issue in issues:
        data = asdict(issue)
        data["stale_severity"] = classify_stale_issue_severity(issue)
        decorated.append(data)
    return decorated


def generate_workspace_stale_report(
    workspace_id: str,
) -> Dict[str, Any]:
    issues: List[GovernanceIssue] = []

    issues.extend(detect_stale_upload_structure(workspace_id))
    issues.extend(detect_stale_upload_phrase_pool(workspace_id))
    issues.extend(detect_stale_active_phrase_set(workspace_id))
    issues.extend(detect_stale_active_phrase_pool(workspace_id))
    issues.extend(detect_stale_target_pools(workspace_id))
    issues.extend(detect_stale_runtime_state(workspace_id))

    decorated_issues = decorate_stale_issues(issues)

    blocking_stale_issues = [
        issue for issue in decorated_issues
        if issue.get("stale_severity") == "BLOCKING"
    ]

    warning_stale_issues = [
        issue for issue in decorated_issues
        if issue.get("stale_severity") == "WARNING"
    ]

    info_stale_issues = [
        issue for issue in decorated_issues
        if issue.get("stale_severity") == "INFO"
    ]

    stale_detected = len(blocking_stale_issues) > 0
    advisory_stale_detected = bool(warning_stale_issues or info_stale_issues)

    if blocking_stale_issues:
        status = STALE
    elif warning_stale_issues:
        status = WARNING
    elif info_stale_issues:
        status = HEALTHY
    else:
        status = HEALTHY

    report = {
        "workspace_id": workspace_id,
        "status": status,
        "health_score": score_for_status(status),
        "stale_detected": stale_detected,
        "advisory_stale_detected": advisory_stale_detected,
        "issue_count": len(issues),
        "blocking_stale_count": len(blocking_stale_issues),
        "warning_stale_count": len(warning_stale_issues),
        "info_stale_count": len(info_stale_issues),
        "issues": decorated_issues,
        "recommended_action": (
            "queue_blocking_stale_repair"
            if blocking_stale_issues
            else "recommend_reload_or_rebuild"
            if warning_stale_issues
            else "log_info"
            if info_stale_issues
            else "no_action"
        ),
        "checked_at": utc_now_iso(),
    }

    state = update_workspace_state(
        workspace_id=workspace_id,
        summary=report,
    )

    state["last_stale_report"] = report
    state["last_stale_checked_at"] = report.get("checked_at")
    state["last_stale_detected"] = stale_detected
    state["updated_at"] = utc_now_iso()

    save_workspace_state(workspace_id, state)

    return report


def read_json_file_safely(path: Path) -> Dict[str, Any] | List[Any] | None:
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def extract_upload_document_ids(upload_data: Dict[str, Any] | List[Any] | None) -> set[str]:
    if not upload_data:
        return set()

    if isinstance(upload_data, dict):
        docs = upload_data.get("docs") or upload_data.get("documents") or {}

        if isinstance(docs, dict):
            return {str(doc_id) for doc_id in docs.keys()}

        if isinstance(docs, list):
            ids = set()
            for item in docs:
                if isinstance(item, dict):
                    doc_id = item.get("doc_id") or item.get("id") or item.get("document_id")
                    if doc_id:
                        ids.add(str(doc_id))
            return ids

    if isinstance(upload_data, list):
        ids = set()
        for item in upload_data:
            if isinstance(item, dict):
                doc_id = item.get("doc_id") or item.get("id") or item.get("document_id")
                if doc_id:
                    ids.add(str(doc_id))
        return ids

    return set()


def extract_active_membership_document_ids(active_set_data: Dict[str, Any] | List[Any] | None) -> set[str]:
    if not active_set_data:
        return set()

    possible_keys = [
        "active_document_ids",
        "document_ids",
        "doc_ids",
        "docs",
        "documents",
    ]

    if isinstance(active_set_data, dict):
        for key in possible_keys:
            value = active_set_data.get(key)

            if isinstance(value, list):
                return {str(item) for item in value}

            if isinstance(value, dict):
                return {str(doc_id) for doc_id in value.keys()}

        memberships = active_set_data.get("memberships") or active_set_data.get("items")
        if isinstance(memberships, list):
            ids = set()
            for item in memberships:
                if isinstance(item, dict):
                    doc_id = item.get("doc_id") or item.get("id") or item.get("document_id")
                    if doc_id:
                        ids.add(str(doc_id))
            return ids

    if isinstance(active_set_data, list):
        ids = set()
        for item in active_set_data:
            if isinstance(item, dict):
                doc_id = item.get("doc_id") or item.get("id") or item.get("document_id")
                if doc_id:
                    ids.add(str(doc_id))
            elif isinstance(item, str):
                ids.add(item)
        return ids

    return set()


def validate_upload_to_active_membership(
    workspace_id: str,
) -> Dict[str, Any]:
    workspace_id = str(workspace_id or "").strip()

    upload_struct_path = Path(f"backend/server/data/upload_struct_{workspace_id}.json")
    active_phrase_set_path = Path(
        f"backend/server/data/phrase_pools/active/active_phrase_set_{workspace_id}.json"
    )

    issues: List[GovernanceIssue] = []

    if not upload_struct_path.exists():
        issues.append(
            GovernanceIssue(
                code="upload_structure_missing_for_membership_validation",
                status=REPAIR_REQUIRED,
                message="Upload structure is missing; cannot validate upload to active membership.",
            )
        )

    if not active_phrase_set_path.exists():
        issues.append(
            GovernanceIssue(
                code="active_phrase_set_missing_for_membership_validation",
                status=REPAIR_REQUIRED,
                message="Active phrase set is missing; cannot validate upload to active membership.",
            )
        )

    upload_data = read_json_file_safely(upload_struct_path)
    active_set_data = read_json_file_safely(active_phrase_set_path)

    if upload_struct_path.exists() and upload_data is None:
        issues.append(
            GovernanceIssue(
                code="upload_structure_invalid_json_for_membership_validation",
                status=REPAIR_REQUIRED,
                message="Upload structure JSON is invalid or unreadable.",
            )
        )

    if active_phrase_set_path.exists() and active_set_data is None:
        issues.append(
            GovernanceIssue(
                code="active_phrase_set_invalid_json_for_membership_validation",
                status=REPAIR_REQUIRED,
                message="Active phrase set JSON is invalid or unreadable.",
            )
        )

    upload_doc_ids = extract_upload_document_ids(upload_data)
    membership_doc_ids = extract_active_membership_document_ids(active_set_data)

    missing_from_membership = sorted(upload_doc_ids - membership_doc_ids)
    nonexistent_membership_refs = sorted(membership_doc_ids - upload_doc_ids)

    if missing_from_membership:
        issues.append(
            GovernanceIssue(
                code="upload_docs_missing_from_active_membership",
                status=DRIFTED,
                message=f"Uploaded documents missing from active membership: {missing_from_membership}",
            )
        )

    if nonexistent_membership_refs:
        issues.append(
            GovernanceIssue(
                code="active_membership_references_missing_upload_docs",
                status=DRIFTED,
                message=f"Active membership references documents not found in upload structure: {nonexistent_membership_refs}",
            )
        )

    status = classify_workspace_status(issues)
    passed = len(issues) == 0

    report = {
        "workspace_id": workspace_id,
        "validation": "upload_to_active_membership",
        "passed": passed,
        "status": status if not passed else HEALTHY,
        "upload_doc_count": len(upload_doc_ids),
        "membership_doc_count": len(membership_doc_ids),
        "missing_from_membership": missing_from_membership,
        "nonexistent_membership_refs": nonexistent_membership_refs,
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
        "checked_at": utc_now_iso(),
    }

    if passed:
        mark_workspace_validation_passed(workspace_id)
    else:
        mark_workspace_validation_failed(
            workspace_id,
            error=f"Upload to active membership validation failed with {len(issues)} issue(s).",
        )

    return report


def extract_active_pool_document_ids(active_pool_data: Dict[str, Any] | List[Any] | None) -> set[str]:
    if not active_pool_data:
        return set()

    ids = set()

    if isinstance(active_pool_data, dict):
        for key in ["doc_ids", "document_ids", "active_document_ids"]:
            value = active_pool_data.get(key)
            if isinstance(value, list):
                ids.update(str(x) for x in value)

        phrases = active_pool_data.get("phrases") or active_pool_data.get("items") or []
        if isinstance(phrases, list):
            for item in phrases:
                if isinstance(item, dict):
                    doc_id = item.get("doc_id") or item.get("document_id") or item.get("source_doc_id")
                    if doc_id:
                        ids.add(str(doc_id))

    elif isinstance(active_pool_data, list):
        for item in active_pool_data:
            if isinstance(item, dict):
                doc_id = item.get("doc_id") or item.get("document_id") or item.get("source_doc_id")
                if doc_id:
                    ids.add(str(doc_id))

    return ids


def validate_active_membership_to_active_pool(workspace_id: str) -> Dict[str, Any]:
    workspace_id = str(workspace_id or "").strip()

    active_phrase_set_path = Path(
        f"backend/server/data/phrase_pools/active/active_phrase_set_{workspace_id}.json"
    )
    active_phrase_pool_path = Path(
        f"backend/server/data/phrase_pools/active/active_phrase_pool_{workspace_id}.json"
    )

    issues: List[GovernanceIssue] = []

    active_set_data = read_json_file_safely(active_phrase_set_path)
    active_pool_data = read_json_file_safely(active_phrase_pool_path)

    if not active_phrase_set_path.exists():
        issues.append(GovernanceIssue("active_phrase_set_missing_for_pool_validation", REPAIR_REQUIRED, "Active phrase set is missing."))

    if not active_phrase_pool_path.exists():
        issues.append(GovernanceIssue("active_phrase_pool_missing_for_pool_validation", REPAIR_REQUIRED, "Active phrase pool is missing."))

    if active_phrase_set_path.exists() and active_set_data is None:
        issues.append(GovernanceIssue("active_phrase_set_invalid_json_for_pool_validation", REPAIR_REQUIRED, "Active phrase set JSON is invalid."))

    if active_phrase_pool_path.exists() and active_pool_data is None:
        issues.append(GovernanceIssue("active_phrase_pool_invalid_json_for_pool_validation", REPAIR_REQUIRED, "Active phrase pool JSON is invalid."))

    membership_doc_ids = extract_active_membership_document_ids(active_set_data)
    active_pool_doc_ids = extract_active_pool_document_ids(active_pool_data)

    missing_from_pool = sorted(membership_doc_ids - active_pool_doc_ids)
    nonexistent_pool_refs = sorted(active_pool_doc_ids - membership_doc_ids)

    if missing_from_pool:
        issues.append(GovernanceIssue("membership_docs_missing_from_active_pool", DRIFTED, f"Membership docs missing from active pool: {missing_from_pool}"))

    if nonexistent_pool_refs:
        issues.append(GovernanceIssue("active_pool_references_missing_membership_docs", DRIFTED, f"Active pool references docs not in membership: {nonexistent_pool_refs}"))

    passed = len(issues) == 0
    status = HEALTHY if passed else classify_workspace_status(issues)

    return {
        "workspace_id": workspace_id,
        "validation": "active_membership_to_active_pool",
        "passed": passed,
        "status": status,
        "membership_doc_count": len(membership_doc_ids),
        "active_pool_doc_count": len(active_pool_doc_ids),
        "missing_from_pool": missing_from_pool,
        "nonexistent_pool_refs": nonexistent_pool_refs,
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
        "checked_at": utc_now_iso(),
    }


def validate_active_pool_to_runtime(workspace_id: str) -> Dict[str, Any]:
    workspace_id = str(workspace_id or "").strip()

    active_phrase_pool_path = Path(
        f"backend/server/data/phrase_pools/active/active_phrase_pool_{workspace_id}.json"
    )
    runtime_snapshot = build_runtime_state_snapshot(workspace_id)

    issues: List[GovernanceIssue] = []

    active_pool_data = read_json_file_safely(active_phrase_pool_path)

    if not active_phrase_pool_path.exists():
        issues.append(GovernanceIssue("active_phrase_pool_missing_for_runtime_validation", REPAIR_REQUIRED, "Active phrase pool is missing."))

    if active_phrase_pool_path.exists() and active_pool_data is None:
        issues.append(GovernanceIssue("active_phrase_pool_invalid_json_for_runtime_validation", REPAIR_REQUIRED, "Active phrase pool JSON is invalid."))

    runtime_state = runtime_snapshot.get("runtime_state") or {}
    runtime_cache = runtime_snapshot.get("runtime_cache") or {}

    if not runtime_state.get("exists") and not runtime_cache.get("exists"):
        issues.append(GovernanceIssue("runtime_state_missing_for_active_pool_validation", WARNING, "No runtime state or runtime cache file found."))

    passed = len(issues) == 0
    status = HEALTHY if passed else classify_workspace_status(issues)

    return {
        "workspace_id": workspace_id,
        "validation": "active_pool_to_runtime",
        "passed": passed,
        "status": status,
        "runtime_state": runtime_state,
        "runtime_cache": runtime_cache,
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
        "checked_at": utc_now_iso(),
    }


def validate_target_pool_references(workspace_id: str) -> Dict[str, Any]:
    workspace_id = str(workspace_id or "").strip()

    snapshot = build_workspace_state_snapshot(workspace_id)
    active_phrase_pool_path = Path(
        f"backend/server/data/phrase_pools/active/active_phrase_pool_{workspace_id}.json"
    )

    issues: List[GovernanceIssue] = []

    active_pool_data = read_json_file_safely(active_phrase_pool_path)
    target_files = (snapshot.get("target_pools") or {}).get("files") or []

    if active_phrase_pool_path.exists() and active_pool_data is None:
        issues.append(GovernanceIssue("active_phrase_pool_invalid_json_for_target_reference_validation", REPAIR_REQUIRED, "Active phrase pool JSON is invalid."))

    for target_file in target_files:
        target_path = Path(target_file)
        target_data = read_json_file_safely(target_path)

        if target_data is None:
            issues.append(GovernanceIssue("target_pool_invalid_json_for_reference_validation", REPAIR_REQUIRED, f"Target pool JSON is invalid or unreadable: {target_file}"))

    if not target_files:
        issues.append(GovernanceIssue("target_pool_files_missing_for_reference_validation", WARNING, "No target pool files found for this workspace."))

    passed = len(issues) == 0
    status = HEALTHY if passed else classify_workspace_status(issues)

    return {
        "workspace_id": workspace_id,
        "validation": "target_pool_references",
        "passed": passed,
        "status": status,
        "target_pool_file_count": len(target_files),
        "target_pool_files": target_files,
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
        "checked_at": utc_now_iso(),
    }


def validate_imported_sources(workspace_id: str) -> Dict[str, Any]:
    workspace_id = str(workspace_id or "").strip()

    imported_paths = [
        Path(f"backend/server/data/imported_urls_{workspace_id}.json"),
        Path(f"backend/server/data/imports/imported_urls_{workspace_id}.json"),
        Path(f"backend/server/data/phrase_pools/imported/imported_phrase_pool_{workspace_id}.json"),
    ]

    issues: List[GovernanceIssue] = []
    checked_files = []

    for path in imported_paths:
        info = file_info(path)
        checked_files.append({"path": str(path), **info})

        if info.get("exists") and read_json_file_safely(path) is None:
            issues.append(GovernanceIssue("imported_source_invalid_json", REPAIR_REQUIRED, f"Imported source JSON is invalid: {path}"))

    passed = len(issues) == 0
    status = HEALTHY if passed else classify_workspace_status(issues)

    return {
        "workspace_id": workspace_id,
        "validation": "imported_sources",
        "passed": passed,
        "status": status,
        "checked_files": checked_files,
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
        "checked_at": utc_now_iso(),
    }


def validate_draft_sources(workspace_id: str) -> Dict[str, Any]:
    workspace_id = str(workspace_id or "").strip()

    draft_paths = [
        Path(f"backend/server/data/drafts_{workspace_id}.json"),
        Path(f"backend/server/data/drafts/drafts_{workspace_id}.json"),
        Path(f"backend/server/data/phrase_pools/draft/draft_phrase_pool_{workspace_id}.json"),
    ]

    issues: List[GovernanceIssue] = []
    checked_files = []

    for path in draft_paths:
        info = file_info(path)
        checked_files.append({"path": str(path), **info})

        if info.get("exists") and read_json_file_safely(path) is None:
            issues.append(GovernanceIssue("draft_source_invalid_json", REPAIR_REQUIRED, f"Draft source JSON is invalid: {path}"))

    passed = len(issues) == 0
    status = HEALTHY if passed else classify_workspace_status(issues)

    return {
        "workspace_id": workspace_id,
        "validation": "draft_sources",
        "passed": passed,
        "status": status,
        "checked_files": checked_files,
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
        "checked_at": utc_now_iso(),
    }


def validate_live_domain_sources(workspace_id: str) -> Dict[str, Any]:
    workspace_id = str(workspace_id or "").strip()

    live_domain_paths = [
        Path(f"backend/server/data/live_domain_{workspace_id}.json"),
        Path(f"backend/server/data/live_domains/live_domain_{workspace_id}.json"),
        Path(f"backend/server/data/live_domain_sync/live_domain_sync_{workspace_id}.json"),
        Path(f"backend/server/data/phrase_pools/live_domain/live_domain_phrase_pool_{workspace_id}.json"),
    ]

    issues: List[GovernanceIssue] = []
    checked_files = []

    for path in live_domain_paths:
        info = file_info(path)

        checked_files.append({
            "path": str(path),
            **info,
        })

        if info.get("exists"):
            data = read_json_file_safely(path)

            if data is None:
                issues.append(
                    GovernanceIssue(
                        code="live_domain_source_invalid_json",
                        status=REPAIR_REQUIRED,
                        message=f"Live domain source JSON is invalid: {path}",
                    )
                )

    passed = len(issues) == 0
    status = HEALTHY if passed else classify_workspace_status(issues)

    report = {
        "workspace_id": workspace_id,
        "validation": "live_domain_sources",
        "passed": passed,
        "status": status,
        "checked_files": checked_files,
        "issue_count": len(issues),
        "issues": [asdict(issue) for issue in issues],
        "checked_at": utc_now_iso(),
    }

    if passed:
        mark_workspace_validation_passed(workspace_id)
    else:
        mark_workspace_validation_failed(
            workspace_id,
            error=f"Live domain validation failed with {len(issues)} issue(s).",
        )

    return report


def workspace_repair_queue_path(workspace_id: str) -> Path:
    safe_workspace_id = str(workspace_id or "").strip() or "default"
    return ensure_workspace_governance_data_dir() / f"{safe_workspace_id}_repair_queue.json"


def load_workspace_repair_queue(workspace_id: str) -> List[Dict[str, Any]]:
    path = workspace_repair_queue_path(workspace_id)

    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception:
        return []

    return []


def save_workspace_repair_queue(
    workspace_id: str,
    queue: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    path = workspace_repair_queue_path(workspace_id)

    path.write_text(
        json.dumps(queue, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return queue


def queue_workspace_repair(
    workspace_id: str,
    repair_type: str,
    reason: str,
) -> Dict[str, Any]:
    now = utc_now_iso()
    queue = load_workspace_repair_queue(workspace_id)

    repair_item = {
        "repair_id": f"repair_{len(queue) + 1}_{int(datetime.now(timezone.utc).timestamp())}",
        "workspace_id": workspace_id,
        "repair_type": repair_type,
        "reason": str(reason or ""),
        "status": "queued",
        "created_at": now,
        "updated_at": now,
    }

    queue.append(repair_item)
    save_workspace_repair_queue(workspace_id, queue)

    state = load_workspace_state(workspace_id)
    state["last_repair_queued_at"] = now
    state["last_repair_type"] = repair_type
    state["last_repair_reason"] = reason
    state["updated_at"] = now
    save_workspace_state(workspace_id, state)

    return repair_item


def queue_rebuild_repair(
    workspace_id: str,
    reason: str = "Workspace governance requested rebuild repair.",
) -> Dict[str, Any]:
    return queue_workspace_repair(
        workspace_id=workspace_id,
        repair_type="rebuild_repair",
        reason=reason,
    )


def queue_reload_repair(
    workspace_id: str,
    reason: str = "Workspace governance requested reload repair.",
) -> Dict[str, Any]:
    return queue_workspace_repair(
        workspace_id=workspace_id,
        repair_type="reload_repair",
        reason=reason,
    )


def queue_membership_repair(
    workspace_id: str,
    reason: str = "Workspace governance requested active membership repair.",
) -> Dict[str, Any]:
    return queue_workspace_repair(
        workspace_id=workspace_id,
        repair_type="membership_repair",
        reason=reason,
    )


def queue_pool_repair(
    workspace_id: str,
    reason: str = "Workspace governance requested pool repair.",
) -> Dict[str, Any]:
    return queue_workspace_repair(
        workspace_id=workspace_id,
        repair_type="pool_repair",
        reason=reason,
    )


def queue_runtime_refresh(
    workspace_id: str,
    reason: str = "Workspace governance requested runtime refresh.",
) -> Dict[str, Any]:
    return queue_workspace_repair(
        workspace_id=workspace_id,
        repair_type="runtime_refresh",
        reason=reason,
    )


def generate_workspace_auto_repair_report(
    workspace_id: str,
) -> Dict[str, Any]:
    workspace_id = str(workspace_id or "").strip()

    queue = load_workspace_repair_queue(workspace_id)
    state = load_workspace_state(workspace_id)

    queued_items = [
        item for item in queue
        if item.get("status") == "queued"
    ]

    repair_types = sorted({
        str(item.get("repair_type"))
        for item in queue
        if item.get("repair_type")
    })

    report = {
        "workspace_id": workspace_id,
        "repair_report": "workspace_auto_repair",
        "total_repair_items": len(queue),
        "queued_repair_items": len(queued_items),
        "repair_types": repair_types,
        "last_repair_queued_at": state.get("last_repair_queued_at"),
        "last_repair_type": state.get("last_repair_type"),
        "last_repair_reason": state.get("last_repair_reason"),
        "queue": queue,
        "checked_at": utc_now_iso(),
    }

    state["last_auto_repair_report"] = report
    state["last_auto_repair_checked_at"] = report.get("checked_at")
    state["updated_at"] = utc_now_iso()

    save_workspace_state(workspace_id, state)

    return report


def run_workspace_open_governance_check(
    workspace_id: str,
) -> Dict[str, Any]:
    workspace_id = str(workspace_id or "").strip()

    health_report = update_workspace_health(workspace_id)
    drift_report = generate_workspace_drift_report(workspace_id)
    stale_report = generate_workspace_stale_report(workspace_id)

    statuses = [
        health_report.get("current_status") or health_report.get("status"),
        drift_report.get("status"),
        stale_report.get("status"),
    ]

    final_status = choose_most_severe_status([
        status for status in statuses
        if status
    ])

    report = {
        "workspace_id": workspace_id,
        "event": "workspace_open",
        "status": final_status,
        "health": health_report,
        "drift": drift_report,
        "stale": stale_report,
        "checked_at": utc_now_iso(),
    }

    state = load_workspace_state(workspace_id)
    state["last_workspace_open_check"] = report
    state["last_workspace_open_checked_at"] = report.get("checked_at")
    state["current_status"] = final_status
    state["health_score"] = score_for_status(final_status)
    state["updated_at"] = utc_now_iso()

    save_workspace_state(workspace_id, state)

    return report


def run_upload_complete_governance_check(
    workspace_id: str,
) -> Dict[str, Any]:
    report = run_workspace_open_governance_check(workspace_id)

    report["event"] = "upload_complete"
    report["checked_at"] = utc_now_iso()

    state = load_workspace_state(workspace_id)
    state["last_upload_complete_check"] = report
    state["last_upload_complete_checked_at"] = report["checked_at"]

    save_workspace_state(workspace_id, state)

    return report


def run_session_clear_governance_check(
    workspace_id: str,
) -> Dict[str, Any]:
    report = run_workspace_open_governance_check(workspace_id)

    report["event"] = "session_clear"
    report["checked_at"] = utc_now_iso()

    state = load_workspace_state(workspace_id)
    state["last_session_clear_check"] = report
    state["last_session_clear_checked_at"] = report["checked_at"]

    save_workspace_state(workspace_id, state)

    return report


def run_rebuild_complete_governance_check(
    workspace_id: str,
) -> Dict[str, Any]:
    report = run_workspace_open_governance_check(workspace_id)

    report["event"] = "rebuild_complete"
    report["checked_at"] = utc_now_iso()

    state = load_workspace_state(workspace_id)
    state["last_rebuild_complete_check"] = report
    state["last_rebuild_complete_checked_at"] = report["checked_at"]

    save_workspace_state(workspace_id, state)

    return report


def run_reload_complete_governance_check(
    workspace_id: str,
) -> Dict[str, Any]:
    report = run_workspace_open_governance_check(workspace_id)

    report["event"] = "reload_complete"
    report["checked_at"] = utc_now_iso()

    state = load_workspace_state(workspace_id)
    state["last_reload_complete_check"] = report
    state["last_reload_complete_checked_at"] = report["checked_at"]

    save_workspace_state(workspace_id, state)

    return report


def run_governance_sweep(
    workspace_id: str,
) -> Dict[str, Any]:
    report = run_workspace_open_governance_check(workspace_id)

    report["event"] = "governance_sweep"
    report["sweep_interval_seconds"] = 180
    report["checked_at"] = utc_now_iso()

    state = load_workspace_state(workspace_id)

    previous_sweeps = int(state.get("governance_sweep_count") or 0)

    state["governance_sweep_count"] = previous_sweeps + 1
    state["last_governance_sweep"] = report
    state["last_governance_sweep_at"] = report["checked_at"]

    save_workspace_state(workspace_id, state)

    return report


def process_workspace_repair_queue(workspace_id: str) -> Dict[str, Any]:
    """
    AUTO REPAIR EXECUTION ENGINE
    Executes queued repair actions safely (one pass only).
    """

    queue = load_workspace_repair_queue(workspace_id)
    state = load_workspace_state(workspace_id)

    processed = []
    skipped = []

    for item in queue:
        if item.get("status") != "queued":
            skipped.append(item)
            continue

        repair_type = item.get("repair_type")

        if should_escalate_repair(item):
            mark_repair_escalated(
                item,
                reason="Repair exceeded maximum retry attempts before execution.",
            )
            skipped.append(item)
            continue

        mark_repair_attempt_started(item)

        try:
            # -------------------------
            # EXECUTION DISPATCHER
            # -------------------------

            if repair_type == "rebuild_repair":
                # REAL FULL REBUILD:
                # 1) rebuild upload phrase pool from canonical upload phrase index
                # 2) rebuild active phrase pool from upload pool and active membership
                upload_result = build_upload_phrase_pool(workspace_id)
                active_result = build_active_phrase_pool(workspace_id)

                item["execution_result"] = {
                    "upload_phrase_pool": {
                        "source_phrase_count": upload_result.get("source_phrase_count"),
                        "quality_filtered_source_count": upload_result.get("quality_filtered_source_count"),
                        "phrase_count": upload_result.get("phrase_count"),
                    },
                    "active_phrase_pool": {
                        "phrase_count": active_result.get("phrase_count"),
                        "accepted_by_source": active_result.get("accepted_by_source"),
                        "rejected_by_source": active_result.get("rejected_by_source"),
                    },
                }

                state["last_auto_rebuild_executed"] = utc_now_iso()
                state["last_auto_rebuild_upload_phrase_count"] = upload_result.get("phrase_count")
                state["last_auto_rebuild_active_phrase_count"] = active_result.get("phrase_count")

            elif repair_type == "reload_repair":
                # REAL RELOAD GOVERNANCE:
                # Queue and process backend reload state so frontend/runtime can repaint from healthy pools.
                reload_event = queue_reload_event(
                    workspace_id=workspace_id,
                    trigger="active_phrase_pool_changed",
                )

                reload_result = process_reload_queue(workspace_id)

                item["execution_result"] = {
                    "reload_event": reload_event,
                    "reload_result": reload_result,
                }

                state["last_auto_reload_executed"] = utc_now_iso()
                state["last_auto_reload_processed"] = reload_result.get("processed")
                state["last_auto_reload_remaining"] = reload_result.get("remaining")

            elif repair_type == "membership_repair":
                state["last_membership_repair_executed"] = utc_now_iso()

            elif repair_type == "pool_repair":
                upload_result = build_upload_phrase_pool(workspace_id)
                active_result = build_active_phrase_pool(workspace_id)

                item["execution_result"] = {
                    "upload_phrase_pool_count": upload_result.get("phrase_count"),
                    "active_phrase_pool_count": active_result.get("phrase_count"),
                }

                state["last_pool_repair_executed"] = utc_now_iso()
                state["last_pool_repair_upload_phrase_count"] = upload_result.get("phrase_count")
                state["last_pool_repair_active_phrase_count"] = active_result.get("phrase_count")

            elif repair_type == "runtime_refresh":
                state["last_runtime_refresh_executed"] = utc_now_iso()

            else:
                mark_repair_escalated(
                    item,
                    reason=f"Unknown repair type cannot be executed automatically: {repair_type}",
                )
                skipped.append(item)
                continue

            # -------------------------
            # POST-REPAIR VALIDATION
            # -------------------------
            if repair_type == "rebuild_repair":
                validation_report = run_rebuild_complete_governance_check(workspace_id)
            elif repair_type == "reload_repair":
                validation_report = run_reload_complete_governance_check(workspace_id)
            else:
                validation_report = run_workspace_open_governance_check(workspace_id)

            item["validation_report"] = validation_report

            validation_failed = bool(
                (validation_report.get("drift") or {}).get("drift_detected")
                or int((validation_report.get("drift") or {}).get("blocking_issue_count") or 0) > 0
                or str(validation_report.get("status") or "").upper() in {
                    "DRIFTED",
                    "REPAIR_REQUIRED",
                    "CRITICAL",
                }
            )

            if validation_failed:
                item["failed_validation_at"] = utc_now_iso()

                if should_escalate_repair(item):
                    mark_repair_escalated(
                        item,
                        reason=f"Repair failed validation after {get_repair_attempt_count(item)} attempt(s).",
                    )
                else:
                    item["status"] = "queued"
                    item["retry_reason"] = "post_repair_validation_failed"
                    item["next_retry_allowed"] = True

                skipped.append(item)
                continue

            # mark as completed only after validation passes
            item["status"] = "completed"
            item["completed_at"] = utc_now_iso()

            processed.append(item)

        except Exception as e:
            item["error"] = str(e)
            item["last_failed_at"] = utc_now_iso()

            if should_escalate_repair(item):
                mark_repair_escalated(
                    item,
                    reason=f"Repair failed after {get_repair_attempt_count(item)} attempt(s): {e}",
                )
            else:
                item["status"] = "queued"
                item["retry_reason"] = str(e)
                item["next_retry_allowed"] = True

            skipped.append(item)

    # update queue state
    save_workspace_repair_queue(workspace_id, queue)

    # update workspace state
    state["last_repair_execution_run"] = utc_now_iso()
    state["last_repair_processed_count"] = len(processed)
    state["last_repair_skipped_count"] = len(skipped)

    save_workspace_state(workspace_id, state)

    return {
        "workspace_id": workspace_id,
        "processed": processed,
        "skipped": skipped,
        "processed_count": len(processed),
        "checked_at": utc_now_iso(),
    }


import threading
import time


_WORKSPACE_GOVERNANCE_LOCKS = {}
_WORKSPACE_LAST_RUN = {}


def _can_run_sweep(workspace_id: str) -> bool:
    now = time.time()
    last = _WORKSPACE_LAST_RUN.get(workspace_id, 0)

    return (now - last) >= 180  # 3-minute cooldown


def run_autonomous_workspace_governance_engine(
    workspace_id: str,
    max_cycles: int = 1,
) -> Dict[str, Any]:
    """
    FULL AUTONOMOUS WORKSPACE ENGINE

    3-minute sweep → detect → repair → execute → verify
    """

    workspace_id = str(workspace_id or "").strip()

    if workspace_id in _WORKSPACE_GOVERNANCE_LOCKS:
        return {
            "workspace_id": workspace_id,
            "status": "RUNNING",
            "message": "Governance engine already running.",
        }

    if not _can_run_sweep(workspace_id):
        return {
            "workspace_id": workspace_id,
            "status": "COOLDOWN",
            "message": "3-minute sweep cooldown active.",
        }

    _WORKSPACE_GOVERNANCE_LOCKS[workspace_id] = True
    _WORKSPACE_LAST_RUN[workspace_id] = time.time()

    try:
        results = []

        for _ in range(max_cycles):

            # ---------------------------
            # 1. DETECTION PHASE
            # ---------------------------
            drift = generate_workspace_drift_report(workspace_id)
            stale = generate_workspace_stale_report(workspace_id)

            # ---------------------------
            # 2. REPAIR QUEUE PHASE
            # ---------------------------
            if drift.get("drift_detected"):
                queue_rebuild_repair(workspace_id, "auto drift repair")

            if stale.get("stale_detected"):
                queue_reload_repair(workspace_id, "auto stale repair")

            # ---------------------------
            # 3. EXECUTION PHASE
            # ---------------------------
            execution_result = process_workspace_repair_queue(workspace_id)

            # ---------------------------
            # 4. RE-VALIDATION PHASE
            # ---------------------------
            post_drift = generate_workspace_drift_report(workspace_id)
            post_stale = generate_workspace_stale_report(workspace_id)

            results.append({
                "cycle_complete": True,
                "drift_before": drift.get("drift_detected"),
                "stale_before": stale.get("stale_detected"),
                "drift_after": post_drift.get("drift_detected"),
                "stale_after": post_stale.get("stale_detected"),
                "execution": execution_result,
            })

        # ---------------------------
        # FINAL STATE UPDATE
        # ---------------------------
        state = load_workspace_state(workspace_id)
        state["last_autonomous_run"] = utc_now_iso()
        state["last_autonomous_results"] = results
        state["updated_at"] = utc_now_iso()

        save_workspace_state(workspace_id, state)

        return {
            "workspace_id": workspace_id,
            "status": "COMPLETED",
            "cycles": results,
            "checked_at": utc_now_iso(),
        }

    finally:
        _WORKSPACE_GOVERNANCE_LOCKS.pop(workspace_id, None)


_BACKGROUND_SCHEDULER_RUNNING = False


def _workspace_scheduler_loop():
    """
    Background loop that runs autonomous governance every 3 minutes.
    """

    global _BACKGROUND_SCHEDULER_RUNNING

    while _BACKGROUND_SCHEDULER_RUNNING:
        try:
            # Load all known workspaces from state directory
            base_dir = ensure_workspace_governance_data_dir()

            workspace_files = list(base_dir.glob("*_state.json"))

            for file in workspace_files:
                workspace_id = file.stem.replace("_state", "")

                try:
                    run_autonomous_workspace_governance_engine(workspace_id)
                except Exception:
                    # never crash scheduler loop
                    continue

        except Exception:
            pass

        time.sleep(180)  # 3 minutes


def start_workspace_governance_scheduler():
    """
    Starts the always-on background governance scheduler.
    Safe to call multiple times (idempotent).
    """

    global _BACKGROUND_SCHEDULER_RUNNING

    if _BACKGROUND_SCHEDULER_RUNNING:
        return {
            "status": "already_running"
        }

    _BACKGROUND_SCHEDULER_RUNNING = True

    thread = threading.Thread(
        target=_workspace_scheduler_loop,
        daemon=True
    )

    thread.start()

    return {
        "status": "started",
        "interval_seconds": 180,
        "mode": "autonomous_background_scheduler",
        "checked_at": utc_now_iso(),
    }


def stop_workspace_governance_scheduler():
    """
    Stops the background scheduler.
    """

    global _BACKGROUND_SCHEDULER_RUNNING

    _BACKGROUND_SCHEDULER_RUNNING = False

    return {
        "status": "stopped",
        "checked_at": utc_now_iso(),
    }










MAX_REPAIR_RETRY_ATTEMPTS = 3


def get_repair_attempt_count(item: Dict[str, Any]) -> int:
    return int(item.get("attempt_count") or 0)


def mark_repair_attempt_started(item: Dict[str, Any]) -> Dict[str, Any]:
    item["attempt_count"] = get_repair_attempt_count(item) + 1
    item["last_attempt_started_at"] = utc_now_iso()
    return item


def should_escalate_repair(item: Dict[str, Any]) -> bool:
    return get_repair_attempt_count(item) >= MAX_REPAIR_RETRY_ATTEMPTS


def mark_repair_escalated(
    item: Dict[str, Any],
    reason: str,
) -> Dict[str, Any]:
    item["status"] = "escalated"
    item["escalated_at"] = utc_now_iso()
    item["escalation_reason"] = str(reason or "Repair exceeded retry limit.")
    item["requires_manual_review"] = True
    return item



def generate_owner_admin_repair_alert_summary(workspace_id: str) -> Dict[str, Any]:
    """
    OWNER / ADMIN REPAIR ALERT SUMMARY

    Summarizes repair queue state for Owner Console display.
    """
    queue = load_workspace_repair_queue(workspace_id)
    state = load_workspace_state(workspace_id)

    escalated = [
        item for item in queue
        if str(item.get("status") or "").lower() == "escalated"
    ]

    manual_review_required = [
        item for item in queue
        if bool(item.get("requires_manual_review"))
    ]

    failed_validation = [
        item for item in queue
        if str(item.get("status") or "").lower() == "failed_validation"
    ]

    failed = [
        item for item in queue
        if str(item.get("status") or "").lower() == "failed"
    ]

    queued = [
        item for item in queue
        if str(item.get("status") or "").lower() == "queued"
    ]

    completed = [
        item for item in queue
        if str(item.get("status") or "").lower() == "completed"
    ]

    summary = {
        "workspace_id": workspace_id,
        "alert_type": "owner_admin_repair_alert_summary",
        "total_repair_items": len(queue),
        "queued_count": len(queued),
        "completed_count": len(completed),
        "failed_count": len(failed),
        "failed_validation_count": len(failed_validation),
        "escalated_count": len(escalated),
        "manual_review_required_count": len(manual_review_required),
        "has_owner_alerts": bool(escalated or manual_review_required or failed_validation or failed),
        "latest_escalated": escalated[-1] if escalated else None,
        "latest_manual_review_required": manual_review_required[-1] if manual_review_required else None,
        "latest_failed_validation": failed_validation[-1] if failed_validation else None,
        "latest_failed": failed[-1] if failed else None,
        "last_auto_rebuild_executed": state.get("last_auto_rebuild_executed"),
        "last_auto_rebuild_upload_phrase_count": state.get("last_auto_rebuild_upload_phrase_count"),
        "last_auto_rebuild_active_phrase_count": state.get("last_auto_rebuild_active_phrase_count"),
        "last_auto_reload_executed": state.get("last_auto_reload_executed"),
        "last_auto_reload_processed": state.get("last_auto_reload_processed"),
        "last_auto_reload_remaining": state.get("last_auto_reload_remaining"),
        "last_repair_execution_run": state.get("last_repair_execution_run"),
        "last_repair_processed_count": state.get("last_repair_processed_count"),
        "last_repair_skipped_count": state.get("last_repair_skipped_count"),
        "checked_at": utc_now_iso(),
    }

    state["last_owner_admin_repair_alert_summary"] = summary
    state["last_owner_admin_repair_alert_checked_at"] = summary["checked_at"]
    save_workspace_state(workspace_id, state)

    return summary


def compact_repair_item_for_owner_console(item: Dict[str, Any] | None) -> Dict[str, Any] | None:
    """
    Converts a full repair queue item into a compact Owner Console card payload.
    """
    if not isinstance(item, dict):
        return None

    return {
        "repair_id": item.get("repair_id"),
        "workspace_id": item.get("workspace_id"),
        "repair_type": item.get("repair_type"),
        "status": item.get("status"),
        "reason": item.get("reason"),
        "attempt_count": item.get("attempt_count"),
        "requires_manual_review": bool(item.get("requires_manual_review")),
        "escalation_reason": item.get("escalation_reason"),
        "retry_reason": item.get("retry_reason"),
        "error": item.get("error"),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
        "completed_at": item.get("completed_at"),
        "failed_validation_at": item.get("failed_validation_at"),
        "last_failed_at": item.get("last_failed_at"),
        "escalated_at": item.get("escalated_at"),
    }


def generate_owner_admin_repair_alert_display_payload(workspace_id: str) -> Dict[str, Any]:
    """
    Compact Owner Console-ready repair alert payload.
    """
    summary = generate_owner_admin_repair_alert_summary(workspace_id)

    queue = load_workspace_repair_queue(workspace_id)

    escalated = [
        compact_repair_item_for_owner_console(item)
        for item in queue
        if str(item.get("status") or "").lower() == "escalated"
    ]

    manual_review_required = [
        compact_repair_item_for_owner_console(item)
        for item in queue
        if bool(item.get("requires_manual_review"))
    ]

    failed_validation = [
        compact_repair_item_for_owner_console(item)
        for item in queue
        if str(item.get("status") or "").lower() == "failed_validation"
    ]

    failed = [
        compact_repair_item_for_owner_console(item)
        for item in queue
        if str(item.get("status") or "").lower() == "failed"
    ]

    recent_activity = [
        compact_repair_item_for_owner_console(item)
        for item in queue[-10:]
    ]

    payload = {
        "workspace_id": workspace_id,
        "display_type": "owner_admin_repair_alert_display_payload",
        "has_owner_alerts": summary.get("has_owner_alerts"),
        "counts": {
            "total": summary.get("total_repair_items"),
            "queued": summary.get("queued_count"),
            "completed": summary.get("completed_count"),
            "failed": summary.get("failed_count"),
            "failed_validation": summary.get("failed_validation_count"),
            "escalated": summary.get("escalated_count"),
            "manual_review_required": summary.get("manual_review_required_count"),
        },
        "cards": {
            "latest_escalated": compact_repair_item_for_owner_console(summary.get("latest_escalated")),
            "latest_manual_review_required": compact_repair_item_for_owner_console(summary.get("latest_manual_review_required")),
            "latest_failed_validation": compact_repair_item_for_owner_console(summary.get("latest_failed_validation")),
            "latest_failed": compact_repair_item_for_owner_console(summary.get("latest_failed")),
        },
        "lists": {
            "escalated": escalated[-10:],
            "manual_review_required": manual_review_required[-10:],
            "failed_validation": failed_validation[-10:],
            "failed": failed[-10:],
            "recent_activity": recent_activity,
        },
        "last_rebuild_reload": {
            "last_auto_rebuild_executed": summary.get("last_auto_rebuild_executed"),
            "last_auto_rebuild_upload_phrase_count": summary.get("last_auto_rebuild_upload_phrase_count"),
            "last_auto_rebuild_active_phrase_count": summary.get("last_auto_rebuild_active_phrase_count"),
            "last_auto_reload_executed": summary.get("last_auto_reload_executed"),
            "last_auto_reload_processed": summary.get("last_auto_reload_processed"),
            "last_auto_reload_remaining": summary.get("last_auto_reload_remaining"),
            "last_repair_execution_run": summary.get("last_repair_execution_run"),
            "last_repair_processed_count": summary.get("last_repair_processed_count"),
            "last_repair_skipped_count": summary.get("last_repair_skipped_count"),
        },
        "checked_at": utc_now_iso(),
    }

    state = load_workspace_state(workspace_id)
    state["last_owner_admin_repair_alert_display_payload"] = payload
    state["last_owner_admin_repair_alert_display_checked_at"] = payload["checked_at"]
    save_workspace_state(workspace_id, state)

    return payload
