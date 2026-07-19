"""Inspect the structure of the three remaining Article Validation failures."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


WORKSPACE_ID = "ws_whattoexpect_com"

DATA_ROOT = (
    PROJECT_ROOT
    / "backend"
    / "server"
    / "data"
)

POPULATION_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_population_v3_verification.json"
)

OUTPUT_REPORT_PATH = (
    DATA_ROOT
    / "article_validation_scan"
    / WORKSPACE_ID
    / "article_validation_three_failure_structure_v3.json"
)


def normalize_text(
    value: str,
) -> str:
    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip()


def sha256_text(
    value: str,
) -> str:
    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


def sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                block
            )

    return digest.hexdigest()


def load_json(
    path: Path,
) -> dict[str, Any]:
    value = json.loads(
        path.read_text(
            encoding="utf-8-sig",
        )
    )

    if not isinstance(
        value,
        dict,
    ):
        raise RuntimeError(
            f"Expected JSON object: {path}"
        )

    return value


def load_jsonl(
    path: Path,
) -> list[dict[str, Any]]:
    records: list[
        dict[str, Any]
    ] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        for line_number, line in enumerate(
            handle,
            start=1,
        ):
            line = line.strip()

            if not line:
                continue

            value = json.loads(
                line
            )

            if not isinstance(
                value,
                dict,
            ):
                raise RuntimeError(
                    "JSONL record is not an object at "
                    f"line {line_number}: {path}"
                )

            records.append(
                value
            )

    return records


def write_json(
    path: Path,
    payload: dict[str, Any],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def resolve_reference(
    raw_value: Any,
) -> Path:
    supplied = Path(
        str(
            raw_value or ""
        ).strip()
    )

    resolved = (
        supplied
        if supplied.is_absolute()
        else PROJECT_ROOT / supplied
    ).resolve()

    if not resolved.is_file():
        raise FileNotFoundError(
            f"Article file does not exist: {resolved}"
        )

    return resolved


class StructuralHTMLParser(
    HTMLParser
):
    SEMANTIC_BLOCK_TAGS = {
        "p",
        "li",
        "blockquote",
        "figcaption",
        "dd",
        "dt",
        "td",
    }

    CONTAINER_TAGS = {
        "article",
        "main",
        "section",
        "div",
    }

    HEADING_TAGS = {
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }

    SKIP_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
        "template",
        "form",
        "nav",
        "footer",
        "aside",
    }

    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(
        self,
    ) -> None:
        super().__init__(
            convert_charrefs=True
        )

        self.stack: list[
            dict[str, Any]
        ] = []

        self.root_counts: Counter[str] = Counter()
        self.tag_counts: Counter[str] = Counter()

        self.semantic_blocks: list[
            dict[str, Any]
        ] = []

        self.leaf_containers: list[
            dict[str, Any]
        ] = []

        self.headings: list[
            dict[str, Any]
        ] = []

        self.skip_depth = 0

    def _location(
        self,
        frame: dict[str, Any],
    ) -> dict[str, Any]:
        attrs = frame[
            "attrs"
        ]

        class_value = str(
            attrs.get(
                "class"
            )
            or ""
        ).strip()

        return {
            "tag":
                frame[
                    "tag"
                ],

            "path":
                frame[
                    "path"
                ],

            "id":
                str(
                    attrs.get(
                        "id"
                    )
                    or ""
                ).strip(),

            "class":
                class_value[:250],
        }

    def _finalize(
        self,
        frame: dict[str, Any],
    ) -> None:
        text = normalize_text(
            " ".join(
                frame[
                    "text_parts"
                ]
            )
        )

        word_count = len(
            text.split()
        )

        tag = frame[
            "tag"
        ]

        base = {
            **self._location(
                frame
            ),

            "text_sha256":
                sha256_text(
                    text
                )
                if text
                else "",

            "word_count":
                word_count,

            "character_count":
                len(text),

            "text_included":
                False,
        }

        if (
            tag
            in self.SEMANTIC_BLOCK_TAGS
            and text
        ):
            self.semantic_blocks.append(
                base
            )

        if (
            tag
            in self.HEADING_TAGS
            and text
        ):
            self.headings.append(
                base
            )

        if (
            tag
            in self.CONTAINER_TAGS
            and text
            and frame[
                "semantic_descendants"
            ]
            == 0
            and frame[
                "heading_descendants"
            ]
            == 0
            and frame[
                "container_descendants"
            ]
            == 0
        ):
            self.leaf_containers.append(
                base
            )

    def handle_starttag(
        self,
        tag: str,
        attrs: list[
            tuple[str, str | None]
        ],
    ) -> None:
        tag = str(
            tag or ""
        ).lower()

        if self.skip_depth:
            if tag in self.SKIP_TAGS:
                self.skip_depth += 1

            return

        if tag in self.SKIP_TAGS:
            self.skip_depth = 1
            return

        self.tag_counts[
            tag
        ] += 1

        if self.stack:
            parent = self.stack[
                -1
            ]

            parent[
                "child_counts"
            ][tag] += 1

            position = parent[
                "child_counts"
            ][tag]

            path = (
                parent[
                    "path"
                ]
                + f"/{tag}[{position}]"
            )

        else:
            self.root_counts[
                tag
            ] += 1

            position = self.root_counts[
                tag
            ]

            path = f"/{tag}[{position}]"

        if tag in self.VOID_TAGS:
            return

        self.stack.append(
            {
                "tag":
                    tag,

                "path":
                    path,

                "attrs":
                    {
                        str(key).lower():
                            value
                        for key, value
                        in attrs
                    },

                "text_parts":
                    [],

                "child_counts":
                    Counter(),

                "semantic_descendants":
                    0,

                "heading_descendants":
                    0,

                "container_descendants":
                    0,
            }
        )

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[
            tuple[str, str | None]
        ],
    ) -> None:
        self.handle_starttag(
            tag,
            attrs,
        )

        if (
            str(
                tag or ""
            ).lower()
            not in self.VOID_TAGS
        ):
            self.handle_endtag(
                tag
            )

    def handle_endtag(
        self,
        tag: str,
    ) -> None:
        tag = str(
            tag or ""
        ).lower()

        if self.skip_depth:
            if tag in self.SKIP_TAGS:
                self.skip_depth -= 1

            return

        matching_index = None

        for index in range(
            len(self.stack) - 1,
            -1,
            -1,
        ):
            if (
                self.stack[
                    index
                ][
                    "tag"
                ]
                == tag
            ):
                matching_index = index
                break

        if matching_index is None:
            return

        while (
            len(self.stack)
            > matching_index
        ):
            frame = self.stack.pop()

            self._finalize(
                frame
            )

            semantic_increment = (
                frame[
                    "semantic_descendants"
                ]
                + (
                    1
                    if frame[
                        "tag"
                    ]
                    in self.SEMANTIC_BLOCK_TAGS
                    else 0
                )
            )

            heading_increment = (
                frame[
                    "heading_descendants"
                ]
                + (
                    1
                    if frame[
                        "tag"
                    ]
                    in self.HEADING_TAGS
                    else 0
                )
            )

            container_increment = (
                frame[
                    "container_descendants"
                ]
                + (
                    1
                    if frame[
                        "tag"
                    ]
                    in self.CONTAINER_TAGS
                    else 0
                )
            )

            if self.stack:
                parent = self.stack[
                    -1
                ]

                parent[
                    "semantic_descendants"
                ] += semantic_increment

                parent[
                    "heading_descendants"
                ] += heading_increment

                parent[
                    "container_descendants"
                ] += container_increment

    def handle_data(
        self,
        data: str,
    ) -> None:
        if (
            self.skip_depth
            or not self.stack
        ):
            return

        for frame in self.stack:
            frame[
                "text_parts"
            ].append(
                data
            )

    def close(
        self,
    ) -> None:
        super().close()

        while self.stack:
            frame = self.stack.pop()

            self._finalize(
                frame
            )


def repeated_groups(
    blocks: list[
        dict[str, Any]
    ],
) -> list[dict[str, Any]]:
    grouped: dict[
        str,
        list[dict[str, Any]],
    ] = defaultdict(list)

    for block in blocks:
        block_hash = str(
            block.get(
                "text_sha256"
            )
            or ""
        )

        if (
            block_hash
            and int(
                block.get(
                    "character_count"
                )
                or 0
            )
            >= 20
        ):
            grouped[
                block_hash
            ].append(
                block
            )

    output: list[
        dict[str, Any]
    ] = []

    for block_hash, occurrences in (
        grouped.items()
    ):
        if len(
            occurrences
        ) < 2:
            continue

        output.append(
            {
                "paragraph_sha256":
                    block_hash,

                "occurrence_count":
                    len(
                        occurrences
                    ),

                "word_count":
                    occurrences[
                        0
                    ][
                        "word_count"
                    ],

                "character_count":
                    occurrences[
                        0
                    ][
                        "character_count"
                    ],

                "locations":
                    [
                        {
                            "tag":
                                item[
                                    "tag"
                                ],

                            "path":
                                item[
                                    "path"
                                ],

                            "id":
                                item[
                                    "id"
                                ],

                            "class":
                                item[
                                    "class"
                                ],
                        }
                        for item
                        in occurrences
                    ],

                "text_included":
                    False,
            }
        )

    output.sort(
        key=lambda item: (
            -int(
                item[
                    "occurrence_count"
                ]
            ),
            -int(
                item[
                    "character_count"
                ]
            ),
            str(
                item[
                    "paragraph_sha256"
                ]
            ),
        )
    )

    return output


def main() -> int:
    print()
    print("=" * 100)
    print(
        "ARTICLE VALIDATION — THREE-FAILURE STRUCTURAL PROVENANCE SCAN"
    )
    print("=" * 100)

    population_report = load_json(
        POPULATION_REPORT_PATH
    )

    artifact_paths = population_report.get(
        "artifact_paths"
    )

    if not isinstance(
        artifact_paths,
        dict,
    ):
        raise RuntimeError(
            "Population report has no artifact paths."
        )

    failure_manifest_path = Path(
        str(
            artifact_paths.get(
                "failure_manifest"
            )
            or ""
        )
    )

    failures = load_jsonl(
        failure_manifest_path
    )

    if len(
        failures
    ) != 3:
        raise RuntimeError(
            "Expected exactly three failures, found "
            + str(
                len(
                    failures
                )
            )
        )

    report_records: list[
        dict[str, Any]
    ] = []

    for failure in failures:
        article_path = resolve_reference(
            failure.get(
                "article_reference"
            )
        )

        expected_hash = str(
            failure.get(
                "article_sha256"
            )
            or ""
        ).lower()

        actual_hash = sha256_file(
            article_path
        )

        parser = StructuralHTMLParser()

        parser.feed(
            article_path.read_text(
                encoding="utf-8-sig",
                errors="strict",
            )
        )

        parser.close()

        repeated = repeated_groups(
            parser.semantic_blocks
        )

        orphan_containers = [
            container
            for container
            in parser.leaf_containers
            if int(
                container.get(
                    "word_count"
                )
                or 0
            )
            >= 5
        ]

        reasons = list(
            failure.get(
                "rejection_reasons"
            )
            or []
        )

        if (
            "INVALID_PARAGRAPH_STRUCTURE"
            in reasons
        ):
            structural_interpretation = (
                "POSSIBLE_EXTRACTOR_STRUCTURE_MISS"
                if orphan_containers
                else "SINGLE_SEMANTIC_PARAGRAPH_CONFIRMED"
            )

        elif (
            "HIGH_DUPLICATE_PARAGRAPH_RATIO"
            in reasons
        ):
            structural_interpretation = (
                "EXACT_REPEATED_SEMANTIC_BLOCKS_PRESENT"
                if repeated
                else "ENGINE_DUPLICATION_RESULT_NOT_REPRODUCED"
            )

        else:
            structural_interpretation = (
                "UNCLASSIFIED"
            )

        record = {
            "source_record_id":
                failure.get(
                    "source_record_id"
                ),

            "title":
                failure.get(
                    "title"
                ),

            "article_reference":
                failure.get(
                    "article_reference"
                ),

            "article_sha256_verified":
                expected_hash
                == actual_hash,

            "rejection_reasons":
                reasons,

            "engine_statistics":
                failure.get(
                    "statistics"
                ),

            "tag_counts":
                dict(
                    sorted(
                        parser.tag_counts.items()
                    )
                ),

            "semantic_block_count":
                len(
                    parser.semantic_blocks
                ),

            "semantic_block_tag_counts":
                dict(
                    Counter(
                        block[
                            "tag"
                        ]
                        for block
                        in parser.semantic_blocks
                    )
                ),

            "heading_count":
                len(
                    parser.headings
                ),

            "leaf_text_container_count":
                len(
                    orphan_containers
                ),

            "leaf_text_containers":
                orphan_containers,

            "exact_repeated_group_count":
                len(
                    repeated
                ),

            "exact_repeated_occurrence_count":
                sum(
                    int(
                        group[
                            "occurrence_count"
                        ]
                    )
                    - 1
                    for group
                    in repeated
                ),

            "repeated_groups":
                repeated,

            "structural_interpretation":
                structural_interpretation,

            "article_body_included":
                False,

            "article_body_modified":
                False,
        }

        report_records.append(
            record
        )

    report = {
        "schema_version":
            "article_validation_three_failure_structure_v3",

        "workspace_id":
            WORKSPACE_ID,

        "run_id":
            population_report.get(
                "run_id"
            ),

        "failure_count":
            len(
                report_records
            ),

        "records":
            report_records,

        "article_bodies_included":
            False,

        "source_articles_modified":
            False,

        "integrity_artifacts_modified":
            False,

        "validation_evidence_modified":
            False,
    }

    write_json(
        OUTPUT_REPORT_PATH,
        report,
    )

    print()

    for record in report_records:
        print(
            "Source record ID: "
            + str(
                record[
                    "source_record_id"
                ]
            )
        )

        print(
            "Title: "
            + str(
                record[
                    "title"
                ]
            )
        )

        print(
            "SHA-256 verified: "
            + str(
                record[
                    "article_sha256_verified"
                ]
            )
        )

        print(
            "Semantic blocks: "
            + str(
                record[
                    "semantic_block_count"
                ]
            )
        )

        print(
            "Semantic block tags: "
            + json.dumps(
                record[
                    "semantic_block_tag_counts"
                ],
                sort_keys=True,
            )
        )

        print(
            "Leaf text containers: "
            + str(
                record[
                    "leaf_text_container_count"
                ]
            )
        )

        print(
            "Repeated exact groups: "
            + str(
                record[
                    "exact_repeated_group_count"
                ]
            )
        )

        print(
            "Repeated extra occurrences: "
            + str(
                record[
                    "exact_repeated_occurrence_count"
                ]
            )
        )

        print(
            "Interpretation: "
            + str(
                record[
                    "structural_interpretation"
                ]
            )
        )

        print("-" * 100)

    print()
    print(
        "Structural report: "
        + str(
            OUTPUT_REPORT_PATH
        )
    )

    print()
    print(
        "ARTICLE VALIDATION THREE-FAILURE "
        "STRUCTURAL PROVENANCE SCAN: PASS"
    )

    print(
        "No article text was printed or stored."
    )

    print("=" * 100)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
