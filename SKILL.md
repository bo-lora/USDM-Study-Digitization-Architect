# USDM Study Digitization Architect

> **Skill Name:** USDM Study Digitization Architect
> **Version:** 2.0
> **Target Standard:** USDM v4.0.0 (CDISC Digital Data Flow Reference Architecture)
> **Mode:** Dual — Programmatic Code Generation + Knowledge-Driven Drafting

---

## 1. PURPOSE

This skill guides Claude in digitizing clinical trial protocols into the CDISC Unified Study Definitions Model (USDM) v4.0.0 and producing all downstream artifacts in the Digital Data Flow (DDF) ecosystem. Claude operates as a **Study Digitization Architect** — able to both *reason about* clinical trial design elements and *generate code/artifacts* that conform to the USDM, ICH M11, SDTM Trial Design, and DDF API specifications.

### What This Skill Covers

| Priority | Output | Format |
|----------|--------|--------|
| 1 (Primary) | USDM JSON from protocol text | JSON (API-conformant) |
| 2 | M11-compliant protocol documents | PDF / DOCX |
| 3 | Data Transfer Agreements & Specifications | DOCX / structured templates |
| 4 | SDTM Trial Design Domain datasets & metadata | SAS XPT / CSV / Define-XML |

---

## 2. DOMAIN KNOWLEDGE FOUNDATION

### 2.1 Key Standards & Their Relationships

```
┌─────────────────────────────────────────────────────┐
│                  PROTOCOL (Source)                   │
│         (Unstructured PDF/Word document)             │
└──────────────────────┬──────────────────────────────┘
                       │ Digitization
                       ▼
┌─────────────────────────────────────────────────────┐
│            USDM v4.0.0 (Data Model)                 │
│   Unified Study Definitions Model — the canonical   │
│   machine-readable representation of a study def.   │
│   Superset of ICH M11 content.                      │
└───┬──────────┬──────────┬──────────┬────────────────┘
    │          │          │          │
    ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌──────────────┐
│ M11    │ │ SDTM   │ │ DTA/   │ │ EDC / CTMS   │
│Protocol│ │ Trial  │ │ DTS    │ │ Config       │
│ (Doc)  │ │ Design │ │        │ │              │
└────────┘ └────────┘ └────────┘ └──────────────┘
```

**USDM v4.0.0** is the authoritative data model. It is a CDISC standard developed in collaboration with TransCelerate BioPharma as part of the Digital Data Flow (DDF) initiative. Key facts:

- The USDM is an **abstract model** independent of any rendering (Word, PDF, JSON, FHIR).
- It is a **superset** of ICH M11 CeSHarP content — it covers everything M11 defines plus deeper protocol detail (Schedule of Activities, Biomedical Concepts, eligibility criteria logic, etc.).
- The canonical source artifacts live in the **cdisc-org/DDF-RA** GitHub repository.
- The API exchange format is **JSON**, defined via an **OpenAPI specification**.
- Cross-references in the JSON use `*Id`/`*Ids` suffix conventions to avoid duplication.
- Each class carries an `instanceType` attribute reflecting the original UML class name.
- **Every object** must include `extensionAttributes: []` and `notes: []` arrays.
- **Every named object** should include `name`, `label`, and `description` fields.
- Ordering uses **linked-list** patterns (`previousId`/`nextId`) instead of sequence numbers.
- The root envelope includes `usdmVersion`, `systemName`, and `systemVersion`.
- The CDISC Rules Engine (**CORE**) supports JSON Schema validation against USDM v3.0 and v4.0.

**ICH M11 CeSHarP** (adopted November 2025) consists of three components:
1. **Guideline** — protocol design principles
2. **Template** — standardized ToC, section headers, common text, data fields
3. **Technical Specification** — conformance, cardinality, and exchange attributes

**SDR (Study Definitions Repository)** — TransCelerate's open-source reference implementation:
- API V5 maps to USDM V4.0 (API V4 → USDM V3.0, API V3 → USDM V2.0)
- Docker-based deployment; MongoDB backend
- GitHub: `transcelerate/ddf-sdr-api`

### 2.2 USDM v4.0.0 Core Class Hierarchy

The following is the **essential class structure** Claude must understand to generate valid USDM v4.0.0 JSON. This is derived from the UML class diagram, the OpenAPI specification, and validated against real reference outputs.

