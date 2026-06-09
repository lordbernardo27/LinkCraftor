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


def _concept_dir() -> Path:
    return _data_dir() / "concepts"


def concept_store_path(workspace_id: str) -> Path:
    return _concept_dir() / f"workspace_concepts_{_safe_ws(workspace_id)}.json"


def load_workspace_concepts(workspace_id: str) -> Dict[str, Any]:
    fp = concept_store_path(workspace_id)

    if not fp.exists():
        return {
            "workspace_id": _safe_ws(workspace_id),
            "type": "workspace_concepts",
            "concepts": {},
            "metadata": {
                "source": "auto_generated_workspace_concept_store",
                "version": "v1",
            },
        }

    try:
        obj = json.loads(fp.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def save_workspace_concepts(workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    fp = concept_store_path(workspace_id)
    fp.parent.mkdir(parents=True, exist_ok=True)

    data["workspace_id"] = _safe_ws(workspace_id)
    data["type"] = "workspace_concepts"

    fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def normalize_concept_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").lower()).strip()
