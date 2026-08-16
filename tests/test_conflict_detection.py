import pytest
from sunbridge.ingestion.sources import get_all_sources
from sunbridge.parsing import parse_source
from sunbridge.extraction import extract_evidence_from_document
from sunbridge.validation import reconcile_evidence
from sunbridge.schemas.compliance import EvidenceStatus
from sunbridge.config import DOCS_FALLBACK_DIR

def test_weight_conflict_preservation():
    sources = get_all_sources("http://example.com/dummy.pdf")
    fallback_pdf = DOCS_FALLBACK_DIR / "src1_task2.pdf"
    
    docs = [parse_source(s, fallback_pdf) for s in sources]
    all_evidence = [r for d in docs for r in extract_evidence_from_document(d)]
    
    comp_rec = reconcile_evidence(all_evidence)
    
    # Weight conflict assertion
    assert len(comp_rec.conflicts) >= 1
    weight_conf = next((c for c in comp_rec.conflicts if c.field_name == "weight"), None)
    assert weight_conf is not None, "Weight conflict was not detected"
    assert len(weight_conf.conflicting_evidence) >= 2
    
    # Assert 11 kg and 18 kg are both preserved in evidence records
    vals = [e.raw_value for e in weight_conf.conflicting_evidence]
    assert any("11" in v for v in vals), "11 kg datasheet value missing from conflict"
    assert any("18" in v for v in vals), "18 kg call note value missing from conflict"

def test_sgs_verbal_claim_not_certified():
    sources = get_all_sources("http://example.com/dummy.pdf")
    fallback_pdf = DOCS_FALLBACK_DIR / "src1_task2.pdf"
    
    docs = [parse_source(s, fallback_pdf) for s in sources]
    all_evidence = [r for d in docs for r in extract_evidence_from_document(d)]
    
    comp_rec = reconcile_evidence(all_evidence)
    
    # Verify SGS is flagged in pending items and NOT marked as certified
    assert any("SGS" in p for p in comp_rec.pending_items)
    sgs_status = comp_rec.testing_and_standards.get("sgs_status", "")
    assert "PENDING_FROM_MANUFACTURER" in sgs_status
    assert "no certificate or report was provided" in sgs_status.lower() or "verbal" in sgs_status.lower()