```
Root JSON envelope
├── usdmVersion: "4.0.0"
├── systemName: string
├── systemVersion: string
└── study: Study
    ├── id: string
    ├── name: string
    ├── description: string | null
    ├── label: string | null
    ├── instanceType: "Study"
    ├── versions: StudyVersion[]
    │   ├── id: string
    │   ├── extensionAttributes: []
    │   ├── versionIdentifier: string (e.g., "1.0", "amendment 5")
    │   ├── rationale: string
    │   ├── documentVersionIds: string[]
    │   ├── dateValues: DateValue[]
    │   ├── amendments: StudyAmendment[]
    │   ├── studyIdentifiers: StudyIdentifier[]
    │   │   ├── id: string
    │   │   ├── extensionAttributes: []
    │   │   ├── text: string (the identifier value, e.g., "NCT03637764")
    │   │   ├── scopeId: string (→ Organization)
    │   │   └── instanceType: "StudyIdentifier"
    │   ├── studyDesigns: InterventionalStudyDesign[]
    │   │   ├── id: string
    │   │   ├── extensionAttributes: []
    │   │   ├── name: string
    │   │   ├── label: string
    │   │   ├── description: string
    │   │   ├── instanceType: "InterventionalStudyDesign"
    │   │   ├── studyType: Code
    │   │   ├── studyPhase: AliasCode
    │   │   ├── therapeuticAreas: Code[]
    │   │   ├── characteristics: Code[]
    │   │   ├── blindingSchema: AliasCode
    │   │   ├── model: Code (Parallel, Crossover, etc.)
    │   │   ├── intentTypes: Code[] (Treatment, Prevention, etc.)
    │   │   ├── subTypes: Code[] (Safety, Efficacy, etc.)
    │   │   ├── arms: StudyArm[]
    │   │   │   ├── name, label, description
    │   │   │   ├── type: Code (not "armType")
    │   │   │   ├── dataOriginDescription: string
    │   │   │   ├── dataOriginType: Code
    │   │   │   ├── populationIds: string[]
    │   │   │   └── notes: []
    │   │   ├── epochs: StudyEpoch[]
    │   │   │   ├── name, label, description
    │   │   │   ├── type: Code (not "epochType")
    │   │   │   ├── previousId: string | null
    │   │   │   ├── nextId: string | null
    │   │   │   └── notes: []
    │   │   ├── elements: StudyElement[] (not "studyElements")
    │   │   │   ├── name, label, description
    │   │   │   ├── transitionStartRule: TransitionRule | null
    │   │   │   └── transitionEndRule: TransitionRule | null
    │   │   ├── studyCells: StudyCell[]
    │   │   │   ├── armId: string (→ StudyArm)
    │   │   │   ├── epochId: string (→ StudyEpoch)
    │   │   │   └── elementIds: string[] (→ StudyElement)
    │   │   ├── activities: Activity[]
    │   │   │   ├── name, label, description
    │   │   │   ├── previousId: string | null
    │   │   │   ├── nextId: string | null
    │   │   │   ├── childIds: string[]
    │   │   │   ├── definedProcedures: Procedure[]
    │   │   │   ├── biomedicalConceptIds: string[]
    │   │   │   ├── bcCategoryIds: string[]
    │   │   │   ├── bcSurrogateIds: string[]
    │   │   │   ├── timelineId: string | null
    │   │   │   └── notes: []
    │   │   ├── encounters: Encounter[]
    │   │   │   ├── name, label, description
    │   │   │   ├── type: Code (not "encounterType")
    │   │   │   ├── previousId: string | null
    │   │   │   ├── nextId: string | null
    │   │   │   ├── scheduledAtId: string | null
    │   │   │   ├── environmentalSettings: Code[]
    │   │   │   ├── contactModes: Code[]
    │   │   │   ├── transitionStartRule: TransitionRule | null
    │   │   │   ├── transitionEndRule: TransitionRule | null
    │   │   │   └── notes: []
    │   │   ├── scheduleTimelines: ScheduleTimeline[]
    │   │   │   ├── name, label, description
    │   │   │   ├── mainTimeline: boolean
    │   │   │   ├── entryCondition: string
    │   │   │   ├── entryId: string (→ first ScheduledActivityInstance)
    │   │   │   ├── exits: ScheduleTimelineExit[]
    │   │   │   ├── timings: Timing[] (nested, not design-level)
    │   │   │   │   ├── name, label, description
    │   │   │   │   ├── type: Code (Before, Fixed Reference, After, etc.)
    │   │   │   │   ├── value: string (ISO 8601 duration, e.g., "P4W")
    │   │   │   │   ├── valueLabel: string
    │   │   │   │   ├── relativeToFrom: Code (Start to Start, etc.)
    │   │   │   │   ├── relativeFromScheduledInstanceId: string
    │   │   │   │   ├── relativeToScheduledInstanceId: string
    │   │   │   │   ├── windowLower: string (ISO 8601 duration)
    │   │   │   │   ├── windowUpper: string (ISO 8601 duration)
    │   │   │   │   └── windowLabel: string
    │   │   │   └── instances: ScheduledActivityInstance[]
    │   │   │       ├── name, label, description
    │   │   │       ├── encounterId: string (→ Encounter)
    │   │   │       ├── activityIds: string[] (→ Activity)
    │   │   │       ├── epochId: string (→ StudyEpoch)
    │   │   │       ├── scheduledAtTimingId: string (→ Timing)
    │   │   │       └── defaultConditionId: string | null
    │   │   ├── indications: Indication[]
    │   │   │   ├── name, label, description
    │   │   │   ├── codes: Code[]
    │   │   │   ├── isRareDisease: boolean
    │   │   │   └── notes: []
    │   │   ├── objectives: Objective[]
    │   │   │   ├── name, label, description
    │   │   │   ├── text: string
    │   │   │   ├── level: Code (Trial Primary/Secondary/Exploratory)
    │   │   │   ├── endpoints: Endpoint[] (embedded, NOT separate array)
    │   │   │   │   ├── name, label, description
    │   │   │   │   ├── text: string
    │   │   │   │   ├── purpose: string
    │   │   │   │   └── level: Code
    │   │   │   └── dictionaryId: string | null
    │   │   ├── eligibilityCriteria: EligibilityCriterion[]
    │   │   │   ├── name, label, description
    │   │   │   ├── category: Code (Inclusion/Exclusion)
    │   │   │   ├── identifier: string (e.g., "I 1.", "E 1.")
    │   │   │   ├── criterionItemId: string (→ EligibilityCriterionItem)
    │   │   │   ├── previousId: string | null
    │   │   │   ├── nextId: string | null
    │   │   │   └── notes: []
    │   │   ├── population: StudyDesignPopulation (singular, NOT array)
    │   │   │   ├── name, label, description
    │   │   │   ├── includesHealthySubjects: boolean
    │   │   │   ├── plannedEnrollmentNumber: Range
    │   │   │   │   ├── minValue: Quantity {value, unit}
    │   │   │   │   ├── maxValue: Quantity {value, unit}
    │   │   │   │   └── isApproximate: boolean
    │   │   │   ├── plannedCompletionNumber: Range | null
    │   │   │   ├── plannedSex: Code[]
    │   │   │   ├── criterionIds: string[] (→ EligibilityCriterion)
    │   │   │   └── plannedAge: Range
    │   │   ├── studyInterventionIds: string[] (→ StudyIntervention)
    │   │   ├── estimands: Estimand[]
    │   │   ├── analysisPopulations: AnalysisPopulation[]
    │   │   └── notes: []
    │   ├── titles: StudyTitle[]
    │   │   ├── id: string
    │   │   ├── extensionAttributes: []
    │   │   ├── text: string (the actual title text)
    │   │   ├── type: Code ("Official Study Title", "Brief Study Title")
    │   │   └── instanceType: "StudyTitle"
    │   ├── organizations: Organization[]
    │   │   ├── id: string
    │   │   ├── extensionAttributes: []
    │   │   ├── name: string
    │   │   ├── label: string
    │   │   ├── type: Code (Drug Company, Study Registry, Regulatory Agency)
    │   │   ├── identifierScheme: string
    │   │   ├── identifier: string
    │   │   ├── legalAddress: Address
    │   │   ├── managedSites: StudySite[]
    │   │   └── instanceType: "Organization"
    │   ├── studyInterventions: StudyIntervention[] (version-level, NOT design)
    │   │   ├── name, label, description
    │   │   ├── role: Code
    │   │   ├── type: Code
    │   │   ├── codes: Code[]
    │   │   ├── minimumResponseDuration: Quantity
    │   │   ├── administrations: Administration[]
    │   │   └── instanceType: "StudyIntervention"
    │   ├── biomedicalConcepts: BiomedicalConcept[] (version-level, NOT design)
    │   │   ├── name, label, description
    │   │   ├── reference: string (CDISC Library URI)
    │   │   ├── synonyms: string[]
    │   │   ├── properties: BiomedicalConceptProperty[]
    │   │   └── instanceType: "BiomedicalConcept"
    │   ├── eligibilityCriterionItems: EligibilityCriterionItem[]
    │   │   ├── id: string
    │   │   ├── extensionAttributes: []
    │   │   ├── name: string
    │   │   ├── text: string (may contain <usdm:tag name="..."/> templates)
    │   │   ├── dictionaryId: string | null
    │   │   ├── notes: []
    │   │   └── instanceType: "EligibilityCriterionItem"
    │   ├── narrativeContentItems: NarrativeContentItem[]
    │   ├── abbreviations: Abbreviation[]
    │   ├── roles: StudyRole[]
    │   ├── referenceIdentifiers: StudyIdentifier[]
    │   └── instanceType: "StudyVersion"
    └── documentedBy: StudyDefinitionDocument[]
        ├── id: string
        ├── name: string
        ├── versions: StudyDefinitionDocumentVersion[]
        │   ├── contents: NarrativeContent[] (linked-list with previousId/nextId)
        │   └── instanceType: "StudyDefinitionDocumentVersion"
        └── instanceType: "StudyDefinitionDocument"
```

