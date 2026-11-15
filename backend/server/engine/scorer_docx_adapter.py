"""Restricted DOCX structural adapter for LinkCraftor Original Scorer.

Reads WordprocessingML and explicit hyperlink relationships.
Unsupported structures fail closed. No linking is authorized.
"""

from __future__ import annotations

import hashlib
from io import BytesIO
import re
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET
from zipfile import ZipFile, BadZipFile

from backend.server.engine.scorer_document_contract import (
    SCORER_DOCUMENT_CONTRACT_VERSION,
    validate_scorer_document_contract,
)


class ScorerDocxAdapterError(ValueError):
    pass


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"

FAQ_TITLES = {"faq", "faqs", "frequently asked questions"}
REFERENCE_TITLES = {
    "references", "bibliography", "works cited",
    "sources", "further reading",
}


def _read_relationships(archive):
    name = "word/_rels/document.xml.rels"
    if name not in archive.namelist():
        return {}

    root = ET.fromstring(archive.read(name))
    relationships = {}

    for item in root:
        if item.tag != REL + "Relationship":
            raise ScorerDocxAdapterError(
                "unsupported relationship element"
            )

        if not item.attrib.get("Type", "").endswith("/hyperlink"):
            continue

        rid = item.attrib.get("Id")
        destination = item.attrib.get("Target", "")
        mode = item.attrib.get("TargetMode")

        if not rid or not destination or mode != "External":
            raise ScorerDocxAdapterError(
                "unsupported hyperlink relationship"
            )

        parsed = urlsplit(destination)

        if (
            parsed.scheme.lower() not in {"http", "https"}
            or not parsed.netloc
            or any(ord(c) < 33 or ord(c) == 127 for c in destination)
        ):
            raise ScorerDocxAdapterError(
                "invalid hyperlink relationship destination"
            )

        if rid in relationships:
            raise ScorerDocxAdapterError(
                "duplicate hyperlink relationship ID"
            )

        relationships[rid] = destination

    return relationships


def _paragraph_content(node, relationships):
    parts = []
    links = []
    position = 0
    style_id = ""

    def read_run(run):
        value = []

        for child in run:
            if child.tag == W + "rPr":
                continue
            if child.tag == W + "t":
                value.append(child.text or "")
            else:
                raise ScorerDocxAdapterError(
                    "unsupported DOCX run element"
                )

        return "".join(value)

    for child in node:
        if child.tag == W + "pPr":
            for prop in child:
                if prop.tag == W + "pStyle":
                    style_id = prop.attrib.get(W + "val", "")
                else:
                    raise ScorerDocxAdapterError(
                        "unsupported paragraph property"
                    )

        elif child.tag == W + "r":
            value = read_run(child)
            parts.append(value)
            position += len(value)

        elif child.tag == W + "hyperlink":
            rid = child.attrib.get(R + "id")
            if rid not in relationships:
                raise ScorerDocxAdapterError(
                    "unresolved DOCX hyperlink"
                )

            start = position
            value = []

            for run in child:
                if run.tag != W + "r":
                    raise ScorerDocxAdapterError(
                        "unsupported hyperlink content"
                    )
                value.append(read_run(run))

            anchor = "".join(value)

            if not anchor:
                raise ScorerDocxAdapterError(
                    "empty DOCX hyperlink anchor"
                )

            parts.append(anchor)
            position += len(anchor)
            links.append(
                (start, position, relationships[rid])
            )

        else:
            raise ScorerDocxAdapterError(
                "unsupported DOCX paragraph element"
            )

    text = "".join(parts)

    if text and text != " ".join(text.split()):
        raise ScorerDocxAdapterError(
            "unsupported DOCX whitespace"
        )

    return text, style_id, links


