from pathlib import Path

# ------------------------------------------------------------
# PATCH 1: Narrow unsafe synonym expansion
# ------------------------------------------------------------
p = Path("backend/server/engine/intelligence_target_resolver.py")
s = p.read_text(encoding="utf-8")

backup = p.with_suffix(".py.bak_synonym_cluster_fix")
backup.write_text(s, encoding="utf-8")

old_syn = '''    {"window", "range", "period", "span", "phase", "stage"},'''
new_syn = '''    # Keep "window" narrow. Do not expand it into phase/stage/period.
    # That caused "fertile window" to match unrelated "labor phases/stages" pages.
    {"window", "range", "span"},
    {"phase", "stage"},
    {"period"},'''

if old_syn not in s:
    raise SystemExit("Synonym group marker not found")
s = s.replace(old_syn, new_syn, 1)


old_cluster = '''            cluster_matches = find_topic_clusters_for_text(
                workspace_id,
                " ".join([
                    str(anchor_phrase or ""),
                    str(title or ""),
                    str(url or ""),
                    str(intelligence.get("path") or ""),
                ]),
                limit=3,
            )
'''

new_cluster = '''            # Cluster matching must be phrase-first.
            # Do NOT include target title/url/path here, or the target page can drag
            # itself into a strong but unrelated cluster.
            cluster_matches = find_topic_clusters_for_text(
                workspace_id,
                str(anchor_phrase or ""),
                limit=3,
            )
'''

if old_cluster not in s:
    raise SystemExit("Cluster matching block marker not found")
s = s.replace(old_cluster, new_cluster, 1)

p.write_text(s, encoding="utf-8")

print("✅ Synonym + cluster contamination fix applied.")
print(f"Backup created: {backup}")
