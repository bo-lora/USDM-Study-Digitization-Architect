# USDM Study Digitization Architect

A **Claude skill** for converting clinical trial protocols into machine-readable [CDISC USDM v4.0.0](https://www.cdisc.org/ddf) JSON and generating downstream regulatory artifacts (M11 documents, SDTM Trial Design datasets, Data Transfer Agreements).

## What is this?

Clinical trial protocols are typically written as Word/PDF documents. Regulatory agencies, data standards, and modern clinical systems increasingly need this information in structured, machine-readable formats. This project provides:

1. **A Claude skill** (`SKILL.md`) that teaches Claude how to read a protocol and produce valid USDM v4.0.0 JSON — the CDISC standard for representing study definitions digitally.
2. **Python scripts** that process USDM JSON into downstream artifacts: validation reports, SDTM datasets, and M11 protocol documents.
3. **Reference data** including real-world USDM outputs and source protocol PDFs for testing.

## Who is this for?

- **Clinical data standards teams** digitizing protocols for Study Definitions Repositories (SDR)
- **Regulatory submission teams** preparing ICH M11 compliant documents
- **SDTM programmers** generating Trial Design datasets (TA, TE, TV, TI, TS)
- **Anyone working with CDISC DDF** (Digital Data Flow) who wants to accelerate protocol digitization

## Quick Start

### 1. Digitize a protocol with Claude

Add `SKILL.md` to your Claude project as a knowledge file (or paste it into your system prompt). Then provide a protocol:

```
Analyze the attached protocol PDF and generate a USDM v4.0.0 JSON study definition.
```

Claude will extract study metadata, arms, epochs, objectives, endpoints, eligibility criteria, interventions, and schedule of activities — then produce a conformant JSON file.

### 2. Validate the output

```bash
python3 scripts/usdm_validator.py -i your_study.json
```

The validator checks:
- Root envelope fields (`usdmVersion`, `systemName`, `systemVersion`)
- Correct navigation path (`study.versions[0].studyDesigns[0]`)
- `InterventionalStudyDesign` instanceType
- Linked-list integrity (`previousId`/`nextId` chains)
- Cross-reference integrity (all `*Id`/`*Ids` resolve)
- CT code structure
- Detects legacy field names with warnings

### 3. Generate SDTM Trial Design datasets

```bash
pip install pandas
python3 scripts/sdtm_trial_design_generator.py -i your_study.json -o output/sdtm/
```

Produces CSV files for five SDTM Trial Design domains:

| Domain | Description |
|--------|-------------|
| **TA** | Trial Arms — arm/epoch/element matrix |
| **TE** | Trial Elements — element definitions |
| **TV** | Trial Visits — encounter schedule |
| **TI** | Trial Inclusion/Exclusion — eligibility criteria |
| **TS** | Trial Summary — key study parameters |

### 4. Generate an M11 protocol document

```bash
pip install python-docx
python3 scripts/m11_document_generator.py -i your_study.json -o protocol_m11.docx
```

Produces a Word document following the ICH M11 CeSHarP template structure: title page, synopsis, trial design matrix, objectives/endpoints, eligibility criteria, interventions, and schedule of activities.

## Repository Structure

```
SKILL.md                    # Claude skill definition (add to your Claude project)
scripts/
  usdm_utils.py             # Shared utilities for navigating USDM v4.0.0 JSON
  usdm_validator.py          # Structural validator
  sdtm_trial_design_generator.py  # SDTM TA/TE/TV/TI/TS generator
  m11_document_generator.py  # ICH M11 Word document generator
examples/
  sources/                   # Source protocol PDFs
    Sanofi_NCT03637764_Oncology.pdf
    EliLilly_NCT04557384_Oncology.pdf
    Roche_NCT02291289_Oncology.pdf
  outputs/                   # Reference USDM v4.0.0 JSON outputs
    Sanofi_NCT03637764_Oncology_USDM_v4.json
docs/
  ct_quick_reference.md      # CDISC Controlled Terminology lookup table
templates/
  dta_template.md            # Data Transfer Agreement template
```

## USDM v4.0.0 at a Glance

The USDM (Unified Study Definitions Model) is the CDISC standard for representing clinical study definitions as structured data. Version 4.0.0 has a specific structure that differs significantly from earlier drafts:

```
Root envelope (usdmVersion, systemName, systemVersion)
└── study
    └── versions[0]              # StudyVersion wrapper
        ├── titles[]             # StudyTitle objects
        ├── studyIdentifiers[]   # text + scopeId (not inline org)
        ├── organizations[]      # Referenced by scopeId
        ├── studyDesigns[0]      # InterventionalStudyDesign
        │   ├── arms[]           # (not studyArms), type (not armType)
        │   ├── epochs[]         # (not studyEpochs), previousId/nextId ordering
        │   ├── elements[]       # (not studyElements)
        │   ├── objectives[]     # endpoints[] embedded (not separate array)
        │   ├── population       # singular (not populations[])
        │   ├── indications[]
        │   └── ...
        ├── studyInterventions[] # Version-level, not design-level
        ├── biomedicalConcepts[] # Version-level, not design-level
        └── eligibilityCriterionItems[]  # Text templates for criteria
```

See `SKILL.md` Section 2.2 for the complete class hierarchy, and Section 2.3 for the field rename mapping table.

## Example: Test Against Sanofi Reference

The `examples/outputs/` folder contains a real v4.0.0 output from the [data4knowledge/usdm_data](https://github.com/data4knowledge/usdm_data) project. You can run all scripts against it:

```bash
# Validate
python3 scripts/usdm_validator.py -i examples/outputs/Sanofi_NCT03637764_Oncology_USDM_v4.json

# Generate SDTM datasets
python3 scripts/sdtm_trial_design_generator.py \
  -i examples/outputs/Sanofi_NCT03637764_Oncology_USDM_v4.json \
  -o output/sdtm/

# Generate M11 document
python3 scripts/m11_document_generator.py \
  -i examples/outputs/Sanofi_NCT03637764_Oncology_USDM_v4.json \
  -o output/protocol_m11.docx
```

## Requirements

- **Python 3.9+**
- **pandas** (for SDTM generator): `pip install pandas`
- **python-docx** (for M11 generator): `pip install python-docx`
- No dependencies required for the validator

## Related Standards

| Standard | Role |
|----------|------|
| [USDM v4.0.0](https://github.com/cdisc-org/DDF-RA) | Data model for study definitions |
| [ICH M11](https://www.ich.org/page/multidisciplinary-guidelines#11) | Standardized clinical protocol template |
| [SDTM](https://www.cdisc.org/standards/foundational/sdtm) | Trial Design domain datasets |
| [CDISC CORE](https://github.com/cdisc-org/cdisc-rules-engine) | Rules engine for JSON schema validation |
| [TransCelerate SDR](https://github.com/transcelerate/ddf-sdr-api) | Study Definitions Repository API (V5 = USDM V4.0) |

## License

See [LICENSE](LICENSE) for details.
