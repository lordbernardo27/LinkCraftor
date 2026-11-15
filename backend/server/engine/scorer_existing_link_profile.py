"""Phase 4 I3 - Existing Link Profile foundation.

Builds an evidence-preserving hyperlink inventory from a validated
Scorer Document Contract. Does not infer route relationships,
authorize linking, or perform scoring.
"""

from __future__ import annotations

from copy import deepcopy

from backend.server.engine.scorer_document_contract import (
    validate_scorer_document_contract,
)


PROFILE_VERSION = "linkcraftor_existing_links_v1"

ROUTES = frozenset({
    "INTERNAL", "SEMANTIC", "EXTERNAL", "UNKNOWN"
})


class ExistingLinkProfileError(ValueError):
    pass


def build_existing_link_profile(document):
    validated = validate_scorer_document_contract(document)

    if validated.get("protected_spans_complete") is not True:
        raise ExistingLinkProfileError(
            "complete protected-span inventory required"
        )

    regions = validated["regions"]
    anchors = [
        span for span in validated["protected_spans"]
        if span["kind"].lower() == "hyperlink"
    ]

    records = []
    budget_count = 0

    for anchor in anchors:
        start = anchor["char_start"]
        end = anchor["char_end"]

        containing = [
            region for region in regions
            if (
                type(region.get("char_start")) is int
                and type(region.get("char_end")) is int
                and region["char_start"] <= start
                and end <= region["char_end"]
            )
        ]

        if len(containing) > 1:
            raise ExistingLinkProfileError(
                "ambiguous anchor-to-region mapping"
            )

        if containing:
            region = containing[0]

            if anchor["source_node_id"] != region.get(
                "source_node_id"
            ):
                raise ExistingLinkProfileError(
                    "anchor source-node mismatch"
                )

            eligible_body = (
                region.get("region_type") == "body_paragraph"
                and region.get("eligible_for_linking") is True
            )
            region_id = region["region_id"]
        else:
            # This first profile cannot prove placement context
            # when a protected anchor is outside mapped regions.
            eligible_body = False
            region_id = None

        if eligible_body:
            budget_count += 1

        records.append({
            "link_id": anchor["span_id"],
            "anchor_text": anchor["text"],
            "destination": anchor["destination"],
            "source_node_id": anchor["source_node_id"],
            "region_id": region_id,
            "char_start": start,
            "char_end": end,
            "protected": True,
            "eligible_body": eligible_body,
            "counts_toward_budget": eligible_body,
            "destination_ownership": "UNKNOWN",
            "relationship_route": "UNKNOWN",
            "relationship_verified": False,
            "relationship_evidence": None,
        })

    total = len(records)

    if budget_count > total:
        raise ExistingLinkProfileError(
            "inconsistent link counts"
        )

    return {
        "profile_version": PROFILE_VERSION,
        "workspace_id": validated["workspace_id"],
        "document_id": validated["document_id"],
        "content_version": validated["content_version"],
        "content_sha256": validated["content_sha256"],
        "source_format": validated["source_format"],
        "inventory_complete_asserted": True,
        "inventory_source": validated.get("source_adapter"),
        "total_existing_links": total,
        "eligible_body_existing_links": budget_count,
        "other_existing_links": total - budget_count,
        "route_counts": {
            "INTERNAL": 0,
            "SEMANTIC": 0,
            "EXTERNAL": 0,
            "UNKNOWN": total,
        },
        "links": deepcopy(records),
        "relationship_classification_complete": False,
        "automatic_linking_authorized": False,
    }


