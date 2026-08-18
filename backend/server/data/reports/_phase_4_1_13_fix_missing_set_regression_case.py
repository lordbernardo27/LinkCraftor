from pathlib import Path


path = Path(
    r"C:\Users\HP\Documents\LinkCraftor\backend\server\data\reports\_phase_4_1_13_worker_capability_regression_runner.py"
)

text = path.read_text(
    encoding="utf-8-sig"
)


old = '''        (
            (),
            (
                "z.cap",
                "a.cap",
            ),
            (
                "z.cap",
                "a.cap",
            ),
        ),
'''


new = '''        (
            (),
            (
                "z.cap",
                "a.cap",
            ),
            (
                "a.cap",
            ),
        ),
'''


if old not in text:

    raise SystemExit(
        (
            "Expected missing_set_forgery_4 test case "
            "was not found in regression runner."
        )
    )


text = text.replace(
    old,
    new,
    1,
)


path.write_text(
    text,
    encoding="utf-8",
)


print(
    "4.1.13 missing_set_forgery_4 regression case corrected."
)

print(
    (
        "The test now supplies an actually incomplete "
        "missing-capability set instead of merely "
        "supplying the correct set in non-canonical order."
    )
)
