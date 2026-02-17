# CDISC Controlled Terminology Quick Reference

> Frequently used CT codes for USDM v4.0.0 study definitions.
> Source: CDISC CT packages (SDTMCT, PROTOCOLCT, DDFCT) version 2025-09-26.

## Study Phase

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Phase I Trial | C15600 | PHASE I TRIAL |
| Phase I/Phase II Trial | C15693 | PHASE I/II TRIAL |
| Phase II Trial | C15601 | PHASE II TRIAL |
| Phase II/Phase III Trial | C15694 | PHASE II/III TRIAL |
| Phase III Trial | C15602 | PHASE III TRIAL |
| Phase III/Phase IV Trial | C15695 | PHASE IIIA/PHASE IV TRIAL |
| Phase IV Trial | C49686 | PHASE IV TRIAL |

## Arm Type

> **v4.0.0 field name:** `arm.type` (not `arm.armType`)

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Investigational Arm | C174266 | EXPERIMENTAL |
| Active Comparator Arm | C174267 | ACTIVE_COMPARATOR |
| Placebo Control Arm | C174268 | PLACEBO_CONTROL |
| Sham Comparator Arm | C174269 | SHAM_COMPARATOR |
| No Intervention Arm | C174270 | NO_INTERVENTION |

## Epoch Type

> **v4.0.0 field name:** `epoch.type` (not `epoch.epochType`)
> **v4.0.0 ordering:** `previousId`/`nextId` linked list (not `sequenceNumber`)

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Screening Epoch | C202487 | SCREENING |
| Run-in Epoch | C198283 | RUN-IN |
| Treatment Epoch | C101526 | TREATMENT |
| Follow-Up Epoch | C202578 | FOLLOW-UP |
| Long-term Follow-up Epoch | C202577 | LONG-TERM FOLLOW-UP |
| Washout Epoch | C48271 | WASHOUT |

## Objective Level

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Trial Primary Objective | C85826 | PRIMARY |
| Trial Secondary Objective | C85827 | SECONDARY |
| Exploratory Objective | C98782 | EXPLORATORY |

## Endpoint Level

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Primary Endpoint | C94496 | PRIMARY |
| Secondary Endpoint | C98781 | SECONDARY |
| Exploratory Endpoint | C98782 | EXPLORATORY |

## Eligibility Category

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Inclusion Criteria | C25532 | INCLUSION |
| Exclusion Criteria | C25370 | EXCLUSION |

## Intervention Model

> **v4.0.0 field name:** `design.model` (not `design.interventionModel`)

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Parallel Study | C82639 | PARALLEL |
| Crossover Study | C82638 | CROSSOVER |
| Sequential Study | C82640 | SEQUENTIAL |
| Factorial Study | C82637 | FACTORIAL |
| Single Group Study | C82636 | SINGLE_GROUP |
| Group Sequential Design | C142568 | GROUP_SEQUENTIAL |

## Intervention Role

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Protocol Agent | C41161 | INVESTIGATIONAL |
| Active Comparator | C82590 | ACTIVE_COMPARATOR |
| Placebo | C49648 | PLACEBO |
| Sham Comparator | C82591 | SHAM |

## Study Type

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Interventional Study | C98388 | INTERVENTIONAL |
| Observational Study | C142615 | OBSERVATIONAL |
| Expanded Access | C176245 | EXPANDED_ACCESS |

## Organization Type

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Drug Company | C54149 | DRUG_COMPANY |
| Clinical Study Sponsor | C70793 | SPONSOR |
| Study Registry | C93453 | REGISTRY |
| Regulatory Agency | C188863 | REGULATORY_AGENCY |
| Ethics Committee | C16741 | ETHICS_COMMITTEE |

## Encounter Type

> **v4.0.0 field name:** `encounter.type` (not `encounter.encounterType`)

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Visit | C25716 | VISIT |
| Screening Visit | C174122 | SCREENING_VISIT |
| Treatment Visit | C174126 | TREATMENT_VISIT |
| Follow-up Visit | C174128 | FOLLOWUP_VISIT |
| Completion/Early Termination Visit | C174127 | COMPLETION_VISIT |

## Blinding Schema

> **v4.0.0 field name:** `design.blindingSchema` (AliasCode)

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Open Label Study | C49659 | OPEN_LABEL |
| Single Blind Study | C15228 | SINGLE_BLIND |
| Double Blind Study | C15227 | DOUBLE_BLIND |
| Triple Blind Study | C206217 | TRIPLE_BLIND |

## Environmental Settings

> **v4.0.0 field:** `encounter.environmentalSettings[]`

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Clinic | C211570 | CLINIC |
| Hospital | C211571 | HOSPITAL |
| Home | C211572 | HOME |
| Pharmacy | C211573 | PHARMACY |

## Contact Modes

> **v4.0.0 field:** `encounter.contactModes[]`

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| In Person | C175574 | IN_PERSON |
| Telephone | C175575 | TELEPHONE |
| Virtual | C175576 | VIRTUAL |

## Protocol Status

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Draft | C132351 | DRAFT |
| Final | C132352 | FINAL |
| Amended | C132353 | AMENDED |

## Study Title Type

> **v4.0.0:** Titles are `StudyTitle` objects at `version.titles[]`

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Brief Study Title | C207615 | BRIEF |
| Official Study Title | C207616 | OFFICIAL |

## Timing Type

> **v4.0.0:** Timings are nested inside `scheduleTimelines[]`

| Preferred Term | C-Code | Submission Value |
|---------------|--------|-----------------|
| Before | C201357 | BEFORE |
| After | C201356 | AFTER |
| Fixed Reference | C201358 | FIXED_REFERENCE |

---

## Usage in USDM v4.0.0 JSON

CT codes appear in two patterns:

### `Code` object (most elements)
```json
{
  "id": "Code_1",
  "extensionAttributes": [],
  "code": "C15602",
  "codeSystem": "http://www.cdisc.org",
  "codeSystemVersion": "2025-09-26",
  "decode": "Phase III Trial",
  "instanceType": "Code"
}
```

### `AliasCode` object (study phase, blinding schema, intervention codes)
```json
{
  "id": "AliasCode_1",
  "extensionAttributes": [],
  "standardCode": { /* Code object */ },
  "standardCodeAliases": [],
  "instanceType": "AliasCode"
}
```

### v4.0.0 Field Name Changes

| Legacy Field | v4.0.0 Field | Context |
|-------------|-------------|---------|
| `armType` | `type` | On StudyArm |
| `epochType` | `type` | On StudyEpoch |
| `encounterType` | `type` | On Encounter |
| `interventionModel` | `model` | On StudyDesign |
| `trialIntentTypes` | `intentTypes` | On StudyDesign |
| `trialTypes` | `subTypes` | On StudyDesign |
| `sequenceNumber` | `previousId`/`nextId` | On epochs, encounters, activities |

### Input flexibility
When entering data via Excel, any of these are accepted:
- C-Code: `C15602`
- Submission Value: `PHASE III TRIAL`
- Preferred Term: `Phase III Trial`
