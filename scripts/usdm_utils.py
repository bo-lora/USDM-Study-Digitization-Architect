#!/usr/bin/env python3
"""
USDM v4.0.0 Shared Utilities

Common helper functions for navigating and extracting data from
USDM v4.0.0 JSON structures. Used by the validator, SDTM generator,
and M11 document generator scripts.
"""

from typing import Any, Optional


def get_version_and_design(data: dict) -> tuple[dict, dict]:
    """Navigate to the first StudyVersion and first StudyDesign.

    In USDM v4.0.0, the path is:
        data["study"]["versions"][0]["studyDesigns"][0]

    Returns:
        (version, design) tuple
    Raises:
        KeyError/IndexError if the expected structure is missing.
    """
    study = data["study"]
    version = study["versions"][0]
    design = version["studyDesigns"][0]
    return version, design


def sort_linked_list(items: list[dict]) -> list[dict]:
    """Sort objects connected by previousId/nextId linked-list pointers.

    Finds the head (previousId is None/null), then follows nextId
    to produce an ordered list. Items not reachable from the head
    are appended at the end.
    """
    if not items:
        return []

    by_id = {item["id"]: item for item in items}
    by_prev = {}
    head = None

    for item in items:
        prev_id = item.get("previousId")
        if prev_id is None:
            head = item
        by_prev[prev_id] = item

    if head is None:
        return items  # fallback: return as-is if no head found

    ordered = []
    current = head
    visited = set()
    while current and current["id"] not in visited:
        ordered.append(current)
        visited.add(current["id"])
        next_id = current.get("nextId")
        current = by_id.get(next_id) if next_id else None

    # Append any unreachable items
    for item in items:
        if item["id"] not in visited:
            ordered.append(item)

    return ordered


def resolve_organization(scope_id: str, organizations: list[dict]) -> Optional[dict]:
    """Find an organization by ID from the version.organizations[] array."""
    for org in organizations:
        if org.get("id") == scope_id:
            return org
    return None


def get_study_title(version: dict, title_type: str = "Official Study Title") -> str:
    """Extract a title from version.titles[] by type decode.

    Common types: "Official Study Title", "Brief Study Title"
    """
    for title in version.get("titles", []):
        type_obj = title.get("type", {})
        if title_type.lower() in type_obj.get("decode", "").lower():
            return title.get("text", "")
    # Fallback: return the first title if available
    titles = version.get("titles", [])
    if titles:
        return titles[0].get("text", "")
    return ""


def get_study_id(version: dict, org_type: str = "Drug Company") -> str:
    """Extract a study identifier by organization type.

    Resolves the scopeId to find the matching organization, then
    returns the identifier text.

    Args:
        version: The StudyVersion object
        org_type: Organization type decode to match (e.g., "Drug Company",
                  "Study Registry", "Regulatory Agency")
    """
    organizations = version.get("organizations", [])
    for sid in version.get("studyIdentifiers", []):
        scope_id = sid.get("scopeId", "")
        org = resolve_organization(scope_id, organizations)
        if org:
            org_type_decode = org.get("type", {}).get("decode", "")
            if org_type.lower() in org_type_decode.lower():
                return sid.get("text", "")
    # Fallback: return first identifier
    identifiers = version.get("studyIdentifiers", [])
    if identifiers:
        return identifiers[0].get("text", "UNKNOWN")
    return "UNKNOWN"


def get_sponsor_info(version: dict) -> dict:
    """Extract sponsor name and protocol number from version data.

    Searches organizations for Drug Company or Sponsor types.
    """
    organizations = version.get("organizations", [])
    for sid in version.get("studyIdentifiers", []):
        scope_id = sid.get("scopeId", "")
        org = resolve_organization(scope_id, organizations)
        if org:
            org_type_decode = org.get("type", {}).get("decode", "").lower()
            if "drug company" in org_type_decode or "sponsor" in org_type_decode:
                return {
                    "name": org.get("name", "") or org.get("label", "TBD"),
                    "protocol_number": sid.get("text", "TBD"),
                }
    return {"name": "TBD", "protocol_number": "TBD"}


def get_registry_id(version: dict) -> str:
    """Extract registry identifier (e.g., NCT number)."""
    organizations = version.get("organizations", [])
    for sid in version.get("studyIdentifiers", []):
        scope_id = sid.get("scopeId", "")
        org = resolve_organization(scope_id, organizations)
        if org:
            org_type_decode = org.get("type", {}).get("decode", "").lower()
            if "registry" in org_type_decode:
                return sid.get("text", "")
    return ""


def get_criterion_text(
    criterion: dict,
    criterion_items: list[dict],
) -> str:
    """Resolve eligibility criterion text via criterionItemId.

    In USDM v4.0.0, EligibilityCriterion has a criterionItemId that
    points to an EligibilityCriterionItem in version.eligibilityCriterionItems[].
    The actual text (possibly with <usdm:tag> templates) is on the item.

    Falls back to criterion's own description if no item found.
    """
    item_id = criterion.get("criterionItemId")
    if item_id:
        for item in criterion_items:
            if item.get("id") == item_id:
                text = item.get("text", "")
                if text:
                    # Strip HTML tags for plain-text usage
                    import re
                    text = re.sub(r"<usdm:tag[^/]*/?>", "[...]", text)
                    text = re.sub(r"<[^>]+>", "", text)
                    return text.strip()
    # Fallback to criterion's own fields
    return (
        criterion.get("description", "")
        or criterion.get("label", "")
        or criterion.get("name", "")
    )


def get_enrollment_number(design: dict) -> str:
    """Extract planned enrollment from design.population (singular)."""
    pop = design.get("population")
    if not pop:
        return "TBD"
    enroll = pop.get("plannedEnrollmentNumber", {})
    max_val = enroll.get("maxValue")
    if isinstance(max_val, dict):
        # v4.0.0 uses Quantity objects
        return str(int(max_val.get("value", 0)))
    elif max_val is not None:
        return str(max_val)
    min_val = enroll.get("minValue")
    if isinstance(min_val, dict):
        return str(int(min_val.get("value", 0)))
    elif min_val is not None:
        return str(min_val)
    return "TBD"
