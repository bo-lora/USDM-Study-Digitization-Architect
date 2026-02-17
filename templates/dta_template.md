# Data Transfer Agreement (DTA) Template

**Between:** [Sponsor Name] ("Sponsor")  
**And:** [Vendor Name] ("Vendor")  
**Study:** [Protocol Number]  
**Data Type:** [Central Lab / ECG / Imaging / PK / Biomarker / ePRO]  
**Effective Date:** [Date]  

---

## 1. Purpose and Scope

This Data Transfer Agreement defines the operational requirements for the electronic transfer of [data type] data between [Vendor Name] and [Sponsor Name] for clinical study [Protocol Number].

**Data covered by this agreement:**
- [ ] Central Laboratory Data
- [ ] ECG/Cardiac Safety Data
- [ ] Medical Imaging Data
- [ ] Pharmacokinetic/Bioanalytical Data
- [ ] Biomarker/Genomic Data
- [ ] ePRO/eCOA Data
- [ ] RTSM/IRT Data

---

## 2. Roles and Responsibilities

| Role | Organization | Contact | Email |
|------|-------------|---------|-------|
| Sponsor Data Manager | [Sponsor] | [Name] | [Email] |
| Sponsor Biostatistician | [Sponsor] | [Name] | [Email] |
| Vendor Technical Lead | [Vendor] | [Name] | [Email] |
| Vendor Project Manager | [Vendor] | [Name] | [Email] |
| CRO Data Manager | [CRO, if applicable] | [Name] | [Email] |

---

## 3. Data Description

### 3.1 Datasets

| Dataset | Description | Domain Alignment | Variables | Est. Records/Transfer |
|---------|-------------|-----------------|-----------|----------------------|
| [Dataset 1] | [Description] | [SDTM domain] | See DTS | [Count] |
| [Dataset 2] | [Description] | [SDTM domain] | See DTS | [Count] |

### 3.2 Reference Data

| Reference File | Description | Provided By | Frequency |
|---------------|-------------|-------------|-----------|
| Site List | Active sites and identifiers | Sponsor | As updated |
| Visit Schedule | Expected visits from protocol SoA | Sponsor | At study start |
| Subject List | Randomized subjects | Sponsor/RTSM | As updated |

---

## 4. Transfer Schedule

| Transfer Type | Frequency | Day/Time (UTC) | Window |
|--------------|-----------|----------------|--------|
| Production (Incremental) | [Daily/Weekly/Bi-weekly] | [Day] [Time] | ±[hours] |
| Production (Cumulative) | [Weekly/Monthly] | [Day] [Time] | ±[hours] |
| Reconciliation | [Monthly/Quarterly] | [Day] [Time] | N/A |
| Ad hoc (on request) | As needed | Within [X] business days | N/A |

**Trigger Events:**
- Database lock: Final cumulative transfer within [X] business days
- Unblinding: Transfer per sponsor instruction
- Safety event: Ad hoc transfer within [X] hours

---

## 5. Transfer Method

| Parameter | Specification |
|-----------|--------------|
| **Protocol** | SFTP / HTTPS API / Secure Portal |
| **Server** | [hostname:port] |
| **Directory** | /[study]/[data_type]/[direction]/ |
| **Authentication** | SSH key / Certificate / OAuth 2.0 |
| **Encryption** | AES-256 in transit, at rest |
| **IP Allowlist** | [Sponsor IPs], [Vendor IPs] |

---

## 6. File Naming Convention

```
{StudyID}_{DataType}_{SiteID}_{YYYYMMDD}_{Seq}.{ext}
```

| Component | Description | Example |
|-----------|-------------|---------|
| StudyID | Protocol number (no special chars) | XYZONCO2025001 |
| DataType | Data category code | LAB, ECG, IMG |
| SiteID | Site identifier (ALL for cumulative) | S0101, ALL |
| YYYYMMDD | Transfer date | 20250715 |
| Seq | Sequence number (2 digits) | 01 |
| ext | File extension | csv, sas7bdat, json |

**Example:** `XYZONCO2025001_LAB_ALL_20250715_01.csv`

---

## 7. Data Specifications

Detailed variable-level specifications are defined in the companion Data Transfer Specification (DTS) document.

**DTS Document Reference:** [DTS filename and version]

---

## 8. Reconciliation Process

| Parameter | Specification |
|-----------|--------------|
| **Frequency** | [Monthly / Quarterly] |
| **Method** | Subject count + sample count comparison |
| **Metrics** | Subjects transferred, samples received vs. transferred, missing data |
| **Discrepancy Threshold** | > [X]% triggers investigation |
| **Escalation** | Vendor PM → Sponsor DM within [X] business days |

---

## 9. Issue Management

| Issue Type | Response Time | Resolution Time | Escalation Path |
|-----------|--------------|-----------------|-----------------|
| Transfer failure | [X] hours | [X] business days | Vendor Tech → Sponsor DM |
| Data quality query | [X] business days | [X] business days | Sponsor DM → Vendor PM |
| Missing data | [X] business days | [X] business days | Sponsor DM → Vendor PM |
| Specification change | N/A | Per change control | Both parties agree |

---

## 10. Confidentiality and Compliance

- All data transfers comply with **21 CFR Part 11** (electronic records/signatures)
- Personal data handling per **GDPR** (EU) / applicable regional privacy laws
- Data retention: [X] years after study completion per sponsor policy
- Vendor will not share study data with any third party without written sponsor consent
- Audit trail maintained for all transfers

---

## Signatures

| | Sponsor | Vendor |
|--|---------|--------|
| **Name** | | |
| **Title** | | |
| **Date** | | |
| **Signature** | | |

---

*Template version: 1.0 | Aligned with USDM v4.0 study definitions*
