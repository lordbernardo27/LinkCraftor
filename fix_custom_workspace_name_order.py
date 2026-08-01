from __future__ import annotations

from pathlib import Path


root = Path(r"C:\Users\HP\Documents\LinkCraftor")
path = root / "frontend/public/assets/js/app.js"

source = path.read_text(encoding="utf-8-sig")
lines = source.splitlines()


declaration_fragments = (
    "const customWorkspaceName =",
    "let customWorkspaceName =",
    "var customWorkspaceName =",
)

usage_fragment = "customWorkspaceName"
workspace_input_fragment = "workspaceNameInput"
domain_mode_fragment = 'selectedWorkspaceMode !== "domain"'
connect_endpoint_fragment = "/api/site/workspace/connect_domain"


# Locate the Domain Workspace handler region.
domain_guard = next(
    (
        index
        for index, line in enumerate(lines)
        if domain_mode_fragment in line
    ),
    None,
)

if domain_guard is None:
    raise RuntimeError(
        "Domain Workspace guard was not found."
    )

connect_endpoint = next(
    (
        index
        for index in range(domain_guard, len(lines))
        if connect_endpoint_fragment in lines[index]
    ),
    None,
)

if connect_endpoint is None:
    raise RuntimeError(
        "Connect Domain endpoint was not found after Domain guard."
    )


# Find the start of the enclosing event-handler/function block.
handler_start = domain_guard

while handler_start >= 0:
    stripped = lines[handler_start].strip()

    if (
        "addEventListener" in stripped
        or stripped.startswith("async function ")
        or stripped.startswith("function ")
        or "onclick" in stripped
    ):
        break

    handler_start -= 1

if handler_start < 0:
    handler_start = max(0, domain_guard - 150)


# Find a safe end boundary.
handler_end = min(len(lines), connect_endpoint + 250)


# Remove every declaration of customWorkspaceName from this handler region.
declaration_indices = []

for index in range(handler_start, handler_end):
    stripped = lines[index].strip()

    if any(
        stripped.startswith(fragment)
        for fragment in declaration_fragments
    ):
        declaration_indices.append(index)


if not declaration_indices:
    raise RuntimeError(
        "No customWorkspaceName declaration was found."
    )


for index in reversed(declaration_indices):
    del lines[index]

    if index < domain_guard:
        domain_guard -= 1

    if index < connect_endpoint:
        connect_endpoint -= 1

    handler_end -= 1


# Insert one canonical declaration before the Domain guard and before all uses.
canonical_declaration = [
    "    const customWorkspaceName = String(",
    '      workspaceNameInput?.value || ""',
    "    ).trim();",
    "",
]

lines[domain_guard:domain_guard] = canonical_declaration


updated = "\n".join(lines).rstrip() + "\n"
path.write_text(updated, encoding="utf-8")


# Verification against the updated source.
updated_lines = updated.splitlines()

updated_domain_guard = next(
    index
    for index, line in enumerate(updated_lines)
    if domain_mode_fragment in line
)

updated_connect_endpoint = next(
    index
    for index in range(updated_domain_guard, len(updated_lines))
    if connect_endpoint_fragment in updated_lines[index]
)

declarations = [
    index
    for index, line in enumerate(updated_lines)
    if any(
        line.strip().startswith(fragment)
        for fragment in declaration_fragments
    )
]

relevant_declarations = [
    index
    for index in declarations
    if handler_start <= index <= updated_connect_endpoint
]

if len(relevant_declarations) != 1:
    raise RuntimeError(
        "Expected exactly one relevant customWorkspaceName declaration; "
        f"found {len(relevant_declarations)}."
    )

declaration_index = relevant_declarations[0]

first_use_index = next(
    (
        index
        for index in range(handler_start, updated_connect_endpoint + 1)
        if usage_fragment in updated_lines[index]
        and index != declaration_index
    ),
    None,
)

if first_use_index is not None and declaration_index > first_use_index:
    raise RuntimeError(
        "customWorkspaceName is still declared after its first use."
    )

print("CUSTOM_WORKSPACE_NAME_ORDER_FIXED")
print(f"DECLARATION_LINE={declaration_index + 1}")
print(f"DOMAIN_GUARD_LINE={updated_domain_guard + 1}")
print(f"CONNECT_ENDPOINT_LINE={updated_connect_endpoint + 1}")
print(f"FILE={path}")
