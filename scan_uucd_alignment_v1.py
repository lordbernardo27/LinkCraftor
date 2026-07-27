from __future__ import annotations

import json
from collections import Counter,defaultdict
from pathlib import Path

PROJECT_ROOT = Path(
    r"C:\Users\HP\Documents\LinkCraftor"
).resolve()

DATA = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

WORKSPACE="ws_whattoexpect_com"

UUCD_DIRS=[
    DATA/"universal_unified_content_documents",
    DATA/"universal_unified_content_document",
    DATA/"uucd",
    DATA/"uucd_store",
]

BODY_DIRS=[
    DATA/"universal_article_body_store",
    DATA/"article_body_store",
]

REPORT=(
    DATA
    /"article_validation_scan"
    /WORKSPACE
    /"uucd_alignment_scan_v1.json"
)

required_fields=[
    "document_id",
    "workspace_id",
    "source_type",
    "title",
    "content_body",
    "content_hash",
]

optional_fields=[
    "body_ref",
    "content_ref",
    "metadata",
    "canonical_url",
    "source_id",
]

uucd_files=[]

for root in UUCD_DIRS:
    if root.exists():
        uucd_files.extend(root.rglob("*.json"))

body_files=[]

for root in BODY_DIRS:
    if root.exists():
        body_files.extend(root.rglob("*"))

body_file_set={
    f.resolve()
    for f in body_files
    if f.is_file()
}

source_counter=Counter()

missing_required=Counter()

legacy_fields=Counter()

missing_body_ref=0

existing_body_ref=0

missing_body_target=0

duplicate_doc=Counter()

duplicate_hash=Counter()

duplicate_body_ref=Counter()

doc_ids=[]
hashes=[]
body_refs=[]

website_records=0
uploaded_records=0
unknown_records=0

sample_errors=[]

for file in uucd_files:

    try:
        data=json.loads(
            file.read_text(
                encoding="utf-8-sig"
            )
        )

    except Exception as exc:
        sample_errors.append(
            {
                "file":str(file),
                "error":str(exc),
            }
        )
        continue

    source=str(
        data.get(
            "source_type",
            "UNKNOWN",
        )
    )

    source_counter[source]+=1

    if source=="website":
        website_records+=1

    elif source=="uploaded_document":
        uploaded_records+=1

    else:
        unknown_records+=1

    for field in required_fields:

        if field not in data:
            missing_required[field]+=1

    if "article_body" in data:
        legacy_fields["article_body"]+=1

    if "body" in data:
        legacy_fields["body"]+=1

    if "text" in data:
        legacy_fields["text"]+=1

    doc=data.get("document_id")

    if doc:
        doc_ids.append(doc)

    h=data.get("content_hash")

    if h:
        hashes.append(h)

    body_ref=data.get("body_ref")

    if body_ref:

        body_refs.append(body_ref)

        target=(PROJECT_ROOT/body_ref).resolve()

        if target.exists():
            existing_body_ref+=1

        else:
            missing_body_target+=1

    else:
        missing_body_ref+=1

duplicate_doc.update(doc_ids)
duplicate_hash.update(hashes)
duplicate_body_ref.update(body_refs)

duplicate_doc_count=sum(
    c-1
    for c in duplicate_doc.values()
    if c>1
)

duplicate_hash_count=sum(
    c-1
    for c in duplicate_hash.values()
    if c>1
)

duplicate_body_ref_count=sum(
    c-1
    for c in duplicate_body_ref.values()
    if c>1
)

decision="SAFE_TO_REUSE"

if website_records>0 and missing_body_ref>0:
    decision="PARTIAL_REBUILD_REQUIRED"

if website_records>0 and existing_body_ref<website_records:
    decision="FULL_WEBSITE_REBUILD_REQUIRED"

if missing_required:
    decision="FULL_REBUILD_REQUIRED"

REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT.write_text(
    json.dumps(
        {
            "decision":decision,
            "uucd_files":len(uucd_files),
            "website_records":website_records,
            "uploaded_records":uploaded_records,
            "unknown_records":unknown_records,
            "source_distribution":dict(source_counter),
            "missing_required_fields":dict(missing_required),
            "legacy_fields":dict(legacy_fields),
            "missing_body_ref":missing_body_ref,
            "existing_body_ref":existing_body_ref,
            "missing_body_target":missing_body_target,
            "duplicate_document_ids":duplicate_doc_count,
            "duplicate_hashes":duplicate_hash_count,
            "duplicate_body_refs":duplicate_body_ref_count,
            "sample_errors":sample_errors[:20],
            "source_files_modified":False,
            "data_files_modified":False,
            "runtime_modified":False,
        },
        indent=2,
    ),
    encoding="utf-8",
)

print()
print("="*100)
print("UUCD ALIGNMENT SCAN")
print("="*100)
print()

print("UUCD files:                    ",len(uucd_files))
print("Website records:              ",website_records)
print("Uploaded records:             ",uploaded_records)
print("Unknown records:              ",unknown_records)
print()

print("Missing body_ref:             ",missing_body_ref)
print("Existing body_ref targets:    ",existing_body_ref)
print("Missing body targets:         ",missing_body_target)
print()

print("Duplicate document IDs:       ",duplicate_doc_count)
print("Duplicate content hashes:     ",duplicate_hash_count)
print("Duplicate body_refs:          ",duplicate_body_ref_count)
print()

print("Missing required fields")

if missing_required:
    for k,v in missing_required.items():
        print(" ",k,":",v)
else:
    print(" None")

print()

print("Legacy fields")

if legacy_fields:
    for k,v in legacy_fields.items():
        print(" ",k,":",v)
else:
    print(" None")

print()
print("FINAL DECISION:",decision)
print()

print("Source files modified: False")
print("Data modified: False")
print("Runtime modified: False")
print()
print("Report:",REPORT)
print("="*100)
