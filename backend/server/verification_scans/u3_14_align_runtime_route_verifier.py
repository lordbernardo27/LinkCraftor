from pathlib import Path

path = Path(
    "backend/server/verification_scans/u3_14_route_wiring_verifier.py"
)

text = path.read_text(
    encoding="utf-8"
)

old = '''upload_routes = []

for route in files_route.router.routes:
    path = getattr(route, "path", "")
    methods = set(getattr(route, "methods", set()) or set())

    if path == "/upload" and "POST" in methods:
        upload_routes.append(route)'''

new = '''upload_routes = []

router_prefix = str(
    getattr(files_route.router, "prefix", "") or ""
).rstrip("/")

expected_upload_path = (
    f"{router_prefix}/upload"
    if router_prefix
    else "/upload"
)

check(
    "FILES_ROUTER_PREFIX_IS_CANONICAL",
    router_prefix == "/api/files",
)

check(
    "EXPECTED_RUNTIME_UPLOAD_PATH_IS_CANONICAL",
    expected_upload_path == "/api/files/upload",
)

for route in files_route.router.routes:
    path = getattr(route, "path", "")
    methods = set(getattr(route, "methods", set()) or set())

    if (
        path == expected_upload_path
        and "POST" in methods
    ):
        upload_routes.append(route)'''

if old not in text:
    raise RuntimeError(
        "Expected runtime-route discovery block was not found."
    )

text = text.replace(
    old,
    new,
    1,
)

path.write_text(
    text,
    encoding="utf-8",
)

print(
    "U3.14_RUNTIME_ROUTE_VERIFIER_ALIGNMENT: APPLIED"
)