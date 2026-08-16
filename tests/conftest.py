import pytest
from sunbridge.schemas.compliance import EvidenceRecord, EvidenceStatus, ComplianceRecord
from sunbridge.ingestion.sources import SourceType
from sunbridge.validation.conflicts import reconcile_evidence

@pytest.fixture
def sample_evidence_records() -> list[EvidenceRecord]:
    """
    Returns deterministic, multi-source EvidenceRecord objects using production schemas.
    Does NOT invoke any network or LLM extraction.
    """
    return [
        # Source 1: Manufacturer Datasheet (VERIFIED)
        EvidenceRecord(
            field_name="manufacturer_name",
            normalized_value="Ningbo Deye Inverter Technology Co., Ltd.",
            raw_value="Ningbo Deye Inverter Technology Co., Ltd.",
            source_id="source_1",
            source_type=SourceType.MANUFACTURER_DATASHEET,
            confidence=0.99,
            status=EvidenceStatus.VERIFIED
        ),
        EvidenceRecord(
            field_name="country_of_origin",
            normalized_value="China",
            raw_value="China",
            source_id="source_1",
            source_type=SourceType.MANUFACTURER_DATASHEET,
            confidence=0.95,
            status=EvidenceStatus.VERIFIED
        ),
        EvidenceRecord(
            field_name="model_name",
            normalized_value="SUN-5K-G06P3-EU-AM2-P1",
            raw_value="SUN-5K-G06P3-EU-AM2-P1",
            source_id="source_1",
            source_type=SourceType.MANUFACTURER_DATASHEET,
            confidence=0.99,
            status=EvidenceStatus.VERIFIED
        ),
        EvidenceRecord(
            field_name="rated_output_power",
            normalized_value="5000",
            raw_value="5 kW / 5000 W",
            unit="W",
            source_id="source_1",
            source_type=SourceType.MANUFACTURER_DATASHEET,
            confidence=0.98,
            status=EvidenceStatus.VERIFIED
        ),
        EvidenceRecord(
            field_name="ip_rating",
            normalized_value="IP65",
            raw_value="IP65",
            source_id="source_1",
            source_type=SourceType.MANUFACTURER_DATASHEET,
            confidence=0.99,
            status=EvidenceStatus.VERIFIED
        ),
        EvidenceRecord(
            field_name="weight",
            normalized_value="11",
            raw_value="11 kg",
            unit="kg",
            source_id="source_1",
            source_type=SourceType.MANUFACTURER_DATASHEET,
            confidence=0.95,
            status=EvidenceStatus.VERIFIED
        ),
        EvidenceRecord(
            field_name="max_efficiency",
            normalized_value="97.5%",
            raw_value="97.5%",
            unit="%",
            source_id="source_1",
            source_type=SourceType.MANUFACTURER_DATASHEET,
            confidence=0.95,
            status=EvidenceStatus.VERIFIED
        ),
        EvidenceRecord(
            field_name="safety_standards",
            normalized_value="IEC/EN 62109-1/-2, IEC/EN 61000-6-1/-2/-3/-4",
            raw_value="IEC/EN 62109-1/-2, IEC/EN 61000-6-1/-2/-3/-4",
            source_id="source_1",
            source_type=SourceType.MANUFACTURER_DATASHEET,
            confidence=0.95,
            status=EvidenceStatus.VERIFIED
        ),

        # Source 2: Buyer Form (SOURCE_REPORTED)
        EvidenceRecord(
            field_name="buyer_name",
            normalized_value="SunBridge Trading Pvt. Ltd.",
            raw_value="SunBridge Trading Pvt. Ltd.",
            source_id="source_2",
            source_type=SourceType.BUYER_FORM,
            confidence=1.0,
            status=EvidenceStatus.SOURCE_REPORTED
        ),
        EvidenceRecord(
            field_name="destination_country",
            normalized_value="Bangladesh",
            raw_value="Bangladesh",
            source_id="source_2",
            source_type=SourceType.BUYER_FORM,
            confidence=1.0,
            status=EvidenceStatus.SOURCE_REPORTED
        ),
        EvidenceRecord(
            field_name="model_name",
            normalized_value="SUN-5K-G06P3-EU-AM2-P1",
            raw_value="SUN-5K-G06P3-EU-AM2-P1",
            source_id="source_2",
            source_type=SourceType.BUYER_FORM,
            confidence=1.0,
            status=EvidenceStatus.SOURCE_REPORTED
        ),

        # Source 3: Call Notes (SOURCE_REPORTED)
        EvidenceRecord(
            field_name="model_name",
            normalized_value="SUN-5K-G06P3",
            raw_value="SUN-5K-G06P3",
            source_id="source_3",
            source_type=SourceType.CALL_NOTES,
            confidence=0.8,
            status=EvidenceStatus.SOURCE_REPORTED,
            notes="Verbal model claim"
        ),
        EvidenceRecord(
            field_name="weight",
            normalized_value="18",
            raw_value="maybe 18 kg? Installer guessed",
            unit="kg",
            source_id="source_3",
            source_type=SourceType.CALL_NOTES,
            confidence=0.4,
            status=EvidenceStatus.SOURCE_REPORTED,
            notes="Uncertain verbal installer guess"
        ),
        EvidenceRecord(
            field_name="sgs_testing_claim",
            normalized_value="Mentioned SGS on phone - nothing in writing",
            raw_value="Mentioned SGS on the phone — nothing in writing",
            source_id="source_3",
            source_type=SourceType.CALL_NOTES,
            confidence=0.3,
            status=EvidenceStatus.SOURCE_REPORTED,
            notes="Verbal mention only; no document attached"
        ),
        EvidenceRecord(
            field_name="efficiency_claim",
            normalized_value="high 90s efficiency",
            raw_value="high 90s efficiency",
            source_id="source_3",
            source_type=SourceType.CALL_NOTES,
            confidence=0.5,
            status=EvidenceStatus.SOURCE_REPORTED
        ),
        EvidenceRecord(
            field_name="label_photo",
            normalized_value="Missing",
            raw_value="No label photo yet",
            source_id="source_3",
            source_type=SourceType.CALL_NOTES,
            confidence=1.0,
            status=EvidenceStatus.SOURCE_REPORTED
        )
    ]

@pytest.fixture
def sample_compliance_record(sample_evidence_records) -> ComplianceRecord:
    """
    Returns reconciled ComplianceRecord fixture from deterministic evidence records.
    """
    return reconcile_evidence(sample_evidence_records)
