from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    return here.parents[1] / "data"


def _safe_ws(workspace_id: str) -> str:
    ws = str(workspace_id or "default").strip()
    return ws if ws else "default"


def _feedback_path(workspace_id: str) -> Path:
    return _data_dir() / "topic_clusters" / f"workspace_topic_cluster_feedback_{_safe_ws(workspace_id)}.json"


def _read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def update_cluster_feedback_from_decision(event: Dict[str, Any]) -> Dict[str, Any]:
    workspace_id = str(event.get("workspaceId") or event.get("workspace_id") or "default").strip()
    event_type = str(event.get("eventType") or event.get("event_type") or "").strip()
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}

    if event_type not in {"LINK_SUGGESTION_ACCEPTED", "LINK_SUGGESTION_REJECTED"}:
        return {"ok": True, "updated": False, "reason": "not_link_suggestion_decision"}

    cluster_name = str(
        payload.get("cluster_name")
        or payload.get("clusterName")
        or payload.get("cluster")
        or ""
    ).strip()

    cluster_score = payload.get("cluster_score") or payload.get("clusterScore") or 0
    phrase = str(payload.get("phraseText") or payload.get("phrase") or "").strip()
    url = str(payload.get("url") or payload.get("targetUrl") or "").strip()
    title = str(payload.get("title") or payload.get("targetTitle") or "").strip()

    if not cluster_name:
        return {"ok": True, "updated": False, "reason": "missing_cluster_name"}

    path = _feedback_path(workspace_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = _read_json(path, {"workspace_id": _safe_ws(workspace_id), "clusters": {}, "updated_at": None})
    if not isinstance(data, dict):
        data = {"workspace_id": _safe_ws(workspace_id), "clusters": {}, "updated_at": None}

    clusters = data.get("clusters")
    if not isinstance(clusters, dict):
        clusters = {}

    rec = clusters.get(cluster_name)
    if not isinstance(rec, dict):
        rec = {
            "cluster_name": cluster_name,
            "accepted": 0,
            "rejected": 0,
            "total": 0,
            "acceptance_rate": 0.0,
            "rejection_rate": 0.0,
            "last_decision_at": None,
            "examples": [],
        }

    if event_type == "LINK_SUGGESTION_ACCEPTED":
        rec["accepted"] = int(rec.get("accepted") or 0) + 1
        outcome = "accepted"
    else:
        rec["rejected"] = int(rec.get("rejected") or 0) + 1
        outcome = "rejected"

    total = int(rec.get("accepted") or 0) + int(rec.get("rejected") or 0)
    rec["total"] = total
    rec["acceptance_rate"] = round((int(rec.get("accepted") or 0) / total), 4) if total else 0.0
    rec["rejection_rate"] = round((int(rec.get("rejected") or 0) / total), 4) if total else 0.0
    rec["last_decision_at"] = datetime.now(timezone.utc).isoformat()

    examples = rec.get("examples")
    if not isinstance(examples, list):
        examples = []

    examples.append({
        "outcome": outcome,
        "phrase": phrase,
        "url": url,
        "title": title,
        "cluster_score": cluster_score,
        "timestamp": event.get("timestamp"),
    })

    rec["examples"] = examples[-20:]
    clusters[cluster_name] = rec

    data["workspace_id"] = _safe_ws(workspace_id)
    data["clusters"] = clusters
    data["updated_at"] = datetime.now(timezone.utc).isoformat()

    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "ok": True,
        "updated": True,
        "path": str(path),
        "cluster_name": cluster_name,
        "outcome": outcome,
        "total": total,
    }



def load_cluster_feedback_stats(workspace_id: str) -> Dict[str, Any]:
    path = _feedback_path(workspace_id)
    data = _read_json(path, {"workspace_id": _safe_ws(workspace_id), "clusters": {}})

    if not isinstance(data, dict):
        return {"workspace_id": _safe_ws(workspace_id), "clusters": {}}

    clusters = data.get("clusters")
    if not isinstance(clusters, dict):
        clusters = {}

    return {
        "workspace_id": _safe_ws(workspace_id),
        "clusters": clusters,
        "updated_at": data.get("updated_at"),
        "path": str(path),
    }


def get_cluster_feedback(workspace_id: str, cluster_name: str) -> Dict[str, Any]:
    stats = load_cluster_feedback_stats(workspace_id)
    clusters = stats.get("clusters") if isinstance(stats, dict) else {}

    if not isinstance(clusters, dict):
        return {}

    return clusters.get(str(cluster_name or "").strip()) or {}
