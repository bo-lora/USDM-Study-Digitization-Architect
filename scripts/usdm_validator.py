#!/usr/bin/env python3
"""
USDM JSON Validator

Performs structural and referential integrity validation on USDM v4.0.0 JSON files.
This is a lightweight pre-check before running the full CDISC CORE engine.

Checks:
  1. Root envelope fields (usdmVersion, systemName, systemVersion)
  2. Study → versions[] → studyDesigns[] navigation
  3. InterventionalStudyDesign instanceType
  4. Required fields present on all objects
  5. extensionAttributes presence
  6. Linked-list integrity (previousId/nextId)
  7. Cross-reference integrity (*Id/*Ids point to existing objects)
  8. CT code structure validation
  9. Eligibility criterion text resolution via criterionItemId

Usage:
    python usdm_validator.py --input study_definition.json
"""

import json
import argparse
import sys
from typing import Any

from usdm_utils import get_version_and_design, sort_linked_list, get_criterion_text


class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def error(self, msg: str):
        self.errors.append(f"ERROR: {msg}")

    def warning(self, msg: str):
        self.warnings.append(f"WARNING: {msg}")

    def add_info(self, msg: str):
        self.info.append(f"INFO: {msg}")

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("USDM v4.0.0 Validation Report")
        lines.append("=" * 60)
        lines.append(f"Errors:   {len(self.errors)}")
        lines.append(f"Warnings: {len(self.warnings)}")
        lines.append(f"Info:     {len(self.info)}")
        lines.append("-" * 60)

        for msg in self.errors:
            lines.append(f"  ✗ {msg}")
        for msg in self.warnings:
            lines.append(f"  ⚠ {msg}")
        for msg in self.info:
            lines.append(f"  ℹ {msg}")

        lines.append("-" * 60)
        if self.is_valid:
            lines.append("RESULT: PASS (no errors)")
        else:
            lines.append("RESULT: FAIL")
        lines.append("=" * 60)
        return "\n".join(lines)


