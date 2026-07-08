from pathlib import Path

p = Path("backend/server/routes/site_workspace.py")
code = p.read_text(encoding="utf-8-sig").replace("\ufeff", "")

backup = p.with_suffix(".py.bak_remove_trigger_arg")
backup.write_text(code, encoding="utf-8")

code = code.replace(
''',
        trigger="live_connect_domain_route",
''',
'''
'''
)

p.write_text(code, encoding="utf-8")

print("Removed unsupported trigger argument from connect_domain route.")
print("Backup:", backup)