def attach_owned_target_evidence(profile, registry):
    """Attach exact-match ownership evidence without assigning routes.

    Registry provenance is structurally checked here. Independent
    authentication of the registry is a later integration gate.
    """
    if not isinstance(profile, dict) or not isinstance(registry, dict):
        raise ExistingLinkProfileError("profile and registry required")

    if profile.get("profile_version") != PROFILE_VERSION:
        raise ExistingLinkProfileError("unsupported profile version")

    if registry.get("workspace_id") != profile.get("workspace_id"):
        raise ExistingLinkProfileError("workspace mismatch")

    registry_id = registry.get("registry_id")
    registry_version = registry.get("registry_version")

    if (
        not isinstance(registry_id, str) or not registry_id.strip()
        or not isinstance(registry_version, str)
        or not registry_version.strip()
        or registry.get("inventory_complete") is not True
    ):
        raise ExistingLinkProfileError(
            "complete identified target registry required"
        )

    targets = registry.get("owned_targets")

    if not isinstance(targets, list):
        raise ExistingLinkProfileError(
            "owned_targets must be a list"
        )

    exact_targets = {}

    for target in targets:
        if not isinstance(target, dict):
            raise ExistingLinkProfileError("invalid owned target")

        url = target.get("url")
        target_id = target.get("target_id")
        evidence_ref = target.get("evidence_ref")

        if (
            not isinstance(url, str) or not url.strip()
            or not isinstance(target_id, str) or not target_id.strip()
            or not isinstance(evidence_ref, str)
            or not evidence_ref.strip()
            or target.get("ownership_verified") is not True
        ):
            raise ExistingLinkProfileError(
                "unverified or incomplete owned target"
            )

        if url in exact_targets:
            raise ExistingLinkProfileError(
                "duplicate owned target destination"
            )

        exact_targets[url] = target

    result = deepcopy(profile)

    if not isinstance(result.get("links"), list):
        raise ExistingLinkProfileError("invalid existing link records")

    owned_count = 0

    for link in result["links"]:
        if not isinstance(link, dict):
            raise ExistingLinkProfileError("invalid link record")

        destination = link.get("destination")

        if not isinstance(destination, str):
            raise ExistingLinkProfileError("invalid link destination")

        target = exact_targets.get(destination)

        if target is None:
            link["destination_ownership"] = "UNKNOWN"
            link["ownership_evidence"] = None
        else:
            link["destination_ownership"] = "OWNED"
            link["ownership_evidence"] = {
                "registry_id": registry_id,
                "registry_version": registry_version,
                "target_id": target["target_id"],
                "evidence_ref": target["evidence_ref"],
                "match_type": "EXACT_DESTINATION",
            }
            owned_count += 1

        # Ownership must not relabel a link's relationship route.
        if link.get("relationship_route") != "UNKNOWN":
            raise ExistingLinkProfileError(
                "unexpected preclassified relationship"
            )

    result["owned_destination_count"] = owned_count
    result["unknown_ownership_count"] = (
        len(result["links"]) - owned_count
    )
    result["ownership_registry_id"] = registry_id
    result["ownership_registry_version"] = registry_version
    result["ownership_registry_trust"] = (
        "STRUCTURAL_ATTESTATION_ONLY"
    )
    result["relationship_classification_complete"] = False
    result["automatic_linking_authorized"] = False

    return result