def adapt_docx_for_scorer(
    *,
    docx_bytes: bytes,
    workspace_id: str,
    document_id: str,
    content_version: str,
):
    if not isinstance(docx_bytes, bytes) or not docx_bytes:
        raise ScorerDocxAdapterError("DOCX bytes required")

    try:
        with ZipFile(BytesIO(docx_bytes)) as archive:
            xml = archive.read("word/document.xml")
            relationships = _read_relationships(archive)
    except (BadZipFile, KeyError, OSError) as exc:
        raise ScorerDocxAdapterError(
            "invalid or incomplete DOCX archive"
        ) from exc

    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise ScorerDocxAdapterError(
            "invalid Word document XML"
        ) from exc

    body = root.find(W + "body")

    if body is None:
        raise ScorerDocxAdapterError(
            "Word document body missing"
        )

    regions = []
    protected = []
    paragraphs = []
    eligible_words = 0
    heading_seen = False
    current_section = "root"
    current_type = "article_body"
    protected_level = None

    for index, node in enumerate(body):
        if node.tag == W + "sectPr":
            continue

        if node.tag != W + "p":
            raise ScorerDocxAdapterError(
                "unsupported DOCX body structure"
            )

        text, style, links = _paragraph_content(
            node, relationships
        )

        if not text:
            continue

        style_lower = style.casefold()

        if style_lower in {"title", "subtitle"}:
            level = 1
        else:
            match = re.fullmatch(
                r"heading([1-6])", style_lower
            )
            level = int(match.group(1)) if match else None

        if level is not None:
            if links:
                raise ScorerDocxAdapterError(
                    "linked heading unsupported"
                )

            heading_seen = True
            title = text.casefold()

            if title in FAQ_TITLES:
                current_type = "faq"
                protected_level = level
            elif title in REFERENCE_TITLES:
                current_type = "references"
                protected_level = level
            elif (
                protected_level is None
                or level <= protected_level
            ):
                current_type = "editorial_section"
                protected_level = None

            current_section = f"section_{index}"

            regions.append({
                "region_id": f"heading_{index}",
                "region_type": "heading",
                "eligible_for_linking": False,
                "source_paragraph_index": index,
            })
            continue

        if not heading_seen:
            raise ScorerDocxAdapterError(
                "DOCX requires a styled heading before prose"
            )

        if style_lower not in {"", "normal", "bodytext", "body text"}:
            raise ScorerDocxAdapterError(
                "unverified DOCX paragraph style"
            )

        offset = sum(len(p) + 2 for p in paragraphs)
        node_id = f"word_body_paragraph_{index}"
        eligible = current_type not in {
            "faq", "references",
        }

        if eligible:
            eligible_words += len(text.split())

        lineage = [{
            "section_id": "root",
            "section_type": "article_body",
        }]

        if current_section != "root":
            lineage.append({
                "section_id": current_section,
                "section_type": current_type,
            })

        regions.append({
            "region_id": f"paragraph_{index}",
            "region_type": "body_paragraph",
            "eligible_for_linking": eligible,
            "source_mapping_verified": True,
            "source_node_id": node_id,
            "source_paragraph_index": index,
            "section_id": current_section,
            "section_lineage": lineage,
            "char_start": offset,
            "char_end": offset + len(text),
            "text": text,
            "word_count": len(text.split()),
        })

        for link_index, (start, end, destination) in enumerate(links):
            protected.append({
                "span_id": f"docx_link_{index}_{link_index}",
                "kind": "hyperlink",
                "char_start": offset + start,
                "char_end": offset + end,
                "text": text[start:end],
                "source_node_id": node_id,
                "destination": destination,
            })

        paragraphs.append(text)

    if not heading_seen:
        raise ScorerDocxAdapterError(
            "styled DOCX heading required"
        )

    canonical_text = "\n\n".join(paragraphs)

    document = {
        "schema_version": SCORER_DOCUMENT_CONTRACT_VERSION,
        "workspace_id": workspace_id,
        "document_id": document_id,
        "content_version": content_version,
        "source_format": "docx",
        "canonical_text": canonical_text,
        "content_sha256": hashlib.sha256(
            canonical_text.encode("utf-8")
        ).hexdigest(),
        "source_docx_sha256": hashlib.sha256(
            docx_bytes
        ).hexdigest(),
        "structure_complete": True,
        "regions": regions,
        "eligible_body_word_count": eligible_words,
        "protected_spans_complete": True,
        "protected_spans": protected,
        "source_mapping_scope": "canonical_docx_text_only",
        "original_source_insertion_verified": False,
        "source_adapter": "scorer_docx_adapter_i2_c1",
    }

    return validate_scorer_document_contract(document)
