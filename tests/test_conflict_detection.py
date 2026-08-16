import pytest
from sunbridge.validation import reconcile_evidence

def test_weight_conflict_preservation(sample_evidence_records):
    comp_rec = reconcile_evidence(sample_evidence_records)
    
    assert len(comp_rec.conflicts) >= 1
    weight_conf = next((c for c in comp_rec.conflicts if c.field_name == "weight"), None)
    assert weight_conf is not None, "Weight conflict was not detected"
    assert len(weight_conf.conflicting_evidence) >= 2
    
    vals = [e.raw_value for e in weight_conf.conflicting_evidence]
    assert any("11" in v for v in vals), "11 kg datasheet value missing from conflict"
    assert any("18" in v for v in vals), "18 kg call note value missing from conflict"

def test_sgs_verbal_claim_not_certified(sample_evidence_records):
    comp_rec = reconcile_evidence(sample_evidence_records)
    
    assert any("SGS" in p for p in comp_rec.pending_items)
    sgs_status = comp_rec.testing_and_standards.get("sgs_status", "")
    assert "PENDING_FROM_MANUFACTURER" in sgs_status
    assert "no certificate or report was provided" in sgs_status.lower() or "verbal" in sgs_status.lower()

def test_model_suffix_mismatch_preserved(sample_evidence_records):
    comp_rec = reconcile_evidence(sample_evidence_records)
    prod = comp_rec.product_identity
    
    assert prod["target_model_variant"] == "SUN-5K-G06P3-EU-AM2-P1"
    assert prod["call_notes_model"] == "SUN-5K-G06P3"
    assert prod["variant_confirmation_status"] == "PENDING_FROM_MANUFACTURER"

def test_country_of_origin_not_overstated(sample_evidence_records):
    comp_rec = reconcile_evidence(sample_evidence_records)
    mfr = comp_rec.manufacturer_identity
    
    assert "China" in mfr["manufacturer_location"]
    assert "formal customs origin documentation was not supplied" in mfr["country_of_origin_status"].lower()

def test_standards_not_certification(sample_evidence_records):
    comp_rec = reconcile_evidence(sample_evidence_records)
    testing = comp_rec.testing_and_standards
    
    assert "test reports/certificates not supplied" in testing["datasheet_cited_standards"].lower()

def test_physical_label_pending_without_photo(sample_evidence_records):
    comp_rec = reconcile_evidence(sample_evidence_records)
    labeling = comp_rec.labeling
    
    phys = labeling.get("physical_label_verification", {})
    assert phys.get("status") == "PENDING_FROM_MANUFACTURER"
    assert "no physical product label" in phys.get("reason", "").lower()

def test_destination_is_not_port(sample_evidence_records):
    comp_rec = reconcile_evidence(sample_evidence_records)
    imp = comp_rec.importer_paperwork
    
    assert imp.get("import_destination") == "Bangladesh"
    assert "port" not in imp