def attach_relationship_evidence(profile, evidence_bundle):
    """Match historical relationship evidence without trusting claims.

    This stage records structurally matched route candidates.
    Relationship routes remain UNKNOWN until independent evidence
    authentication is implemented at the integration boundary.
    """
    if not isinstance(profile, dict) or not isinstance(evidence_bundle, dict):
        raise ExistingLinkProfileError(
            "profile and evidence bundle must be mappings"
        )

    if profile.get("profile_version") != PROFILE_VERSION:
        raise ExistingLinkProfileError("unsupported profile version")

    for field in (
        "workspace_id", "document_id",
        "content_version", "content_sha256",
    ):
        if evidence_bundle.get(field) != profile.get(field):
            raise ExistingLinkProfileError(
                "relationship evidence identity mismatch: " + field
            )

    bundle_id = evidence_bundle.get("bundle_id")
    if not isinstance(bundle_id, str) or not bundle_id.strip():
        raise ExistingLinkProfileError(
            "relationship evidence bundle ID required"
        )

    decisions = evidence_bundle.get("decisions")
    if not isinstance(decisions, list):
        raise ExistingLinkProfileError(
            "relationship decisions must be a list"
        )

    result = deepcopy(profile)
    links = result.get("links")
    if not isinstance(links, list):
        raise ExistingLinkProfileError(
            "invalid existing-link inventory"
        )

    by_id = {}
    for link in links:
        if not isinstance(link, dict):
            raise ExistingLinkProfileError("invalid link")
        link_id = link.get("link_id")
        if not isinstance(link_id, str) or link_id in by_id:
            raise ExistingLinkProfileError("invalid or duplicate link ID")
        by_id[link_id] = link
        if link.get("relationship_route") != "UNKNOWN":
            raise ExistingLinkProfileError(
                "cannot overwrite classified relationship"
            )

    matched = set()

    for decision in decisions:
        if not isinstance(decision, dict):
            raise ExistingLinkProfileError(
                "invalid relationship evidence record"
            )

        link_id = decision.get("link_id")
        route = decision.get("route")
        evidence_ref = decision.get("evidence_ref")
        decision_id = decision.get("decision_id")

        if (
            link_id not in by_id
            or link_id in matched
            or route not in {"INTERNAL", "SEMANTIC", "EXTERNAL"}
            or not isinstance(evidence_ref, str)
            or not evidence_ref.strip()
            or not isinstance(decision_id, str)
            or not decision_id.strip()
        ):
            raise ExistingLinkProfileError(
                "invalid, duplicate, or unsupported relationship decision"
            )

        link = by_id[link_id]

        if (
            decision.get("destination") != link.get("destination")
            or decision.get("anchor_text") != link.get("anchor_text")
            or decision.get("char_start") != link.get("char_start")
            or decision.get("char_end") != link.get("char_end")
            or decision.get("source_node_id") != link.get("source_node_id")
        ):
            raise ExistingLinkProfileError(
                "historical decision does not match existing anchor"
            )

        if route in {"INTERNAL", "SEMANTIC"}:
            if (
                link.get("destination_ownership") != "OWNED"
                or not isinstance(link.get("ownership_evidence"), dict)
                or not isinstance(decision.get("relationship_basis"), str)
                or decision["relationship_basis"] not in {
                    "DIRECT_SUBJECT_MATCH",
                    "RELATED_OWNED_SUBJECT",
                }
                or (
                    route == "INTERNAL"
                    and decision["relationship_basis"]
                    != "DIRECT_SUBJECT_MATCH"
                )
                or (
                    route == "SEMANTIC"
                    and decision["relationship_basis"]
                    != "RELATED_OWNED_SUBJECT"
                )
            ):
                raise ExistingLinkProfileError(
                    "owned-target relationship evidence inconsistent"
                )
        else:
            if (
                link.get("destination_ownership") == "OWNED"
                or decision.get("relationship_basis")
                != "CURATED_EXTERNAL_AUTHORITY"
                or not isinstance(decision.get("curated_target_ref"), str)
                or not decision["curated_target_ref"].strip()
            ):
                raise ExistingLinkProfileError(
                    "external authority evidence incomplete"
                )

        # Matching record identity is not authenticating its source.
        link["provisional_relationship_route"] = route
        link["relationship_evidence_candidate"] = {
            "bundle_id": bundle_id,
            "decision_id": decision_id,
            "evidence_ref": evidence_ref,
            "relationship_basis": decision["relationship_basis"],
            "curated_target_ref": decision.get("curated_target_ref"),
            "authentication_status": "NOT_AUTHENTICATED",
        }
        link["relationship_route"] = "UNKNOWN"
        link["relationship_verified"] = False
        matched.add(link_id)

    result["relationship_evidence_matched_count"] = len(matched)
    result["relationship_evidence_trust"] = (
        "STRUCTURALLY_MATCHED_NOT_AUTHENTICATED"
    )
    result["relationship_classification_complete"] = False
    result["automatic_linking_authorized"] = False

    return result