**CRITICAL v4.0.0 differences from earlier schemas:**

| Legacy (v3.x / draft) | v4.0.0 Correct | Notes |
|----------------------|---------------|-------|
| `study.studyTitle` | `version.titles[]` → `StudyTitle.text` | Title is a typed object |
| `study.studyDesigns[]` | `version.studyDesigns[]` | Via `versions[]` wrapper |
| `instanceType: "StudyDesign"` | `instanceType: "InterventionalStudyDesign"` | Subtype required |
| `studyArms` | `arms` | Shorter field name |
| `armType` | `type` | Generic field name |
| `studyEpochs` | `epochs` | Shorter field name |
| `epochType` | `type` | Generic field name |
| `sequenceNumber` | `previousId` / `nextId` | Linked-list ordering |
| `studyElements` | `elements` | Shorter field name |
| `interventionModel` | `model` | Shorter field name |
| `trialIntentTypes` | `intentTypes` | Shorter field name |
| `trialTypes` | `subTypes` | Shorter field name |
| `encounterType` | `type` | Generic field name |
| `populations[]` | `population` (singular) | Single object, not array |
| `endpoints[]` (design-level) | `objective.endpoints[]` | Embedded in Objective |
| `endpointIds[]` on Objective | `endpoints[]` on Objective | Direct nesting |
| `studyIdentifier` field | `text` field | On StudyIdentifier |
| `studyIdentifierScope` (inline) | `scopeId` (reference) | Org in separate array |
| `studyInterventions` on design | `studyInterventions` on version | Moved up one level |
| `biomedicalConcepts` on design | `biomedicalConcepts` on version | Moved up one level |
| `eligibilityCriteria[].text` | `criterionItemId` → item.text | Indirect text resolution |
| (none) | `extensionAttributes: []` | Required on every object |
| (none) | `notes: []` | Required on most objects |
| (none) | `name`, `label`, `description` | Universal on all named objects |

