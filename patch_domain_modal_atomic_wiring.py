from __future__ import annotations

from pathlib import Path


root = Path(r"C:\Users\HP\Documents\LinkCraftor")
path = root / "frontend/public/assets/js/app.js"

source = path.read_text(encoding="utf-8-sig")
lines = source.splitlines()


def find_line(
    needle: str,
    *,
    start: int = 0,
) -> int:
    for index in range(start, len(lines)):
        if needle in lines[index]:
            return index

    raise RuntimeError(f"Marker not found: {needle}")


# ------------------------------------------------------------------
# Locate the Domain Workspace branch only.
# ------------------------------------------------------------------

domain_guard_index = find_line(
    'if (selectedWorkspaceMode !== "domain")'
)

domain_value_index = find_line(
    'const domain = (domainInput.value || "").trim();',
    start=domain_guard_index,
)

connect_endpoint_index = find_line(
    '/api/site/workspace/connect_domain',
    start=domain_value_index,
)

next_connect_endpoint = None

for index in range(connect_endpoint_index + 1, len(lines)):
    if "/api/site/workspace/connect_domain" in lines[index]:
        next_connect_endpoint = index
        break

domain_branch_end = (
    next_connect_endpoint
    if next_connect_endpoint is not None
    else len(lines)
)


# ------------------------------------------------------------------
# 1. Read Workspace Name before submitting Domain Workspace request.
# ------------------------------------------------------------------

workspace_name_line = (
    '    const customWorkspaceName = '
    '(workspaceNameInput?.value || "").trim();'
)

if workspace_name_line not in lines[
    max(domain_guard_index, domain_value_index - 5):
    connect_endpoint_index
]:
    lines.insert(
        domain_value_index,
        workspace_name_line,
    )

    domain_value_index += 1
    connect_endpoint_index += 1
    domain_branch_end += 1


# ------------------------------------------------------------------
# 2. Replace Domain request payload with atomic modal contract.
# ------------------------------------------------------------------

payload_index = find_line(
    "body: JSON.stringify({ domain })",
    start=connect_endpoint_index,
)

if payload_index >= domain_branch_end:
    raise RuntimeError(
        "Domain request payload marker was found outside Domain branch."
    )

replacement_payload = [
    "          body: JSON.stringify({",
    "            workspace_id: null,",
    "            workspace_name: customWorkspaceName || null,",
    '            workspace_mode: "domain",',
    "            domain,",
    "            site_url: null",
    "          })",
]

lines[payload_index:payload_index + 1] = replacement_payload

payload_growth = len(replacement_payload) - 1
domain_branch_end += payload_growth


# ------------------------------------------------------------------
# 3. Use the backend-persisted canonical Workspace Name.
# ------------------------------------------------------------------

old_workspace_name = (
    "        const workspaceName = "
    "customWorkspaceName || identity.workspaceName;"
)

new_workspace_name = (
    "        const workspaceName = "
    "data.workspace_name || customWorkspaceName || identity.workspaceName;"
)

workspace_name_assignment_index = find_line(
    old_workspace_name,
    start=connect_endpoint_index,
)

if workspace_name_assignment_index >= domain_branch_end:
    raise RuntimeError(
        "Domain Workspace name assignment was found outside Domain branch."
    )

lines[workspace_name_assignment_index] = new_workspace_name


# ------------------------------------------------------------------
# 4. Remove only the Domain branch's redundant profile-save request.
#
# Preserve the earlier Sitemap Workspace request:
# /api/workspace/workspace-folder/name
# ------------------------------------------------------------------

domain_profile_fetch_index = find_line(
    'await fetch("/api/workspace/workspace-folder/name"',
    start=connect_endpoint_index,
)

if domain_profile_fetch_index >= domain_branch_end:
    raise RuntimeError(
        "Domain profile-save request was not found inside Domain branch."
    )

try_start_index = domain_profile_fetch_index

while (
    try_start_index >= connect_endpoint_index
    and lines[try_start_index].strip() != "try {"
):
    try_start_index -= 1

if try_start_index < connect_endpoint_index:
    raise RuntimeError(
        "Could not locate Domain profile-save try block."
    )

brace_balance = 0
try_end_index = None

for index in range(try_start_index, domain_branch_end):
    line = lines[index]

    brace_balance += line.count("{")
    brace_balance -= line.count("}")

    if index > try_start_index and brace_balance == 0:
        try_end_index = index
        break

if try_end_index is None:
    raise RuntimeError(
        "Could not determine the end of Domain profile-save block."
    )

replacement_comment = [
    "        // Workspace profile is persisted atomically by",
    "        // /api/site/workspace/connect_domain.",
]

lines[try_start_index:try_end_index + 1] = replacement_comment


# ------------------------------------------------------------------
# Write patched frontend.
# ------------------------------------------------------------------

updated = "\n".join(lines).rstrip() + "\n"
path.write_text(updated, encoding="utf-8")

print("DOMAIN_MODAL_ATOMIC_WIRING_PATCHED")
print(f"FILE={path}")
