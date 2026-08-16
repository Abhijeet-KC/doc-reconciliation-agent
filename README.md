# SunBridge Import Compliance Extraction Pipeline (Task 2)
### Cantordust Analytics AI Engineer Assessment — Trainee / Junior Track

An evidence-aware, autonomous document extraction and compliance draft generation pipeline built with Python, PyMuPDF, LangGraph, Pydantic, and OpenAI API compatibility.

---

## 1. Project Overview
This project implements **Task 2 (China → Bangladesh)** of the Cantordust AI Engineer Assessment. The pipeline ingests multi-source data (manufacturer datasheet PDF, buyer purchase form, and phone call notes) for solar inverters, extracts technical specifications, attributes provenance to every claim, reconciles multi-source conflicts without silent overwrites, flags pending documentary items, and generates both structured machine-readable output (`output/compliance.json`) and a human-readable compliance draft (`output/sunbridge_draft.md`).

---

## 2. Why Task 2 Was Chosen
Task 2 addresses a real-world international trade compliance challenge: reconciling technical specifications from a foreign manufacturer datasheet against buyer requirements and unverified verbal claims. Task 2 was chosen because it highlights the necessity of strict evidence attribution—distinguishing verified documentary proof from verbal phone claims and highlighting critical discrepancies (such as product net weight) before customs clearance.

---

## 3. Architecture
The pipeline is orchestrated as a 9-node state machine using **LangGraph**:

```
[START]
   ↓
[FETCH_SOURCES] ────────► Ingests Source Definitions & Downloads Datasheet PDF
   ↓
[PARSE_DOCUMENTS] ──────► PyMuPDF fitz parses PDF pages & tables; normalizes text sources
   ↓
[EXTRACT_CANDIDATE_FIELDS] ► OpenAI structured LLM / rule-based extraction
   ↓
[NORMALIZE_FIELDS] ────► Standardizes units (kW/W, kg) & field names
   ↓
[VALIDATE_AND_COMPARE_SOURCES] ► Reconciles evidence across sources
   ↓
[CLASSIFY_EVIDENCE] ───► Tags status (VERIFIED, SOURCE_REPORTED, CONFLICT, PENDING)
   ↓
[GENERATE_STRUCTURED_OUTPUT] ► Validates & writes output/compliance.json
   ↓
[GENERATE_HUMAN_DRAFT] ─► Renders 12-section output/sunbridge_draft.md
   ↓
[VALIDATE_OUTPUT] ─────► Runs security secret scan & schema assertions
   ↓
 [END]
```

---

## 4. Project Structure
```
cantordust-task2/
│
├── README.md                           # Main documentation & assessment report
├── .gitignore                          # Git exclusion rules
├── .env.example                        # Environment variable template
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Project metadata & build settings
│
├── src/
│   └── sunbridge/
│       ├── __init__.py
│       ├── main.py                     # CLI pipeline runner
│       ├── config.py                   # Configuration & setting paths
│       │
│       ├── graph/
│       │   ├── __init__.py
│       │   ├── workflow.py             # LangGraph state graph definition
│       │   └── state.py                # PipelineState TypedDict definition
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── downloader.py           # HTTP downloader with caching/fallback
│       │   └── sources.py              # Source 1, 2, 3 definitions
│       │
│       ├── parsing/
│       │   ├── __init__.py
│       │   ├── pdf_parser.py           # PyMuPDF fitz text & table parser
│       │   └── models.py               # DocumentData, PageData, TableData
│       │
│       ├── extraction/
│       │   ├── __init__.py
│       │   ├── extractor.py            # Structured LLM + fallback extractor
│       │   └── prompts.py              # Zero-hallucination extraction prompts
│       │
│       ├── validation/
│       │   ├── __init__.py
│       │   ├── conflicts.py            # Evidence reconciliation & conflict engine
│       │   └── validators.py           # Output integrity & security validators
│       │
│       ├── reporting/
│       │   ├── __init__.py
│       │   └── renderer.py             # Markdown report renderer
│       │
│       └── schemas/
│           ├── __init__.py
│           └── compliance.py           # Pydantic schemas (EvidenceRecord, etc.)
│
├── data/
│   ├── raw/                            # Raw data directory
│   ├── cache/                          # Cached PDF downloads
│   └── input/                          # User input files
│
├── output/                             # Generated compliance JSON & Markdown draft
│
├── tests/
│   ├── test_parser.py
│   ├── test_models.py
│   ├── test_conflict_detection.py
│   └── test_output_validation.py
│
└── docs/
    ├── test_plan.md                    # Detailed manual & automated test scenarios
    └── features/                       # Incremental feature documentation
        ├── feat1.md
        ├── feat2.md
        ├── feat3.md
        ├── feat4.md
        ├── feat5.md
        ├── feat6.md
        ├── feat7.md
        └── feat8.md
```

