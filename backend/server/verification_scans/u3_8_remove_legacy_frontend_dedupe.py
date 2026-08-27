from pathlib import Path


path = Path(r"frontend/public/assets/js/app.js")

raw = path.read_text(encoding="utf-8")

newline = "\r\n" if "\r\n" in raw else "\n"
text = raw.replace("\r\n", "\n")


def require_once(old: str, label: str) -> None:
    count = text.count(old)

    if count != 1:
        raise RuntimeError(
            f"{label}: expected exactly one match, found {count}. "
            "No production file written."
        )


def replace_once(old: str, new: str, label: str) -> None:
    global text

    require_once(old, label)
    text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 1. Remove SHA-256/localStorage duplicate helper subsystem.
# ------------------------------------------------------------

old = '''async function lcFileSha256(file) {
  const buffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest("SHA-256", buffer);
  return Array.from(new Uint8Array(hashBuffer))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

function lcUploadHashKey(ws) {
  return `lc_uploaded_file_hashes_${ws || "default"}`;
}

function lcLoadUploadedHashes(ws) {
  try {
    return new Set(JSON.parse(localStorage.getItem(lcUploadHashKey(ws)) || "[]"));
  } catch {
    return new Set();
  }
}

function lcSaveUploadedHashes(ws, set) {
  try {
    localStorage.setItem(lcUploadHashKey(ws), JSON.stringify(Array.from(set)));
  } catch {}
}

'''

replace_once(
    old,
    "",
    "legacy upload-hash helper block",
)

# ------------------------------------------------------------
# 2. Remove obsolete duplicate counter.
# ------------------------------------------------------------

replace_once(
    '''  let accepted = 0;
  let skipped = 0;
  let duplicates = 0;
''',
    '''  let accepted = 0;
  let skipped = 0;
''',
    "duplicate counter",
)

# ------------------------------------------------------------
# 3. Remove pre-upload hash calculation and blocking.
# ------------------------------------------------------------

replace_once(
    '''      const ws = getCurrentWorkspaceId("");
      const uploadedHashes = lcLoadUploadedHashes(ws);
      const fileHash = await lcFileSha256(file);

      if (uploadedHashes.has(fileHash)) {
        duplicates++;
        showToast(errorBox, "This document already exists in this session.", 2400);
        continue;
      }

      const data = await uploadFile(file, ws);
''',
    '''      const ws = getCurrentWorkspaceId("");

      const data = await uploadFile(file, ws);
''',
    "pre-upload duplicate suppression",
)

# ------------------------------------------------------------
# 4. Remove stale backend duplicate_detected response contract.
# ------------------------------------------------------------

replace_once(
    '''      if (data?.duplicate_detected || data?.ok === false) {
        if (data?.duplicate_detected) {
          duplicates++;
          uploadedHashes.add(fileHash);
          lcSaveUploadedHashes(ws, uploadedHashes);

          showToast(
            errorBox,
            data?.message || "This document already exists in this session.",
            2400
          );
          continue;
        }

        throw new Error(data?.message || data?.reason || "Upload failed.");
      }
''',
    '''      if (data?.ok === false) {
        throw new Error(
          data?.message || data?.reason || "Upload failed."
        );
      }
''',
    "stale duplicate_detected response handling",
)

# ------------------------------------------------------------
# 5. Remove unused hash attachment/persistence after success.
# ------------------------------------------------------------

replace_once(
    '''      data.file_hash = fileHash;

      uploadedHashes.add(fileHash);
      lcSaveUploadedHashes(ws, uploadedHashes);

''',
    "",
    "post-success file hash persistence",
)

# ------------------------------------------------------------
# 6. Remove duplicate-only empty-upload message branch.
# ------------------------------------------------------------

replace_once(
    '''      if (duplicates) {
        parts.push("File already exists");
      }

''',
    "",
    "duplicate-only status message",
)

# ------------------------------------------------------------
# 7. Remove obsolete clear-session dedupe cleanup.
# ------------------------------------------------------------

replace_once(
    '''  // Clear upload duplicate hash memory.
try {
  localStorage.removeItem(lcUploadHashKey(ws));
} catch {}

try {
  window.LC_UPLOAD_FILE_SIGNATURES = new Set();
} catch {}

''',
    "",
    "legacy duplicate-state cleanup",
)

# ------------------------------------------------------------
# Final safety check BEFORE write.
# ------------------------------------------------------------

for forbidden in (
    "lcFileSha256",
    "lcUploadHashKey",
    "lcLoadUploadedHashes",
    "lcSaveUploadedHashes",
    "uploadedHashes",
    "data.file_hash",
    "duplicate_detected",
    "LC_UPLOAD_FILE_SIGNATURES",
    "lc_uploaded_file_hashes_",
):
    if forbidden in text:
        raise RuntimeError(
            f"Legacy duplicate-upload marker remains: {forbidden}. "
            "No production file written."
        )

path.write_text(
    text.replace("\n", newline),
    encoding="utf-8",
    newline="",
)

print("U3.8_FRONTEND_DEDUPE_PATCH: APPLIED")