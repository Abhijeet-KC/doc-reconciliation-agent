import pytest
import json
from sunbridge.ingestion.sources import get_all_sources
from sunbridge.parsing import parse_source
from sunbridge.extraction import extract_evidence_from_document
from sunbridge.validation import reconcile_evidence, validate_compliance_record, serialize_compliance_json
from sunbridge.reporting import render_sunbridge_draft
from sunbridge.config import DOCS_FALLBACK_DIR

def test_full_pipeline_output_validation():
    sources = get_all_sources("http://example.com/dummy.pdf")
    fallback_pdf = DOCS_FALLBACK_DIR / "src1_task2.pdf"
    
    docs = [parse_source(s, fallback_pdf) for s in sources]
    all_evidence = [r for d in docs for r in extract_evidence_from_document(d)]
    comp_rec = reconcile_evidence(all_evidence)
    
    # 1. Validate compliance record & semantic guardrails
    assert validate_compliance_record(comp_rec) is True
    
    # 2. Validate JSON structure
    json_str = serialize_compliance_json(comp_rec)
    data = json.loads(json_str)
    assert "product_identity" in data
    assert "conflicts" in data
    assert "pending_items" in data
    assert "questions_for_manufacturer" in data
    
    # 3. Validate Markdown structure and zero overclaiming
    md = render_sunbridge_draft(comp_rec)
    md_lower = md.lower()
    
    assert "# SunBridge Trading" in md
    assert "## Preliminary Import Compliance Draft" in md
    assert "### 1. Executive Summary" in md
    assert "### 6. Labeling" in md
    assert "### 8. Conflicts / Uncertainty" in md
    assert "### 9. Pending from Manufacturer" in md
    assert "### 10. Questions for Manufacturer" in md
    
    # Semantic Guardrail Assertions on rendered Markdown
    assert "destination port" not in md_lower
    assert "sgs certified" not in md_lower
    assert "country of origin: china (verified)" not in md_lower
    assert "physical label verification" in md_lower