---

## 5. Installation
Clone the repository and install requirements in Python 3.10+:

```powershell
# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

---

## 6. Environment Variables
The application uses the following environment variables:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `LLM_BASE_URL` | OpenAI-compatible API base URL | `https://api.openai.com/v1` |
| `LLM_API_KEY` | API Key for LLM provider | `""` (Triggers deterministic rule fallback) |
| `LLM_MODEL` | LLM Model Name | `gpt-4o-mini` |
| `LLM_TEMPERATURE` | Generation temperature | `0.0` |

---

## 7. .env Setup
To configure your API credentials:

```powershell
cp .env.example .env
```

Open `.env` and enter your API credentials:

```ini
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your_actual_api_key_here
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0
```

---

## 8. Running the Pipeline
Run the complete end-to-end pipeline with:

```powershell
python -m sunbridge
```

Console Output Example:
```
==================================================
      SUNBRIDGE COMPLIANCE PIPELINE SUMMARY      
==================================================
Sources processed:    3
Fields extracted:     21
Conflicts detected:   1
Pending items:        5
Draft generated:      e:\doc-reconciliation-agent\output\sunbridge_draft.md
Structured output:    e:\doc-reconciliation-agent\output\compliance.json
Pipeline Status:      SUCCESS
==================================================
```

---

## 9. Running Tests
Run all unit and integration tests using `pytest`:

```powershell
pytest -v
```

---

## 10. Input Sources
- **Source 1 (Manufacturer Datasheet)**: PDF downloaded from Deye website (`SUN-4-12K-G06P3-EU-AM2-P1`). High evidence weight (`VERIFIED`).
- **Source 2 (Buyer Purchase Inquiry Form)**: Ref `INT-2024-8841`, SunBridge Trading Pvt. Ltd., Bangladesh, requesting model `SUN-5K-G06P3-EU-AM2-P1` ("5000 W", rooftop). Status: `SOURCE_REPORTED`.
- **Source 3 (Call Notes from Ramesh)**: Verbal phone notes (IP65, installer guessed ~18 kg weight, verbal SGS mention, "high 90s efficiency"). Status: `SOURCE_REPORTED` (verbal downgrade).

---

## 11. Extraction Approach
The extraction stage parses raw document text and tabular cells using PyMuPDF `fitz`. Text chunks are passed to the extraction node. If an OpenAI-compatible API key is present, the pipeline invokes Pydantic structured output completion. If no API key is provided, the pipeline executes a deterministic rule-based extractor that scans exact page text blocks. Both paths yield uniform `EvidenceRecord` instances.

---

## 12. Why PyMuPDF Was Chosen
PyMuPDF (`fitz`) was chosen because:
1. Extremely fast PDF page text extraction (C-backed bindings).
2. Built-in table detection (`page.find_tables()`) introduced in 1.23.0+.
3. Preserves exact page numbers without requiring external heavy Java/OCR dependencies.

---

## 13. Table/Layout Limitations
Multi-column spec tables in datasheets often lack explicit cell borders, which can lead table parsers to merge adjacent column cells or misalign model headers. The pipeline mitigates this by extracting page text alongside tables and assigning lower confidence scores (0.7) to layout-sensitive fields.

---

## 14. LLM / API Design
The pipeline uses an OpenAI API-compatible client configured via environment variables. By using `LLM_BASE_URL` and `LLM_MODEL`, any OpenAI-compatible API (OpenAI, Qwen, DeepSeek, vLLM, Ollama) can be substituted seamlessly without changing source code.

---

## 15. Evidence & Provenance Design
Every extracted fact is encapsulated in an `EvidenceRecord`:
- `field_name`: Canonical identifier
- `normalized_value`: Standardized value
- `raw_value`: Exact string as written in source
- `source_id`: `source_1`, `source_2`, or `source_3`
- `source_type`: `manufacturer_datasheet`, `buyer_form`, or `call_notes`
- `confidence`: Floating-point score (0.0 – 1.0)
- `status`: `VERIFIED`, `SOURCE_REPORTED`, `CONFLICT`, `PENDING_FROM_MANUFACTURER`

---