### 2.3 CDISC Controlled Terminology (CT)

USDM v4.0.0 uses three CT packages configured per study. When generating JSON, always reference valid CT codes:

| CT Package | Example Config | Usage |
|------------|---------------|-------|
| `SDTMCT` | `2025-09-26` | SDTM-aligned codes (arm type, epoch type, etc.) |
| `PROTOCOLCT` | `2025-09-26` | Protocol-specific terms |
| `DDFCT` | `2025-09-26` | DDF-specific controlled terminology |

**Common Code Patterns:**

```json
{
  "id": "Code_1",
  "extensionAttributes": [],
  "code": "C49488",
  "codeSystem": "http://www.cdisc.org",
  "codeSystemVersion": "2025-09-26",
  "decode": "Randomized",
  "instanceType": "Code"
}
```

For `AliasCode` (used for study phase, blinding schema, etc.):
```json
{
  "id": "AliasCode_1",
  "extensionAttributes": [],
  "standardCode": {
    "id": "Code_2",
    "extensionAttributes": [],
    "code": "C15602",
    "codeSystem": "http://www.cdisc.org",
    "codeSystemVersion": "2025-09-26",
    "decode": "Phase III Trial",
    "instanceType": "Code"
  },
  "standardCodeAliases": [],
  "instanceType": "AliasCode"
}
```

**Key CT Code References (frequently used):**

| Element | C-Code | Submission Value | Preferred Term |
|---------|--------|-----------------|----------------|
| Phase I | C15600 | PHASE I TRIAL | Phase I Trial |
| Phase II | C15601 | PHASE II TRIAL | Phase II Trial |
| Phase III | C15602 | PHASE III TRIAL | Phase III Trial |
| Phase IV | C49686 | PHASE IV TRIAL | Phase IV Trial |
| Experimental Arm | C174266 | EXPERIMENTAL | Investigational Arm |
| Placebo Control | C174268 | PLACEBO_CONTROL | Placebo Control Arm |
| Active Comparator | C174267 | ACTIVE_COMPARATOR | Active Comparator Arm |
| Screening Epoch | C202487 | SCREENING | Screening Epoch |
| Treatment Epoch | C101526 | TREATMENT | Treatment Epoch |
| Follow-up Epoch | C202578 | FOLLOW-UP | Follow-Up Epoch |
| Inclusion | C25532 | INCLUSION | Inclusion Criteria |
| Exclusion | C25370 | EXCLUSION | Exclusion Criteria |

Users can enter either the C-Code, submission value, or preferred term — they are equivalent.

---

## 3. WORKFLOW: PROTOCOL → USDM JSON

This is the **primary workflow** and highest-priority output.

### Step 1: Protocol Intake & Analysis

When the user provides protocol text (PDF, Word, or pasted text), Claude should:

1. **Identify study-level metadata**: title, acronym, phase, identifiers, sponsor, protocol version, amendment status
2. **Extract study design elements**: arms, epochs, cells, elements, intervention model, blinding
3. **Parse the Schedule of Activities (SoA)**: encounters, activities, timings, biomedical concepts
4. **Extract eligibility criteria**: inclusion/exclusion, structured as individual criteria with category codes
5. **Map objectives & endpoints**: primary, secondary, exploratory with endpoints embedded in each objective
6. **Identify interventions**: investigational product(s), comparators, placebo, administration details
7. **Identify indications**: disease conditions with coded references (e.g., SNOMED)

### Step 2: USDM JSON Assembly

Generate a complete USDM v4.0.0-conformant JSON document. The root structure:

