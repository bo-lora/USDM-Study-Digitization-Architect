#!/usr/bin/env python3
"""
SDTM Trial Design Dataset Generator

Generates SDTM Trial Design Domain datasets from USDM v4.0.0 JSON:
  - TA (Trial Arms)
  - TE (Trial Elements)
  - TI (Trial Inclusion/Exclusion)
  - TV (Trial Visits)
  - TS (Trial Summary)

Usage:
    python sdtm_trial_design_generator.py \
        --input study_definition.json \
        --output-dir output/sdtm/
"""

import json
import argparse
import os
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("ERROR: pandas is required. Install with: pip install pandas")
    raise

from usdm_utils import (
    get_version_and_design,
    sort_linked_list,
    get_study_id,
    get_study_title,
    get_criterion_text,
    get_enrollment_number,
)


def load_usdm(path: str) -> dict:
    """Load and return USDM JSON."""
    with open(path) as f:
        return json.load(f)


def make_code(name: str, max_len: int) -> str:
    """Create a short code from a name (uppercase, no spaces, truncated)."""
    return name.upper().replace(" ", "").replace("-", "").replace("/", "")[:max_len]


def generate_ta(data: dict) -> pd.DataFrame:
    """Generate TA (Trial Arms) domain."""
    version, design = get_version_and_design(data)
    study_id = get_study_id(version)

    arms = design.get("arms", design.get("studyArms", []))
    epochs = sort_linked_list(design.get("epochs", design.get("studyEpochs", [])))
    cells = design.get("studyCells", [])
    elements = {e["id"]: e for e in design.get("elements", design.get("studyElements", []))}

    rows = []
    for arm in arms:
        arm_id = arm["id"]
        taetord = 0
        for epoch in epochs:
            epoch_id = epoch["id"]
            matching_cells = [
                c for c in cells
                if c.get("armId") == arm_id and c.get("epochId") == epoch_id
            ]
            for cell in matching_cells:
                for elem_id in cell.get("elementIds", []):
                    elem = elements.get(elem_id, {})
                    taetord += 1
                    rows.append({
                        "STUDYID": study_id,
                        "DOMAIN": "TA",
                        "ARMCD": make_code(arm.get("name", ""), 20),
                        "ARM": arm.get("label", arm.get("name", "")),
                        "TAETORD": taetord,
                        "ETCD": make_code(elem.get("name", ""), 8),
                        "ELEMENT": elem.get("label", elem.get("name", "")),
                        "TABRANCH": "",
                        "TATRANS": "",
                        "EPOCH": epoch.get("label", epoch.get("name", "")),
                    })

    return pd.DataFrame(rows)


def generate_te(data: dict) -> pd.DataFrame:
    """Generate TE (Trial Elements) domain."""
    version, design = get_version_and_design(data)
    study_id = get_study_id(version)

    elements = design.get("elements", design.get("studyElements", []))

    rows = []
    for elem in elements:
        rows.append({
            "STUDYID": study_id,
            "DOMAIN": "TE",
            "ETCD": make_code(elem.get("name", ""), 8),
            "ELEMENT": elem.get("label", elem.get("name", "")),
            "TESTRL": "",
            "TEENRL": "",
            "TEDUR": "",
        })

    return pd.DataFrame(rows)


def generate_ti(data: dict) -> pd.DataFrame:
    """Generate TI (Trial Inclusion/Exclusion) domain."""
    version, design = get_version_and_design(data)
    study_id = get_study_id(version)

    criteria = design.get("eligibilityCriteria", [])
    criterion_items = version.get("eligibilityCriterionItems", [])

    rows = []
    inc_num = 0
    exc_num = 0

    for c in criteria:
        category = c.get("category", {}).get("decode", "")
        if "inclusion" in category.lower():
            inc_num += 1
            ietestcd = f"IN{inc_num:02d}"
            iecat = "INCLUSION"
        else:
            exc_num += 1
            ietestcd = f"EX{exc_num:02d}"
            iecat = "EXCLUSION"

        # Resolve criterion text via criterionItemId if available
        text = get_criterion_text(c, criterion_items)

        rows.append({
            "STUDYID": study_id,
            "DOMAIN": "TI",
            "IETESTCD": ietestcd,
            "IETEST": text,
            "IECAT": iecat,
            "IESCAT": "",
            "TIRL": "",
            "TIVERS": "1",
        })

    return pd.DataFrame(rows)


