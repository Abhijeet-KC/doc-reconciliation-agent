import pytest
from sunbridge.schemas.compliance import (
    EvidenceRecord,
    EvidenceStatus,
    ConflictRecord,
    ComplianceRecord
)
from sunbridge.ingestion.sources import SourceType

def test_evidence_record_validation():
    rec = EvidenceRecord(
        field_name="ip_rating",
        normalized_value="IP65",
        raw_value="IP65",
        source_id="source_1",
        source_type=SourceType.MANUFACTURER_DATASHEET,
        confidence=0.99,
        status=EvidenceStatus.VERIFIED
    )
    assert rec.field_name == "ip_rating"
    assert rec.status == EvidenceStatus.VERIFIED
    assert rec.confidence == 0.99

def test_conflict_record_creation():
    ev1 = EvidenceRecord(
        field_name="weight",
        normalized_value="11",
        raw_value="11 kg",
        source_id="source_1",
        source_type=SourceType.MANUFACTURER_DATASHEET,
        status=EvidenceStatus.CONFLICT
    )
    ev2 = EvidenceRecord(
        field_name="weight",
        normalized_value="18",
        raw_value="18 kg",
        source_id="source_3",
        source_type=SourceType.CALL_NOTES,
        status=EvidenceStatus.CONFLICT
    )
    conf = ConflictRecord(
        field_name="weight",
        conflicting_evidence=[ev1, ev2],
        resolution="PENDING_FROM_MANUFACTURER"
    )
    assert conf.field_name == "weight"
    assert len(conf.conflicting_evidence) == 2
    assert conf.resolution == "PENDING_FROM_MANUFACTURER"