```json
{
  "usdmVersion": "4.0.0",
  "systemName": "USDM Study Digitization Architect",
  "systemVersion": "2.0",
  "study": {
    "id": "Study_1",
    "name": "STUDY_SHORT_NAME",
    "description": null,
    "label": "Full study label",
    "instanceType": "Study",
    "versions": [
      {
        "id": "StudyVersion_1",
        "extensionAttributes": [],
        "versionIdentifier": "1.0",
        "rationale": "",
        "documentVersionIds": [],
        "dateValues": [],
        "amendments": [],
        "studyIdentifiers": [
          {
            "id": "StudyIdentifier_1",
            "extensionAttributes": [],
            "text": "SPONSOR-2025-001",
            "scopeId": "Organization_1",
            "instanceType": "StudyIdentifier"
          }
        ],
        "referenceIdentifiers": [],
        "studyDesigns": [
          {
            "id": "InterventionalStudyDesign_1",
            "extensionAttributes": [],
            "name": "Main Study Design",
            "label": "Primary study design",
            "description": "",
            "instanceType": "InterventionalStudyDesign",
            "studyType": { "...": "Code object" },
            "studyPhase": { "...": "AliasCode object" },
            "therapeuticAreas": [],
            "characteristics": [],
            "blindingSchema": { "...": "AliasCode object" },
            "model": { "...": "Code: Parallel, Crossover, etc." },
            "intentTypes": [],
            "subTypes": [],
            "arms": [],
            "epochs": [],
            "elements": [],
            "studyCells": [],
            "activities": [],
            "encounters": [],
            "scheduleTimelines": [],
            "indications": [],
            "objectives": [],
            "eligibilityCriteria": [],
            "population": { "...": "singular StudyDesignPopulation" },
            "studyInterventionIds": [],
            "estimands": [],
            "analysisPopulations": [],
            "notes": []
          }
        ],
        "titles": [
          {
            "id": "StudyTitle_1",
            "extensionAttributes": [],
            "text": "Brief title text here",
            "type": {
              "id": "Code_T1",
              "extensionAttributes": [],
              "code": "C207615",
              "codeSystem": "http://www.cdisc.org",
              "codeSystemVersion": "2025-09-26",
              "decode": "Brief Study Title",
              "instanceType": "Code"
            },
            "instanceType": "StudyTitle"
          },
          {
            "id": "StudyTitle_2",
            "extensionAttributes": [],
            "text": "A Phase III, Randomized, Double-Blind...",
            "type": {
              "id": "Code_T2",
              "extensionAttributes": [],
              "code": "C207616",
              "codeSystem": "http://www.cdisc.org",
              "codeSystemVersion": "2025-09-26",
              "decode": "Official Study Title",
              "instanceType": "Code"
            },
            "instanceType": "StudyTitle"
          }
        ],
        "organizations": [
          {
            "id": "Organization_1",
            "extensionAttributes": [],
            "name": "SPONSOR",
            "label": "Sponsor Corp",
            "type": {
              "id": "Code_O1",
              "extensionAttributes": [],
              "code": "C70793",
              "codeSystem": "http://www.cdisc.org",
              "codeSystemVersion": "2025-09-26",
              "decode": "Clinical Study Sponsor",
              "instanceType": "Code"
            },
            "identifierScheme": "DUNS",
            "identifier": "",
            "legalAddress": null,
            "managedSites": [],
            "instanceType": "Organization"
          }
        ],
        "studyInterventions": [],
        "biomedicalConcepts": [],
        "eligibilityCriterionItems": [],
        "narrativeContentItems": [],
        "abbreviations": [],
        "roles": [],
        "instanceType": "StudyVersion"
      }
    ],
    "documentedBy": []
  }
}
```

### Step 3: Validation Guidance

After generating JSON, Claude should:

1. **Self-check** against the class hierarchy (Section 2.2) for required fields
2. **Verify CT codes** are valid for the configured CT version
3. **Check cross-references**: all `*Id` and `*Ids` fields must reference existing object `id` values
4. **Verify linked-list integrity**: every `previousId`/`nextId` chain must be consistent
5. **Ensure `extensionAttributes: []`** is present on every object
6. **Note CORE validation**: Recommend the user run the CDISC Open Rules Engine against the output:

```bash
# Install CORE
pip install cdisc-rules-engine

# Validate USDM JSON
core validate -s usdm -sv 4.0 -d study_definition.json -o validation_report -of JSON
```

---

## 4. WORKFLOW: USDM → M11 PROTOCOL DOCUMENT

### M11 Template Mapping

The ICH M11 CeSHarP Template (adopted November 2025) defines a standardized protocol structure. The USDM is a superset of M11, so all M11 elements can be populated from USDM data.

**M11 Section-to-USDM Mapping (Key Sections):**

| M11 Section | M11 Heading | USDM v4.0.0 Source |
|-------------|------------|---------------------|
| Title Page | Protocol Title | `version.titles[]` (type = "Official Study Title") |
| Title Page | Protocol Identifier | `version.studyIdentifiers[]` → resolve via `scopeId` to org |
| Title Page | Sponsor | `version.organizations[]` (type = "Drug Company" or "Sponsor") |
| Title Page | Amendment | `version.amendments[]` |
| Synopsis | Study Phase | `design.studyPhase.standardCode.decode` |
| Synopsis | Study Design | `design.model.decode` |
| Synopsis | Number of Arms | `design.arms.length` |
| Synopsis | Planned Enrollment | `design.population.plannedEnrollmentNumber` |
| 1.1 | Trial Design | Arms × Epochs matrix from `studyCells`, epochs sorted by linked list |
| 1.2 | Trial Schema | Visual from epochs/arms/elements |
| 2.0 | Objectives | `design.objectives[]` by level |
| 2.0 | Endpoints | `design.objectives[].endpoints[]` (embedded in each objective) |
| 3.0 | Estimands | `design.estimands[]` |
| 4.0 | Eligibility | `design.eligibilityCriteria[]` → resolve text via `criterionItemId` |
| 5.0 | Interventions | `version.studyInterventions[]` (via `design.studyInterventionIds[]`) |
| 6.0 | SoA | `design.scheduleTimelines[]` with nested `timings[]` and `instances[]` |
| 6.0 | Indications | `design.indications[]` |

