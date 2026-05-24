from pathlib import Path

p = Path("backend/server/routes/files.py")
s = p.read_text(encoding="utf-8")

old = '''    for fp in paths_to_remove:
        try:
            if fp.exists():
                fp.unlink()
                removed_files.append(str(fp))
        except Exception as e:
            print("[CLEAR_FILE_SESSION_REMOVE_ERROR]", str(fp), repr(e))

    try:
'''

new = '''    for fp in paths_to_remove:
        try:
            if fp.exists():
                fp.unlink()
                removed_files.append(str(fp))
        except Exception as e:
            print("[CLEAR_FILE_SESSION_REMOVE_ERROR]", str(fp), repr(e))

    # Clear actual uploaded workspace files for this session.
    # This prevents re-upload from being blocked as duplicate after Clear Session.
    try:
        ws_dir = _ws_dir(ws_norm)
        if ws_dir.exists() and ws_dir.is_dir():
            for fp in ws_dir.iterdir():
                try:
                    if fp.is_file():
                        fp.unlink()
                        removed_files.append(str(fp))
                except Exception as e:
                    print("[CLEAR_FILE_SESSION_WORKSPACE_FILE_ERROR]", str(fp), repr(e))
    except Exception as e:
        print("[CLEAR_FILE_SESSION_WORKSPACE_DIR_ERROR]", repr(e))

    try:
'''

if old not in s:
    raise SystemExit("clear_session insertion point not found")

s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
print("Patched clear_session to remove uploaded workspace files")