def generate_tv(data: dict) -> pd.DataFrame:
    """Generate TV (Trial Visits) domain."""
    version, design = get_version_and_design(data)
    study_id = get_study_id(version)

    encounters = sort_linked_list(design.get("encounters", []))

    rows = []
    for i, enc in enumerate(encounters, 1):
        rows.append({
            "STUDYID": study_id,
            "DOMAIN": "TV",
            "VISITNUM": i,
            "VISIT": enc.get("label", enc.get("name", "")),
            "VISITDY": "",
            "ARMCD": "",
            "ARM": "",
            "TVSTRL": "",
            "TVENRL": "",
        })

    return pd.DataFrame(rows)


def generate_ts(data: dict) -> pd.DataFrame:
    """Generate TS (Trial Summary) domain."""
    version, design = get_version_and_design(data)
    study_id = get_study_id(version)

    # Title from version.titles[]
    title = get_study_title(version)

    # Phase from design.studyPhase
    phase = design.get("studyPhase", {}).get("standardCode", {}).get("decode", "")

    # Intervention model from design.model (not interventionModel)
    model = design.get("model", design.get("interventionModel", {}))
    int_model = model.get("decode", "") if isinstance(model, dict) else ""

    # Arms count
    arms = design.get("arms", design.get("studyArms", []))
    num_arms = len(arms)

    # Planned enrollment from design.population (singular)
    planned_enrollment = get_enrollment_number(design)

    # Blinding from design.blindingSchema
    blinding = design.get("blindingSchema", {})
    blinding_text = ""
    if isinstance(blinding, dict):
        std_code = blinding.get("standardCode", {})
        blinding_text = std_code.get("decode", "") if isinstance(std_code, dict) else ""

    # Study type
    study_type = design.get("studyType", {}).get("decode", "")

    params = [
        ("STUDYID", study_id, "Study Identifier"),
        ("TITLE", title, "Study Title"),
        ("TPHASE", phase, "Trial Phase"),
        ("STYPE", study_type, "Study Type"),
        ("INTMODEL", int_model, "Intervention Model"),
        ("NARMS", str(num_arms), "Number of Arms"),
        ("PCNT", planned_enrollment, "Planned Number of Subjects"),
        ("RANDOM", "Y" if num_arms > 1 else "N", "Trial is Randomized"),
        ("BLIND", blinding_text, "Blinding Schema"),
    ]

    rows = []
    for seq, (tsparmcd, tsval, tsparm) in enumerate(params, 1):
        rows.append({
            "STUDYID": study_id,
            "DOMAIN": "TS",
            "TSSEQ": seq,
            "TSGRPID": "",
            "TSPARMCD": tsparmcd,
            "TSPARM": tsparm,
            "TSVAL": tsval,
            "TSVALNF": "",
            "TSVALCD": "",
            "TSVCDREF": "",
            "TSVCDVER": "",
        })

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Generate SDTM Trial Design datasets from USDM v4.0.0 JSON"
    )
    parser.add_argument("--input", "-i", required=True, help="Path to USDM JSON file")
    parser.add_argument("--output-dir", "-o", required=True, help="Output directory for CSV files")
    parser.add_argument("--format", "-f", default="csv", choices=["csv"], help="Output format")
    args = parser.parse_args()

    data = load_usdm(args.input)
    os.makedirs(args.output_dir, exist_ok=True)

    generators = {
        "ta": generate_ta,
        "te": generate_te,
        "ti": generate_ti,
        "tv": generate_tv,
        "ts": generate_ts,
    }

    for domain, gen_func in generators.items():
        df = gen_func(data)
        output_path = os.path.join(args.output_dir, f"{domain}.csv")
        df.to_csv(output_path, index=False)
        print(f"  ✓ {domain.upper()} → {output_path} ({len(df)} rows)")

    print(f"\nAll SDTM Trial Design datasets written to {args.output_dir}")


if __name__ == "__main__":
    main()
