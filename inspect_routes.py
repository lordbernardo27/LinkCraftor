from backend.server.main import app

print("REGISTERED ROUTES")
print("=" * 80)

for r in app.routes:
    methods = ",".join(sorted(getattr(r, "methods", []) or []))
    path = getattr(r, "path", "")
    if "site" in path or "workspace" in path or "domain" in path:
        print(methods, path)
