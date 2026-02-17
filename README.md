# USDM Study Digitization Architect

Welcome to the official repository for the **USDM Study Digitization Architect** skill. This toolkit is designed to facilitate the transition from document-centric clinical trial protocols to data-centric, machine-readable study definitions using the **CDISC Unified Study Definitions Model (USDM) v4.0**.

## 🎯 Purpose

The goal of this repository is to provide a standardized environment for digitizing clinical protocols and automating the generation of downstream clinical assets in the **Digital Data Flow (DDF)** ecosystem.

## 🏗️ Core Architecture

This repository supports the **Reference Architecture (RA)** developed by CDISC in collaboration with TransCelerate BioPharma.

### **The "Prompt-to-Protocol" Workflow**

1. **Analyze**: Extract clinical metadata from unstructured sources (PDF/Word).
2. **Model**: Map elements to **USDM v4.0** classes (e.g., StudyDesign, SoA, EligibilityCriteria).
3. **Generate**: Produce valid JSON for exchange with a **Study Definitions Repository (SDR)**.
4. **Validate**: Verify conformance using the **CDISC Open Rules Engine (CORE)**.

## 📦 Repository Structure

* 
`/templates`: Standardized formats for **ICH M11** documents, **Data Transfer Agreements (DTA)**, and **DTS** content specifications.


* 
`/scripts`: Python-based generators for **SDTM Trial Design** domains (TA, TE, TV, TI, TS).


* 
`/examples`: Test data based on the **LZZT pilot study** and other complex study designs.


* `/docs`: Guidance on **CDISC Controlled Terminology** and relationship definitions.

## 🛠️ Tool Integration

* 
**CORE Engine**: For structural and semantic validation.


* 
**USDM Toolkit**: Integration with **Excel-to-JSON** and **PDF-to-HTML** scraping utilities.


* 
**CDISC Library**: The authoritative source for standard identifiers and Biomedical Concepts (BCs).



## 🚦 Quick Start

To begin a digitization task, provide the protocol text and use the following command structure:

> "Analyze this protocol and generate a **USDM v4.0 JSON** compliant with **API V5** requirements."

