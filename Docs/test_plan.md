# Test Plan - SunBridge Compliance Pipeline (Task 2)

This test plan provides complete manual and automated verification scenarios to evaluate the SunBridge compliance extraction pipeline.

---

## Automated Test Suite

Run all automated unit and integration tests using `pytest`:

```powershell
pytest -v
```

All 4 test files cover:
- `tests/test_parser.py`: PyMuPDF text and table extraction.
- `tests/test_models.py`: Pydantic schema validation.
- `tests/test_conflict_detection.py`: Weight conflict preservation and verbal claim downgrade.
- `tests/test_output_validation.py`: JSON schema, source attribution, and Markdown report structure.

---

## Manual Verification Scenarios

### TEST 1: Run Pipeline from Clean Environment
- **Objective**: Ensure the pipeline executes from a fresh clone without missing dependencies.
- **Command**:
  ```powershell
  python -m sunbridge
  ```
- **Expected Outcome**: Pipeline executes 9 LangGraph nodes, generates `output/compliance.json` and `output/sunbridge_draft.md`, and prints `Pipeline Status: SUCCESS`.

### TEST 2: Run Using Provided Datasheet URL
- **Objective**: Verify live PDF download from Deye website.
- **Execution**: Run `python -m sunbridge`. Observe console logs: `Attempting to download datasheet from https://www.deyeinverter.com/deyeinverter/2023/10/07/datasheet_sun-4-12k-g06p3-eu-am2-p1_231007_en.pdf...`
- **Expected Outcome**: PDF downloads to `data/cache/datasheet_sun_4_12k.pdf`.

### TEST 3: Verify Manufacturer Legal Name
- **Objective**: Confirm manufacturer name comes from extracted document content.
- **Verification**: Inspect `output/compliance.json` -> `manufacturer_identity` -> `legal_name`.
- **Expected Value**: `Ningbo Deye Inverter Technology Co., Ltd.`.

### TEST 4: Verify Model Identification
- **Objective**: Confirm exact model variant identification.
- **Verification**: Inspect `output/compliance.json` -> `product_identity` -> `model`.
- **Expected Value**: `SUN-5K-G06P3-EU-AM2-P1`.

### TEST 5: Verify Ingress Protection Rating
- **Objective**: Confirm IP65 extraction from datasheet.
- **Verification**: Inspect `output/compliance.json` -> `electrical_specifications` -> `ingress_protection`.
- **Expected Value**: `IP65`.

### TEST 6: Weight Conflict Preservation
- **Objective**: Verify installer estimate (18 kg) does NOT overwrite datasheet spec (11 kg).
- **Verification**: Inspect `output/compliance.json` -> `conflicts`.
- **Expected Outcome**: Field `weight` has status `CONFLICT`, preserving both `11 kg` (`source_1`) and `approximately 18 kg` (`source_3`). Resolution set to `PENDING_FROM_MANUFACTURER`.

### TEST 7: Verbal SGS Claim Downgrade
- **Objective**: Verify verbal SGS claim is marked pending rather than certified.
- **Verification**: Inspect `output/compliance.json` -> `pending_items` and `testing_and_standards`.
- **Expected Outcome**: Status set to `PENDING_FROM_MANUFACTURER` with note stating "SGS was mentioned verbally in call notes, but no certificate or report was provided."

### TEST 8: Missing Label Photo Status
- **Objective**: Verify missing physical label photo is marked pending.
- **Verification**: Inspect `output/compliance.json` -> `labeling` -> `missing_fields`.
- **Expected Outcome**: Includes "Actual product label / rating plate photograph".

### TEST 9: Source Attribution Integrity
- **Objective**: Confirm all evidence facts contain source attribution.
- **Verification**: Inspect `output/compliance.json` -> `all_evidence`.
- **Expected Outcome**: Every evidence item contains valid `source_id` (`source_1`, `source_2`, or `source_3`) and `source_type`.

### TEST 10: Final Markdown Draft Generation
- **Objective**: Verify dynamic Markdown generation matching 12-section layout.
- **Verification**: Open `output/sunbridge_draft.md`.
- **Expected Outcome**: Contains all 12 required sections starting with `# SunBridge Trading` and `## Preliminary Import Compliance Draft`.

### TEST 11: Offline / Network Interruption Behavior
- **Objective**: Verify fallback when network is unavailable.
- **Execution**: Disconnect internet or set invalid URL in `config.py` and run `python -m sunbridge`.
- **Expected Outcome**: Downloader logs warning and falls back cleanly to local cached copy or `Docs/src1_task2.pdf`.

### TEST 12: Dynamic Extraction Verification
- **Objective**: Ensure extraction logic operates on document text rather than hardcoded static answers.
- **Verification**: Inspect `src/sunbridge/parsing/pdf_parser.py` and `src/sunbridge/extraction/extractor.py`.
- **Expected Outcome**: Fields are extracted dynamically from PyMuPDF page text and table rows.