## 16. Conflict-Handling Strategy
When sources disagree (e.g. Weight: 11 kg in datasheet vs ~18 kg in call notes):
1. Both values are preserved in `ConflictRecord.conflicting_evidence`.
2. Neither value silently overwrites the other.
3. The field status is set to `CONFLICT`.
4. Resolution is assigned as `PENDING_FROM_MANUFACTURER`.
5. An explicit item is added to "Pending from Manufacturer" and a question is generated for the manufacturer.

---

## 17. Hallucination Prevention
1. **Verbal Claim Downgrade**: Phone claims (e.g. SGS mentioned on call) are classified as `SOURCE_REPORTED` and flagged as `PENDING_FROM_MANUFACTURER` due to lack of attached physical certificates.
2. **Missing Label Photos**: Identified as missing rather than assuming compliance.
3. **No Invented Certificates**: Unattached test reports are marked pending.

---

## 18. Assumptions
1. Target delivery location is Bangladesh as stated in Buyer Form INT-2024-8841.
2. Datasheet for `SUN-4-12K-G06P3-EU-AM2-P1` covers model series containing `SUN-5K-G06P3-EU-AM2-P1`.
3. Installer weight statement (~18 kg) was an unverified phone estimate.

---

## 19. Known Limitations
1. Does not perform OCR on scanned PDF image pages (assumes vector PDF text).
2. Does not consult national customs regulatory APIs directly (out of scope).

---

## 20. What I Would Improve With More Time
1. Add visual table bounding-box rendering over PDF pages.
2. Implement automated PDF label photo image classification.
3. Add a web-based diff viewer comparing candidate extractions across datasheet revisions.

---

## 21. Example Output

### Structured JSON Snippet (`output/compliance.json`)
```json
{
  "product_identity": {
    "model": "SUN-5K-G06P3-EU-AM2-P1",
    "order_reference": "INT-2024-8841",
    "destination": "Bangladesh"
  },
  "conflicts": [
    {
      "field_name": "weight",
      "resolution": "PENDING_FROM_MANUFACTURER",
      "notes": "Datasheet specifies 11 kg net weight, whereas call notes record an installer estimate of approximately 18 kg."
    }
  ]
}
```

### Markdown Draft Snippet (`output/sunbridge_draft.md`)
```markdown
# SunBridge Trading
## Preliminary Import Compliance Draft

### 1. Executive Summary
This preliminary compliance review evaluates the proposed import of SUN-5K-G06P3-EU-AM2-P1 solar inverters...
```

---

## 22. Git Workflow & Feature Progression
The project was built incrementally across 8 tracked features:
- `feat1`: Bootstrap project and configuration (`docs/features/feat1.md`)
- `feat2`: Source ingestion and PDF downloader (`docs/features/feat2.md`)
- `feat3`: PDF parsing and document normalization (`docs/features/feat3.md`)
- `feat4`: Structured LLM extraction & Pydantic schemas (`docs/features/feat4.md`)
- `feat5`: Evidence attribution and conflict detection (`docs/features/feat5.md`)
- `feat6`: Generated compliance JSON (`docs/features/feat6.md`)
- `feat7`: Generated SunBridge draft (`docs/features/feat7.md`)
- `feat8`: Pipeline validation and test plan (`docs/features/feat8.md`)

---

## Assessment Walkthrough & Demo Script (3–8 Minutes)

### 1. Problem Statement (1 min)
"SunBridge Trading is importing solar inverters from Deye in China to Bangladesh. We have three contradictory sources: an official manufacturer datasheet, a buyer form, and verbal call notes. The core challenge is verifying compliance without inventing facts or silently resolving conflicts."

### 2. Architecture & Provenance (1.5 min)
"We built an evidence-aware extraction pipeline using LangGraph, PyMuPDF, and Pydantic. Every extracted specification maintains source provenance—attributing whether a value came from the datasheet (`VERIFIED`), buyer form (`SOURCE_REPORTED`), or phone call notes."

### 3. Conflict & Uncertainty Demonstration (2 min)
"Notice how our conflict engine handles weight: the datasheet specifies 11 kg, but the call notes mention ~18 kg from an installer guess. The pipeline does NOT silently choose 11 kg. It creates a `CONFLICT` record, preserves both evidence values, marks the status `PENDING_FROM_MANUFACTURER`, and generates a concrete question for the factory. Similarly, the verbal SGS claim is downgraded to pending because no physical certificate was attached."

### 4. Output Generation & Limitations (1.5 min)
"Running `python -m sunbridge` executes our 9-node pipeline and generates both `output/compliance.json` for ERP integration and `output/sunbridge_draft.md` for internal circulation. With more time, we would add visual PDF table layout rendering and automated label photo inspection."