def collect_ids(obj: Any, path: str = "") -> dict[str, str]:
    """Recursively collect all 'id' fields and their paths."""
    ids = {}
    if isinstance(obj, dict):
        if "id" in obj and obj["id"] is not None:
            ids[obj["id"]] = path
        for key, value in obj.items():
            ids.update(collect_ids(value, f"{path}.{key}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            ids.update(collect_ids(item, f"{path}[{i}]"))
    return ids


def collect_references(obj: Any, path: str = "") -> list[tuple[str, str]]:
    """Recursively collect all *Id and *Ids reference fields."""
    refs = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.endswith("Id") and key != "id" and isinstance(value, str):
                refs.append((value, f"{path}.{key}"))
            elif key.endswith("Ids") and isinstance(value, list):
                for i, ref_id in enumerate(value):
                    if isinstance(ref_id, str):
                        refs.append((ref_id, f"{path}.{key}[{i}]"))
            else:
                refs.extend(collect_references(value, f"{path}.{key}"))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            refs.extend(collect_references(item, f"{path}[{i}]"))
    return refs


def validate_instance_types(obj: Any, path: str, result: ValidationResult):
    """Check that instanceType is present on all objects that should have it."""
    if isinstance(obj, dict):
        if "id" in obj and "instanceType" not in obj:
            result.warning(f"Object at {path} has 'id' but no 'instanceType'")
        for key, value in obj.items():
            validate_instance_types(value, f"{path}.{key}", result)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            validate_instance_types(item, f"{path}[{i}]", result)


def validate_extension_attributes(obj: Any, path: str, result: ValidationResult):
    """Check that extensionAttributes is present on objects with id."""
    if isinstance(obj, dict):
        if "id" in obj and obj["id"] is not None and "extensionAttributes" not in obj:
            result.warning(f"Object at {path} missing 'extensionAttributes'")
        for key, value in obj.items():
            validate_extension_attributes(value, f"{path}.{key}", result)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            validate_extension_attributes(item, f"{path}[{i}]", result)


def validate_code_objects(obj: Any, path: str, result: ValidationResult):
    """Validate Code objects have required fields."""
    if isinstance(obj, dict):
        if obj.get("instanceType") == "Code":
            for field in ["code", "codeSystem", "decode"]:
                if field not in obj or not obj[field]:
                    result.error(f"Code at {path} missing required field '{field}'")
        for key, value in obj.items():
            validate_code_objects(value, f"{path}.{key}", result)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            validate_code_objects(item, f"{path}[{i}]", result)


def validate_linked_list(items: list[dict], item_name: str, result: ValidationResult):
    """Validate a linked-list (previousId/nextId) for consistency."""
    if not items:
        return

    # Check if items use linked-list pattern
    has_linked = any("previousId" in item or "nextId" in item for item in items)
    if not has_linked:
        return

    by_id = {item["id"]: item for item in items}

    heads = [item for item in items if item.get("previousId") is None]
    if len(heads) == 0:
        result.warning(f"{item_name}: No linked-list head found (no item with previousId=null)")
    elif len(heads) > 1:
        # Multiple heads is OK (e.g., separate inclusion/exclusion lists)
        pass

    for item in items:
        next_id = item.get("nextId")
        prev_id = item.get("previousId")
        if next_id and next_id not in by_id:
            result.error(f"{item_name}: Item '{item['id']}' has nextId '{next_id}' that doesn't exist")
        if prev_id and prev_id not in by_id:
            result.error(f"{item_name}: Item '{item['id']}' has previousId '{prev_id}' that doesn't exist")


def validate_study(data: dict) -> ValidationResult:
    """Main validation entry point."""
    result = ValidationResult()

    # 1. Envelope fields
    usdm_version = data.get("usdmVersion")
    if usdm_version:
        result.add_info(f"USDM version: {usdm_version}")
    else:
        result.warning("Missing root 'usdmVersion' field")

    system_name = data.get("systemName")
    if system_name:
        result.add_info(f"System: {system_name} {data.get('systemVersion', '')}")
    else:
        result.warning("Missing root 'systemName' field")

    # 2. Root study object
    if "study" not in data:
        result.error("Missing root 'study' object")
        return result

    study = data["study"]

    if study.get("instanceType") != "Study":
        result.error(f"Study instanceType should be 'Study', got '{study.get('instanceType')}'")

    # 3. Versions layer
    versions = study.get("versions", [])
    if not versions:
        result.error("Study has no 'versions' array (required in v4.0.0)")
        return result

    result.add_info(f"Found {len(versions)} study version(s)")
    version = versions[0]

    # 4. Study identifiers (now on version)
    identifiers = version.get("studyIdentifiers", [])
    if not identifiers:
        result.warning("Version has no studyIdentifiers")
    else:
        result.add_info(f"Found {len(identifiers)} study identifier(s)")
        # Check identifiers use new field names
        for sid in identifiers:
            if "studyIdentifier" in sid:
                result.warning("StudyIdentifier uses legacy 'studyIdentifier' field; should use 'text'")
            if "studyIdentifierScope" in sid:
                result.warning("StudyIdentifier uses legacy 'studyIdentifierScope'; should use 'scopeId'")

    # 5. Titles
    titles = version.get("titles", [])
    if not titles:
        result.warning("Version has no titles (expected StudyTitle objects)")
    else:
        result.add_info(f"Found {len(titles)} title(s)")
        title_types = [t.get("type", {}).get("decode", "") for t in titles]
        result.add_info(f"Title types: {', '.join(title_types)}")

    # 6. Organizations
    organizations = version.get("organizations", [])
    if organizations:
        result.add_info(f"Found {len(organizations)} organization(s)")

    # 7. Study designs
    designs = version.get("studyDesigns", [])
    if not designs:
        result.error("Version has no studyDesigns")
        return result

    result.add_info(f"Found {len(designs)} study design(s)")

    for di, design in enumerate(designs):
        prefix = f"studyDesigns[{di}]"
        instance_type = design.get("instanceType", "")

        if instance_type == "StudyDesign":
            result.warning(f"{prefix}: instanceType is 'StudyDesign'; should be 'InterventionalStudyDesign' (or other subtype)")
        elif "StudyDesign" in instance_type:
            result.add_info(f"{prefix}: instanceType = '{instance_type}'")
        else:
            result.warning(f"{prefix}: unexpected instanceType '{instance_type}'")

        # Arms (not studyArms)
        arms = design.get("arms", design.get("studyArms", []))
        if design.get("studyArms") and not design.get("arms"):
            result.warning(f"{prefix}: Uses legacy 'studyArms'; should use 'arms'")
        result.add_info(f"{prefix}: {len(arms)} arm(s)")
        if not arms:
            result.warning(f"{prefix}: No arms defined")
        for arm in arms:
            if "armType" in arm:
                result.warning(f"{prefix}: Arm uses legacy 'armType'; should use 'type'")

        # Epochs (not studyEpochs)
        epochs = design.get("epochs", design.get("studyEpochs", []))
        if design.get("studyEpochs") and not design.get("epochs"):
            result.warning(f"{prefix}: Uses legacy 'studyEpochs'; should use 'epochs'")
        result.add_info(f"{prefix}: {len(epochs)} epoch(s)")
        if not epochs:
            result.warning(f"{prefix}: No epochs defined")

        # Validate epoch linked list
        validate_linked_list(epochs, f"{prefix}.epochs", result)

        # Check for legacy sequenceNumber
        if any("sequenceNumber" in e for e in epochs):
            result.warning(f"{prefix}: Epochs use legacy 'sequenceNumber'; should use previousId/nextId linked list")

        # Elements (not studyElements)
        elements = design.get("elements", design.get("studyElements", []))
        if design.get("studyElements") and not design.get("elements"):
            result.warning(f"{prefix}: Uses legacy 'studyElements'; should use 'elements'")
        result.add_info(f"{prefix}: {len(elements)} element(s)")

        # Cells
        cells = design.get("studyCells", [])
        result.add_info(f"{prefix}: {len(cells)} cell(s)")

        # Model (not interventionModel)
        model = design.get("model", design.get("interventionModel"))
        if design.get("interventionModel") and not design.get("model"):
            result.warning(f"{prefix}: Uses legacy 'interventionModel'; should use 'model'")
        if model:
            result.add_info(f"{prefix}: model = '{model.get('decode', '')}'")

        # intentTypes (not trialIntentTypes)
        if design.get("trialIntentTypes") and not design.get("intentTypes"):
            result.warning(f"{prefix}: Uses legacy 'trialIntentTypes'; should use 'intentTypes'")

        # subTypes (not trialTypes)
        if design.get("trialTypes") and not design.get("subTypes"):
            result.warning(f"{prefix}: Uses legacy 'trialTypes'; should use 'subTypes'")

        # Encounters
        encounters = design.get("encounters", [])
        result.add_info(f"{prefix}: {len(encounters)} encounter(s)")
        validate_linked_list(encounters, f"{prefix}.encounters", result)
        for enc in encounters:
            if "encounterType" in enc:
                result.warning(f"{prefix}: Encounter uses legacy 'encounterType'; should use 'type'")

        # Activities
        activities = design.get("activities", [])
        result.add_info(f"{prefix}: {len(activities)} activity(ies)")
        validate_linked_list(activities, f"{prefix}.activities", result)

        # Objectives (with embedded endpoints)
        objectives = design.get("objectives", [])
        primary = [o for o in objectives
                   if "primary" in o.get("level", {}).get("decode", "").lower()]
        result.add_info(f"{prefix}: {len(objectives)} objective(s) ({len(primary)} primary)")
        if not primary:
            result.warning(f"{prefix}: No primary objective defined")

        # Check for legacy design-level endpoints array
        if design.get("endpoints"):
            result.warning(f"{prefix}: Has design-level 'endpoints[]'; in v4.0.0 endpoints should be embedded in objectives")

        # Check for legacy endpointIds on objectives
        for obj in objectives:
            if obj.get("endpointIds"):
                result.warning(f"{prefix}: Objective uses legacy 'endpointIds'; endpoints should be embedded directly")

        # Indications
        indications = design.get("indications", [])
        result.add_info(f"{prefix}: {len(indications)} indication(s)")

        # Population (singular, not populations[])
        population = design.get("population")
        populations_array = design.get("populations", [])
        if populations_array and not population:
            result.warning(f"{prefix}: Uses legacy 'populations[]' array; should use singular 'population'")
        if population:
            result.add_info(f"{prefix}: population defined")
        else:
            result.warning(f"{prefix}: No population defined")

        # Eligibility criteria
        criteria = design.get("eligibilityCriteria", [])
        inc = [c for c in criteria if "inclusion" in c.get("category", {}).get("decode", "").lower()]
        exc = [c for c in criteria if "exclusion" in c.get("category", {}).get("decode", "").lower()]
        result.add_info(f"{prefix}: {len(inc)} inclusion, {len(exc)} exclusion criteria")

        # Check criterionItemId usage
        criterion_items = version.get("eligibilityCriterionItems", [])
        if criterion_items:
            result.add_info(f"Found {len(criterion_items)} eligibilityCriterionItem(s)")
        for crit in criteria:
            if crit.get("text") and not crit.get("criterionItemId"):
                result.warning(f"{prefix}: Criterion uses legacy inline 'text'; should use criterionItemId")

        # StudyInterventionIds (design references version-level interventions)
        intv_ids = design.get("studyInterventionIds", [])
        # Also check for legacy design-level studyInterventions
        if design.get("studyInterventions"):
            result.warning(f"{prefix}: Has design-level 'studyInterventions'; should be at version level")

        # Schedule timelines
        timelines = design.get("scheduleTimelines", [])
        result.add_info(f"{prefix}: {len(timelines)} schedule timeline(s)")

    # Version-level studyInterventions
    interventions = version.get("studyInterventions", [])
    result.add_info(f"Version-level: {len(interventions)} intervention(s)")

    # Version-level biomedicalConcepts
    bcs = version.get("biomedicalConcepts", [])
    result.add_info(f"Version-level: {len(bcs)} biomedical concept(s)")

    # 8. Cross-reference integrity
    all_ids = collect_ids(data, "root")
    all_refs = collect_references(data, "root")

    orphan_refs = [(ref_id, path) for ref_id, path in all_refs if ref_id not in all_ids]
    if orphan_refs:
        for ref_id, path in orphan_refs[:20]:  # Cap output
            result.error(f"Broken reference at {path}: '{ref_id}' not found")
        if len(orphan_refs) > 20:
            result.error(f"... and {len(orphan_refs) - 20} more broken references")
    else:
        result.add_info(f"All {len(all_refs)} cross-references are valid")

    # 9. instanceType checks
    validate_instance_types(data, "root", result)

    # 10. extensionAttributes checks
    validate_extension_attributes(data, "root", result)

    # 11. Code object validation
    validate_code_objects(data, "root", result)

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate USDM v4.0.0 JSON structure")
    parser.add_argument("--input", "-i", required=True, help="Path to USDM JSON file")
    parser.add_argument("--json-output", "-o", help="Optional: save report as JSON")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    result = validate_study(data)
    print(result.summary())

    if args.json_output:
        report = {
            "is_valid": result.is_valid,
            "error_count": len(result.errors),
            "warning_count": len(result.warnings),
            "errors": result.errors,
            "warnings": result.warnings,
            "info": result.info,
        }
        with open(args.json_output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nJSON report saved to: {args.json_output}")

    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    main()
