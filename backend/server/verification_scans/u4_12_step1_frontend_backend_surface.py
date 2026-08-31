from pathlib import Path
import inspect

import backend.server.routes.files as f

print("=== U4.12 STEP 1 - FRONTEND / BACKEND ALIGNMENT SURFACE ===")

print()
print("=== BACKEND ALLOWED_EXT ===")
print(sorted(f.ALLOWED_EXT))

print()
print("=== FRONTEND MATCHES ===")

frontend_path = Path("frontend/public/assets/js/app.js")
frontend_source = frontend_path.read_text(
    encoding="utf-8",
    errors="replace",
)

terms = [
    ".docx,.md,.markdown,.html,.htm,.txt",
    "canonicalSessionFormat",
    'value === ".markdown"',
    'value === ".htm"',
    "/api/files/upload",
    "FormData",
    'append("file"',
    "append('file'",
    "content_type",
    "mime",
    "magic",
    "format_router",
    "route_format",
    "dispatch_format",
]

for i, line in enumerate(frontend_source.splitlines(), 1):
    if any(term.lower() in line.lower() for term in terms):
        print(f"{i}: {line}")

print()
print("=== BACKEND UPLOAD ROUTE ===")

route_source = inspect.getsource(f.upload_file)

route_terms = [
    "@router.post",
    "UploadIntakeDependencies",
    "guess_extension",
    "allowed_extensions",
    "run_upload_document",
    "content_type",
    "document_id",
    "doc_id",
]

for i, line in enumerate(route_source.splitlines(), 1):
    if any(term in line for term in route_terms):
        print(f"{i}: {line}")