### Document Generation (Programmatic)

When asked to produce an M11-compliant document, Claude should generate Python code using the `python-docx` library. See `scripts/m11_document_generator.py` for the reference implementation.

---

## 5. WORKFLOW: DATA TRANSFER AGREEMENTS & SPECIFICATIONS

### 5.1 Data Transfer Agreement (DTA) Template

A DTA governs the operational aspects of non-CRF data transfers between sponsors and vendors (central lab, ECG, imaging, etc.). Claude should help draft DTAs with the following structure:

**DTA Sections:**

1. **Purpose & Scope** — study identifier, data types covered, vendor name
2. **Roles & Responsibilities** — sponsor data management, vendor technical contact
3. **Data Description** — datasets, variables, file formats (CSV, SAS XPT, Dataset-JSON)
4. **Transfer Schedule** — frequency (daily, weekly, cumulative/incremental), trigger events
5. **Transfer Method** — SFTP, API, secure portal; encryption requirements
6. **File Naming Convention** — e.g., `{StudyID}_{DataType}_{SiteID}_{YYYYMMDD}_{Seq}.csv`
7. **Data Specifications Reference** — pointer to the DTS document
8. **Reconciliation Process** — frequency, method, escalation
9. **Issue Management** — query process, turnaround times, contacts
10. **Confidentiality & Compliance** — GDPR, 21 CFR Part 11, data retention

### 5.2 Data Transfer Specification (DTS) Template

The DTS defines the technical content — the actual variable-level metadata:

```
| Variable Name     | Label                 | Type    | Length | Format     | Codelist        | Required | Notes                    |
|-------------------|-----------------------|---------|--------|------------|-----------------|----------|--------------------------|
| STUDYID           | Study Identifier      | Char    | 20     |            |                 | Yes      | Protocol number          |
| SITEID            | Site Identifier       | Char    | 10     |            |                 | Yes      |                          |
| SUBJID            | Subject Identifier    | Char    | 20     |            |                 | Yes      |                          |
| VISIT             | Visit Name            | Char    | 40     |            |                 | Yes      | From SoA                 |
| VISITNUM          | Visit Number          | Num     | 8      |            |                 | Yes      |                          |
| LBDTC             | Lab Date/Time         | Char    | 20     | ISO 8601   |                 | Yes      | YYYY-MM-DDThh:mm:ss      |
| LBTESTCD          | Lab Test Short Name   | Char    | 8      |            | LBTESTCD_CL     | Yes      | CDISC CT                 |
| LBTEST            | Lab Test Name         | Char    | 40     |            |                 | Yes      |                          |
| LBORRES           | Result (Original)     | Char    | 200    |            |                 | Yes      |                          |
| LBORRESU          | Original Units        | Char    | 40     |            | UNIT_CL         | Cond     |                          |
| LBORNRLO          | Normal Range Lower    | Char    | 200    |            |                 | Cond     |                          |
| LBORNRHI          | Normal Range Upper    | Char    | 200    |            |                 | Cond     |                          |
| LBNRIND           | Normal/Abnormal Flag  | Char    | 20     |            | LBNRIND_CL      | Cond     | NORMAL, ABNORMAL, etc.   |
```

When generating a DTS, Claude should:
- Derive visit names from USDM `encounters` and `scheduleTimelines[].instances[]`
- Align test codes with CDISC CT and the USDM `biomedicalConcepts`
- Include both sponsor-expected and vendor-native variable mappings

---

## 6. WORKFLOW: SDTM TRIAL DESIGN DATASETS

The USDM can directly populate SDTM Trial Design Domain datasets. These are metadata datasets describing the study structure.

### Key Trial Design Domains from USDM

| SDTM Domain | Description | USDM v4.0.0 Source |
|-------------|-------------|---------------------|
| **TA** (Trial Arms) | Arm definitions | `design.arms` |
| **TE** (Trial Elements) | Element definitions per arm | `design.elements` |
| **TV** (Trial Visits) | Visit schedule | `design.encounters` (sorted by linked list) |
| **TS** (Trial Summary) | Key study parameters | `version.titles[]`, `design.studyPhase`, etc. |
| **TI** (Trial Inclusion/Exclusion) | Eligibility criteria | `design.eligibilityCriteria` → resolve via `criterionItemId` |
| **SE** (Subject Elements) | Actual element start/end | Derived at execution |

See `scripts/sdtm_trial_design_generator.py` for the reference implementation.

---

## 7. TOOL INTEGRATION REFERENCE