def evaluate_existing_link_capacity(
    profile, document, candidate_occurrences=None
):
    """Read-only capacity and collision precheck, not Scorer selection."""
    validated = validate_scorer_document_contract(document)

    if not isinstance(profile, dict):
        raise ExistingLinkProfileError("profile required")

    if profile.get("profile_version") != PROFILE_VERSION:
        raise ExistingLinkProfileError("invalid profile version")

    for field in (
        "workspace_id", "document_id", "content_version",
        "content_sha256", "source_format",
    ):
        if profile.get(field) != validated.get(field):
            raise ExistingLinkProfileError(
                "stale or mismatched profile: " + field
            )

    baseline = build_existing_link_profile(validated)

    for field in (
        "total_existing_links",
        "eligible_body_existing_links",
        "other_existing_links",
    ):
        if profile.get(field) != baseline[field]:
            raise ExistingLinkProfileError(
                "existing link inventory count mismatch"
            )

    links = profile.get("links")
    if not isinstance(links, list):
        raise ExistingLinkProfileError("invalid profile links")

    baseline_links = {
        link["link_id"]: link for link in baseline["links"]
    }

    if len(links) != len(baseline_links):
        raise ExistingLinkProfileError(
            "existing link inventory changed"
        )

    seen = set()

    for link in links:
        if not isinstance(link, dict):
            raise ExistingLinkProfileError("invalid hyperlink record")

        link_id = link.get("link_id")

        if link_id in seen or link_id not in baseline_links:
            raise ExistingLinkProfileError(
                "duplicate or foreign hyperlink"
            )

        seen.add(link_id)
        original_link = baseline_links[link_id]

        for field in (
            "anchor_text", "destination", "source_node_id",
            "region_id", "char_start", "char_end",
            "counts_toward_budget", "protected",
        ):
            if link.get(field) != original_link[field]:
                raise ExistingLinkProfileError(
                    "existing hyperlink geometry changed"
                )

    words = validated["eligible_body_word_count"]
    gross = min(40, words // 200)
    existing = baseline["eligible_body_existing_links"]
    remaining = max(0, gross - existing)

    eligible = {}
    section_words = {}
    section_existing = {}

    for region in validated["regions"]:
        if region.get("eligible_for_linking") is True:
            eligible[region["region_id"]] = region
            section = region["section_id"]
            section_words[section] = (
                section_words.get(section, 0)
                + region["word_count"]
            )

    for link in baseline["links"]:
        if link["counts_toward_budget"]:
            region = eligible[link["region_id"]]
            section = region["section_id"]
            section_existing[section] = (
                section_existing.get(section, 0) + 1
            )

    sections = {}

    for section, count in section_words.items():
        ceiling = count // 200
        used = section_existing.get(section, 0)

        sections[section] = {
            "eligible_body_words": count,
            "gross_link_ceiling": ceiling,
            "existing_links": used,
            "remaining_link_capacity": max(0, ceiling - used),
        }

    occurrences = (
        [] if candidate_occurrences is None
        else candidate_occurrences
    )

    if not isinstance(occurrences, list):
        raise ExistingLinkProfileError(
            "candidate_occurrences must be a list"
        )

    canonical = validated["canonical_text"]
    blocked = [
        (span["char_start"], span["char_end"])
        for span in validated["protected_spans"]
    ]
    seen_candidates = set()
    cleared_ranges = []
    checks = []

    for item in occurrences:
        if not isinstance(item, dict):
            raise ExistingLinkProfileError(
                "invalid candidate occurrence"
            )

        candidate_id = item.get("candidate_id")
        region_id = item.get("region_id")
        start = item.get("char_start")
        end = item.get("char_end")
        phrase = item.get("text")

        if (
            not isinstance(candidate_id, str)
            or not candidate_id.strip()
            or candidate_id in seen_candidates
        ):
            raise ExistingLinkProfileError(
                "duplicate or invalid candidate ID"
            )

        seen_candidates.add(candidate_id)

        if (
            type(start) is not int
            or type(end) is not int
            or not 0 <= start < end <= len(canonical)
            or not isinstance(phrase, str)
            or canonical[start:end] != phrase
        ):
            raise ExistingLinkProfileError(
                "candidate text or offsets invalid"
            )

        region = eligible.get(region_id)

        if region is None:
            status = "INELIGIBLE_REGION"
        elif not (
            region["char_start"] <= start
            and end <= region["char_end"]
        ):
            status = "OUTSIDE_ELIGIBLE_PARAGRAPH"
        elif any(
            start < right and left < end
            for left, right in blocked
        ):
            status = "PROTECTED_SPAN_COLLISION"
        elif any(
            start < right and left < end
            for left, right in cleared_ranges
        ):
            status = "CANDIDATE_COLLISION"
        elif remaining == 0:
            status = "NO_ARTICLE_CAPACITY"
        elif sections[region["section_id"]][
            "remaining_link_capacity"
        ] == 0:
            status = "NO_SECTION_CAPACITY"
        else:
            status = "ELIGIBLE_FOR_SCORER_REVIEW"
            cleared_ranges.append((start, end))

        checks.append({
            "candidate_id": candidate_id,
            "region_id": region_id,
            "char_start": start,
            "char_end": end,
            "status": status,
            "placement_precheck_passed": (
                status == "ELIGIBLE_FOR_SCORER_REVIEW"
            ),
        })

    return {
        "workspace_id": validated["workspace_id"],
        "document_id": validated["document_id"],
        "content_sha256": validated["content_sha256"],
        "eligible_body_word_count": words,
        "gross_article_link_ceiling": gross,
        "existing_eligible_body_links": existing,
        "remaining_article_link_capacity": remaining,
        "sections": sections,
        "candidate_prechecks": checks,
        "minimum_new_links_required": 0,
        "scorer_selection_performed": False,
        "original_source_insertion_verified": False,
        "automatic_linking_authorized": False,
    }
