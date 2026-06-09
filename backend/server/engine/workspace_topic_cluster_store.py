from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict


def _data_dir() -> Path:
    here = Path(__file__).resolve()
    return here.parents[1] / "data"


def _safe_ws(workspace_id: str) -> str:
    ws = str(workspace_id or "default").strip()
    return ws if ws else "default"


def _cluster_dir() -> Path:
    return _data_dir() / "topic_clusters"


def topic_cluster_store_path(workspace_id: str) -> Path:
    return _cluster_dir() / f"workspace_topic_clusters_{_safe_ws(workspace_id)}.json"


def normalize_topic_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()


def load_workspace_topic_clusters(workspace_id: str) -> Dict[str, Any]:
    fp = topic_cluster_store_path(workspace_id)

    if not fp.exists():
        return {
            "workspace_id": _safe_ws(workspace_id),
            "type": "workspace_topic_clusters",
            "cluster_count": 0,
            "clusters": {},
            "metadata": {
                "source": "workspace_topic_cluster_store",
                "version": "v1",
            },
        }

    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def save_workspace_topic_clusters(workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    fp = topic_cluster_store_path(workspace_id)
    fp.parent.mkdir(parents=True, exist_ok=True)

    data["workspace_id"] = _safe_ws(workspace_id)
    data["type"] = "workspace_topic_clusters"

    fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def find_topic_clusters_for_text(workspace_id: str, text: Any, limit: int = 5) -> List[Dict[str, Any]]:
    data = load_workspace_topic_clusters(workspace_id)
    clusters = data.get("clusters") or {}
    if not isinstance(clusters, dict):
        return []

    query = set(
        t for t in re.findall(r"[a-z0-9]+", normalize_topic_text(text))
        if len(t) >= 3
    )

    if not query:
        return []

    scored = []

    for cluster in clusters.values():
        if not isinstance(cluster, dict):
            continue

        keywords = set(str(x).strip().lower() for x in (cluster.get("keywords") or []) if str(x).strip())
        primary = str(cluster.get("primary_token") or cluster.get("name") or "").strip().lower()
        if primary:
            keywords.add(primary)

        matched = sorted(list(query & keywords))
        if not matched:
            continue

        anchor_primary_bonus = 0.35 if primary in query else 0.0
        matched_ratio = len(matched) / max(3, len(query))
        purity_bonus = min(0.15, float(cluster.get("purity_score") or 0) * 0.15)

        score = min(1.0, matched_ratio + anchor_primary_bonus + purity_bonus)

        scored.append({
            "cluster_id": cluster.get("cluster_id"),
            "cluster_name": cluster.get("name"),
            "primary_token": primary,
            "matched_terms": matched,
            "score": round(score, 4),
            "confidence": cluster.get("confidence"),
            "purity_score": cluster.get("purity_score"),
            "primary_coverage": cluster.get("primary_coverage"),
            "broad_terms": cluster.get("broad_terms"),
        })

    scored.sort(
        key=lambda x: (float(x.get("score") or 0), float(x.get("confidence") or 0)),
        reverse=True,
    )
    return scored[:limit]