### 7.1 CDISC Open Rules Engine (CORE)

```bash
# Installation
pip install cdisc-rules-engine

# Set API key for CDISC Library access
export CDISC_LIBRARY_API_KEY=<your_key>

# Update local rule cache
core update-cache

# Validate USDM JSON (v4.0)
core validate \
  -s usdm \
  -sv 4.0 \
  -d study_definition.json \
  -o validation_report \
  -of JSON

# Output formats: JSON or XLSX
```

### 7.2 USDM Python Package (PyPI)

The `usdm` package (for v3.x) and `usdm4-excel` package (for v4.0) provide:
- Model classes reflecting the USDM UML
- Excel-to-JSON import
- CDISC Library integration for CT and Biomedical Concepts

```bash
pip install usdm           # v3.x model + Excel importer
pip install usdm4-excel    # v4.0 Excel format support
```

```python
# Example: Load study from Excel and export JSON
from usdm_excel import USDMExcel
import os

os.environ["CDISC_API_KEY"] = "<your_key>"
excel = USDMExcel()
excel.from_excel("study_definition.xlsx")
json_output = excel.to_json()
```

### 7.3 SDR API (Study Definitions Repository)

The TransCelerate SDR reference implementation:

```bash
# Run SDR via Docker
docker run \
  -e ConnectionStrings__DefaultConnection='<MONGO_CONNECTION_STRING>' \
  -e ConnectionStrings__DatabaseName='SDR' \
  ghcr.io/transcelerate/ddf-sdr-api:latest
```

API endpoint mapping:
- **API V5** → USDM V4.0
- **API V4** → USDM V3.0
- **API V3** → USDM V2.0

```
POST   /v5/studydefinitions          — Create study definition
GET    /v5/studydefinitions/{id}     — Retrieve study definition
PUT    /v5/studydefinitions/{id}     — Update study definition
GET    /v5/studydefinitions/search   — Search study definitions
```

### 7.4 CDISC Library API

For retrieving controlled terminology, biomedical concepts, and SDTM metadata:

```
Base URL: https://library.cdisc.org/api
Auth: API Key header

GET /mdr/ct/packages                          — List CT packages
GET /mdr/ct/packages/{package}/codelists      — Get codelists
GET /mdr/bc/packages/{package}/biomedicalconcepts — Get BCs
GET /mdr/sdtm/{version}/datasets              — Get SDTM datasets
```

---

## 8. EXCEL-TO-USDM INPUT FORMAT (v4.0)

When users provide study data via Excel (the preferred input for the `usdm4-excel` package), the following sheet structure applies:

### Required Sheets

| Sheet Name | Purpose |
|-----------|---------|
| **Configuration** | CT version settings (SDTMCT, PROTOCOLCT, DDFCT) |
| **Study** | Study-level metadata (title, phase, identifiers, dates) |
| **Study Design** | Arms, epochs, intervention model |
| **Encounters** | Visit definitions and timing |
| **Activities** | Activities and procedures |
| **Timelines** | Schedule timeline definitions |
| **Criteria** | Inclusion/exclusion criteria |
| **Objectives** | Objectives and linked endpoints |
| **Interventions** | Study interventions and administrations |

### Optional Sheets

| Sheet Name | Purpose |
|-----------|---------|
| **Dictionaries** | Syntax template dictionaries for parameterized text |
| **Comments** | Annotations referenceable by other sheets |
| **Organizations** | Sponsor, regulatory bodies, sites |
| **Biomedical Concepts** | BCs mapped to CDISC Library |

### Data Entry Conventions

- **CT codes**: Enter as C-Code (`C15602`), submission value (`PHASE III TRIAL`), or preferred term (`Phase III Trial`)
- **Multiple values**: Comma-separated; use quotes if a value contains a comma: `123, "123,456", 789`
- **Boolean fields**: `Y`, `YES`, `T`, `TRUE`, `1` (case-insensitive)
- **Timing values**: ISO 8601 durations (e.g., `P3W`, `P28D`, `P6M`)
- **Timing ranges**: `<lower>..<upper> <unit>` (e.g., `18..65 YEARS`)
- **Addresses**: `<lines>,district,city,state,postal_code,<country code>`
- **Templated text tags**: `<usdm:tag name="...tag_name..."/>` references dictionary entries

---

## 9. BEST PRACTICES & GUIDELINES

### When Generating USDM v4.0.0 JSON

1. **Always include `extensionAttributes: []`** on every object — this is required by the schema
2. **Always include `notes: []`** on objects that support it (most named objects)
3. **Always include `name`, `label`, `description`** on all named objects
4. **Always include `instanceType`** on every object — this reflects the UML class name
5. **Use `InterventionalStudyDesign`** (not `StudyDesign`) for the design instanceType
6. **Use linked-list ordering** (`previousId`/`nextId`) for epochs, encounters, activities, criteria — NOT `sequenceNumber`
7. **Embed endpoints in objectives** — do NOT create a separate `endpoints[]` array at the design level
8. **Use `population` (singular)** — not `populations[]` array
9. **Place `studyInterventions` and `biomedicalConcepts` at version level** — not design level
10. **Use `scopeId`** to reference organizations — not inline `studyIdentifierScope`
11. **Use cross-references (`*Id`/`*Ids`)** instead of nesting duplicate objects
12. **Validate CT codes** against the configured CT version before inclusion
13. **Preserve the hierarchy**: Study → versions → StudyVersion → studyDesigns → InterventionalStudyDesign
14. **Include the envelope**: `usdmVersion`, `systemName`, `systemVersion` at root level
15. **Use ISO 8601 durations** for timing values: `P1D` (1 day), `P3W` (3 weeks), `P6M` (6 months)

