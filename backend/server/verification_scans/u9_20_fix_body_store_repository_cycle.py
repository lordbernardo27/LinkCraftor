from pathlib import Path

path = Path(
    r"backend/server/universal_article_body_store/body_store_repository_v1.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)

old_import = '''from backend.server.universal_article_body_store.body_store_writer_v1 import (
    write_verified_body_from_envelope_v1,
)

'''

if old_import not in text:
    raise RuntimeError(
        "Expected top-level body_store_writer_v1 import was not found."
    )

text = text.replace(
    old_import,
    "",
    1,
)

old_call = '''    return write_verified_body_from_envelope_v1(
        envelope,
        project_root=project_root,
        overwrite=overwrite,
    )
'''

new_call = '''    from backend.server.universal_article_body_store.body_store_writer_v1 import (
        write_verified_body_from_envelope_v1,
    )

    return write_verified_body_from_envelope_v1(
        envelope,
        project_root=project_root,
        overwrite=overwrite,
    )
'''

if old_call not in text:
    raise RuntimeError(
        "Expected repository writer call was not found."
    )

text = text.replace(
    old_call,
    new_call,
    1,
)

path.write_text(
    text,
    encoding="utf-8",
)

print("U9.20_PATCH_STATUS=BODY_STORE_WRITER_IMPORT_LAZY_LOADED")
print(
    "TARGET="
    + str(path)
)