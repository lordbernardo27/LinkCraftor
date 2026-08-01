from __future__ import annotations

from pathlib import Path


root = Path(r"C:\Users\HP\Documents\LinkCraftor")
path = root / "frontend/public/assets/js/app.js"

source = path.read_text(encoding="utf-8-sig")


def find_function_start(text: str, name: str) -> int:
    markers = [
        f"async function {name}(",
        f"function {name}(",
        f"const {name} = async (",
        f"let {name} = async (",
    ]

    positions = [
        text.find(marker)
        for marker in markers
        if text.find(marker) >= 0
    ]

    if not positions:
        raise RuntimeError(f"Function not found: {name}")

    return min(positions)


def find_body_open(text: str, start: int) -> int:
    index = text.find("{", start)

    if index < 0:
        raise RuntimeError("Function body opening brace not found.")

    return index


function_name = "lcAutosaveWorkspaceSession"
start = find_function_start(source, function_name)
body_open = find_body_open(source, start)

guard_marker = "[LinkCraftor Autosave] skipped: workspace_id unavailable"

if guard_marker in source[start:start + 3000]:
    print("AUTOSAVE_WORKSPACE_GUARD_ALREADY_PRESENT")
else:
    guard = r'''

  const autosaveWorkspaceId = String(
    window.LC_WORKSPACE_ID ||
    window.currentWorkspaceId ||
    localStorage.getItem("lc_workspace_id") ||
    localStorage.getItem("workspace_id") ||
    ""
  ).trim();

  if (
    !autosaveWorkspaceId ||
    autosaveWorkspaceId === "default" ||
    autosaveWorkspaceId === "null" ||
    autosaveWorkspaceId === "undefined"
  ) {
    console.debug(
      "[LinkCraftor Autosave] skipped: workspace_id unavailable"
    );

    return {
      ok: true,
      skipped: true,
      reason: "workspace_id_unavailable",
    };
  }
'''

    updated = source[:body_open + 1] + guard + source[body_open + 1:]

    path.write_text(updated, encoding="utf-8")

    print("AUTOSAVE_WORKSPACE_GUARD_PATCHED")
    print(f"FILE={path}")