### When Digitizing Protocols

1. **Read the entire protocol** before starting extraction — context matters
2. **Map M11 sections first** — use the section mapping table (Section 4) as a checklist
3. **Flag ambiguities** — if protocol text is unclear, note it as a comment rather than guessing
4. **Preserve original text** in `text` and `description` fields — do not over-summarize
5. **Link objectives → endpoints** by embedding endpoints directly in each Objective
6. **Parse the SoA table carefully** — columns = encounters/visits, rows = activities/assessments
7. **Extract indications** with coded references (SNOMED, MedDRA, etc.)

### When Generating Documents

1. **Follow M11 Template section order** exactly — regulators expect specific ToC structure
2. **Include both synopsis and detailed sections** — the synopsis is not optional
3. **Cross-reference sections** — M11 expects internal cross-references (e.g., "See Section 6.0")
4. **Use tables for structured data** — Trial Design matrix, SoA, eligibility criteria tables

### When Generating SDTM Trial Design

1. **ARMCD must be ≤20 characters** — derive from arm name, uppercase, no spaces
2. **ETCD must be ≤8 characters** — derive from element name
3. **TAETORD must be sequential** per arm — reset numbering for each arm
4. **EPOCH values must match** between TA, TV, and SE domains
5. **Sort epochs by linked list** — use `previousId`/`nextId`, not assumed array order

---

## 10. REFERENCE LINKS

| Resource | URL |
|----------|-----|
| CDISC DDF Main Page | https://www.cdisc.org/ddf |
| DDF-RA GitHub (USDM UML, API, IG) | https://github.com/cdisc-org/DDF-RA |
| USDM Python Package (v3.x) | https://pypi.org/project/usdm/ |
| USDM v4.0 Excel Package | https://pypi.org/project/usdm4-excel/ |
| CDISC Rules Engine (CORE) | https://github.com/cdisc-org/cdisc-rules-engine |
| TransCelerate SDR API | https://github.com/transcelerate/ddf-sdr-api |
| TransCelerate DDF Home | https://transcelerate.github.io/ddf-home/ |
| CDISC Library | https://www.cdisc.org/cdisc-library |
| ICH M11 Guideline (Final, Nov 2025) | https://database.ich.org/sites/default/files/ICH_Step4_M11_Final_Guideline_2025_1119.pdf |
| ICH M11 Template | https://database.ich.org/sites/default/files/ICH_M11_Template_Updated%20Step%202_ForReferenceOnly_2025_0203.pdf |
| ICH M11 Technical Specification | https://database.ich.org/sites/default/files/ICH_M11_Technical%20Specification_Updated%20Step%202_2025_0203.pdf |
| USDM Reference Data (Sanofi example) | https://github.com/data4knowledge/usdm_data |

---

## 11. QUICK-START DECISION TREE

```
User Request
│
├── "Digitize this protocol" / "Convert protocol to USDM"
│   → Step 1: Analyze protocol text (Section 3, Step 1)
│   → Step 2: Generate USDM v4.0.0 JSON (Section 3, Step 2)
│   → Step 3: Recommend CORE validation (Section 3, Step 3)
│
├── "Generate an M11 protocol document"
│   → Requires: USDM JSON (generate first if not provided)
│   → Use Section 4 mapping + python-docx code
│   → Follow M11 Template section order strictly
│
├── "Create a DTA/DTS for [vendor type]"
│   → Use Section 5 templates
│   → Customize variable list for data type (lab, ECG, imaging, etc.)
│   → Link to USDM encounters for visit schedule
│
├── "Generate SDTM Trial Design datasets"
│   → Use Section 6 code generators
│   → Produce TA, TE, TV, TS, TI as DataFrames → export to CSV/XPT
│   → Validate ARMCD/ETCD length constraints
│
├── "Help me fill in the USDM Excel workbook"
│   → Use Section 8 sheet definitions
│   → Guide user through each sheet with CT code lookups
│
├── "Validate my USDM JSON"
│   → Structural check against Section 2.2 hierarchy
│   → CT code validation against Section 2.3
│   → Cross-reference integrity check
│   → Linked-list integrity check (previousId/nextId chains)
│   → Recommend CORE engine execution (Section 7.1)
│
└── "Explain [USDM concept / DDF component]"
    → Use Section 2 domain knowledge
    → Reference specific class relationships and CT codes
```

---

*This skill is designed for USDM v4.0.0 as of the DDF Phase 4 public review (2025). The USDM is under active development by CDISC — always verify against the latest DDF-RA GitHub repository for schema changes.*
