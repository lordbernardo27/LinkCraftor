from pathlib import Path

p = Path("backend/server/routes/site_reader.py")
code = p.read_text(encoding="utf-8")

import_line = "from backend.server.runtime.live_route_orchestration_hooks import enqueue_and_run_website_ingestion_job_v1\n"

if import_line not in code:
    marker = "from fastapi import APIRouter, Query\n"
    if marker not in code:
        raise SystemExit("Could not find site_reader.py import marker.")
    code = code.replace(marker, marker + import_line)

# Insert just before the connect_domain route returns.
# We use a conservative marker based on the route region.
route_marker = '@router.post("/workspace/connect_domain")'
route_pos = code.find(route_marker)
if route_pos < 0:
    raise SystemExit("Could not find connect_domain route.")

after = code[route_pos:]
return_pos = after.find("return ")
if return_pos < 0:
    raise SystemExit("Could not find return inside connect_domain route.")

absolute_return = route_pos + return_pos

insert = '''
    try:
        orchestration_result = enqueue_and_run_website_ingestion_job_v1(
            workspace_id=workspace_id,
            domain=domain if "domain" in locals() else "",
            payload={
                "route": "/api/site/workspace/connect_domain",
            },
        )
    except Exception as e:
        orchestration_result = {
            "ok": False,
            "error": f"website_orchestration_failed:{str(e)[:160]}",
        }

'''

if "enqueue_and_run_website_ingestion_job_v1(" not in after[:return_pos]:
    code = code[:absolute_return] + insert + code[absolute_return:]

# Add orchestration_result into returned dict if route returns a dict literal.
code = code.replace(
    '"ok": True,',
    '"ok": True,\n        "universal_knowledge_orchestration": orchestration_result if "orchestration_result" in locals() else None,',
    1
)

p.write_text(code, encoding="utf-8")
print("Patched site_reader.py connect_domain route.")
