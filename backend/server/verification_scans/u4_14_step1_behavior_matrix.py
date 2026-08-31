from backend.server.routes.files import _guess_ext, ALLOWED_EXT

print("=== U4.14 STEP 1 - FORMAT DETECTION BEHAVIOR MATRIX ===")

cases = [
    # canonical six
    ("article.txt", ".txt", True),
    ("article.md", ".md", True),
    ("article.markdown", ".markdown", True),
    ("article.html", ".html", True),
    ("article.htm", ".htm", True),
    ("article.docx", ".docx", True),

    # case normalization
    ("ARTICLE.TXT", ".txt", True),
    ("ARTICLE.MD", ".md", True),
    ("ARTICLE.MARKDOWN", ".markdown", True),
    ("ARTICLE.HTML", ".html", True),
    ("ARTICLE.HTM", ".htm", True),
    ("ARTICLE.DOCX", ".docx", True),
    ("article.MarkDown", ".markdown", True),
    ("article.HtMl", ".html", True),

    # unsupported
    ("article.pdf", ".pdf", False),
    ("article.csv", ".csv", False),
    ("article.xml", ".xml", False),
    ("article.zip", ".zip", False),
    ("article.exe", ".exe", False),

    # no-extension / trailing dot
    ("article", "", False),
    ("article.", "", False),

    # deceptive multi-extension
    ("article.md.exe", ".exe", False),
    ("article.docx.zip", ".zip", False),
    ("article.html.pdf", ".pdf", False),

    # path-like names
    (r"C:\Users\HP\Desktop\article.docx", ".docx", True),
    ("/tmp/uploads/article.html", ".html", True),
    (r"..\..\article.md", ".md", True),
    ("../../article.htm", ".htm", True),
]

failures = []

for filename, expected_ext, expected_allowed in cases:
    try:
        actual_ext = _guess_ext(filename)
        actual_allowed = actual_ext in ALLOWED_EXT
        ok = (
            actual_ext == expected_ext
            and actual_allowed == expected_allowed
        )
        status = "PASS" if ok else "FAIL"

        print(
            f"{status} | "
            f"{filename!r} "
            f"-> ext={actual_ext!r} "
            f"allowed={actual_allowed}"
        )

        if not ok:
            failures.append(filename)

    except Exception as exc:
        print(
            f"FAIL | {filename!r} "
            f"-> {type(exc).__name__}: {exc}"
        )
        failures.append(filename)

print()
print("=== HIDDEN / MALFORMED FILENAMES ===")

malformed = [
    "",
    "   ",
    ".",
    "..",
]

for filename in malformed:
    try:
        value = _guess_ext(filename)
        print(
            f"FAIL | {filename!r} unexpectedly returned {value!r}"
        )
        failures.append(repr(filename))
    except ValueError:
        print(
            f"PASS | {filename!r} -> ValueError"
        )

print()
print("=== HIDDEN EXTENSION-LIKE NAMES ===")

hidden_cases = [
    ".txt",
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".docx",
]

for filename in hidden_cases:
    actual = _guess_ext(filename)
    allowed = actual in ALLOWED_EXT
    ok = actual == "" and not allowed
    status = "PASS" if ok else "FAIL"

    print(
        f"{status} | "
        f"{filename!r} "
        f"-> ext={actual!r} "
        f"allowed={allowed}"
    )

    if not ok:
        failures.append(filename)

print()
print("========================================")

if failures:
    print("U4.14_STEP1_BEHAVIOR_MATRIX: FAIL")
    print("FAILED_CASES:")
    for failure in failures:
        print(f" - {failure}")
    raise RuntimeError(
        "U4.14 Step 1 behavior matrix failed."
    )

print("U4.14_STEP1_BEHAVIOR_MATRIX: PASS")