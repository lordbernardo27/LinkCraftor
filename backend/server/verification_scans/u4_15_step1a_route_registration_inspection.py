import backend.server.routes.files as files_route

print("=== U4.15 STEP 1A - ROUTE REGISTRATION INSPECTION ===")
print()

print("ROUTER PREFIX:")
print(repr(getattr(files_route.router, "prefix", None)))

print()
print("ROUTER ROUTES:")

for route in files_route.router.routes:
    path = getattr(route, "path", None)
    methods = sorted(getattr(route, "methods", set()) or set())
    name = getattr(route, "name", None)

    print(
        f"path={path!r} "
        f"methods={methods} "
        f"name={name!r}"
    )

print()
print("U4.15_STEP1A_ROUTE_REGISTRATION_INSPECTION: PASS")