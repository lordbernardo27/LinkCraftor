from pathlib import Path
import re


path = Path(
    "backend/server/routes/site_reader.py"
)

lines = path.read_text(
    encoding="utf-8-sig",
    errors="replace",
).splitlines()

target_line = 798

function_pattern = re.compile(
    r"^\s*(async\s+def|def)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\("
)

nearest_function = None

for index in range(
    min(
        target_line - 1,
        len(lines) - 1,
    ),
    -1,
    -1,
):
    match = function_pattern.match(
        lines[index]
    )

    if match:
        nearest_function = {
            "name":
                match.group(2),

            "line":
                index + 1,

            "definition":
                lines[index].strip(),
        }

        break

print(
    "Containing function:",
    nearest_function,
)

print()
print(
    "Raw indentation around damaged block:"
)

for line_number in range(
    790,
    min(
        811,
        len(lines) + 1,
    ),
):
    value = lines[
        line_number - 1
    ]

    indentation = (
        len(value)
        - len(
            value.lstrip(
                " \t"
            )
        )
    )

    print(
        f"{line_number:4}: "
        f"indent={indentation:2} "
        f"{value!r}"
    )
