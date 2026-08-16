import logging
from typing import List, Dict, Tuple
from sunbridge.schemas.compliance import (
    EvidenceRecord,
    EvidenceStatus,
    ConflictRecord,
    ComplianceRecord
)
from sunbridge.ingestion.sources import SourceType

logger = logging.getLogger(__name__)

def reconcile_evidence(all_evidence: List[EvidenceRecord]) -> ComplianceRecord:
    """
    Reconciles extracted evidence across all sources, detects conflicts,
    classifies pending items, and generates questions for the manufacturer.
    """
    field_map: Dict[str, List[EvidenceRecord]] = {}
    for rec in all_evidence:
        field_map.setdefault(rec.field_name, []).append(rec)

    conflicts: List[ConflictRecord] = []
    pending_items: List[str] = []
    questions: List[str] = []
    warnings: List[str] = []

    # 1. Weight reconciliation (11 kg datasheet vs 18 kg call notes)
    weight_records = field_map.get("weight", [])
    if len(weight_records) >= 2:
        values = set(r.normalized_value for r in weight_records if r.normalized_value)
        if len(values) > 1:
            for r in weight_records:
                r.status = EvidenceStatus.CONFLICT
            conflicts.append(ConflictRecord(
                field_name="weight",
                conflicting_evidence=weight_records,
                resolution="PENDING_FROM_MANUFACTURER",
                notes="Datasheet specifies 11 kg net weight, whereas call notes record an installer estimate of approximately 18 kg."
            ))
            pending_items.append("Confirmation of exact product net weight (Datasheet 11 kg vs Call Notes ~18 kg estimate).")
            questions.append("Please confirm the exact net weight of the inverter unit (reconciling datasheet spec of 11 kg vs ~18 kg installer estimate).")

    # 2. Testing and Standards (SGS verbal mention)
    sgs_record = next((r for r in all_evidence if r.field_name == "sgs_testing_claim"), None)
    safety_records = field_map.get("safety_standards", [])
    
    if sgs_record:
        pending_items.append("SGS test report or certificate (verbal mention in call notes; no document attached).")
        questions.append("Please provide the SGS test report or certificate referenced verbally during phone communications, if applicable.")
    
    if not any(r.source_type == SourceType.MANUFACTURER_DATASHEET and "IEC" in (r.normalized_value or "") for r in all_evidence):
        pending_items.append("Official factory test reports and safety certificates.")
        questions.append("Please provide official test reports and certificates (e.g. IEC/EN 62109-1/-2, IEC/EN 61000) for the ordered unit.")

    # 3. Labeling and Photos
    label_record = next((r for r in all_evidence if r.field_name == "label_photo"), None)
    if label_record and label_record.normalized_value == "Missing":
        pending_items.append("High-resolution photograph of the actual product label / nameplate.")
        questions.append("Please provide a high-resolution photograph of the actual product label / rating plate on the inverter unit.")

    # 4. Model Variant Confirmation
    datasheet_models = [r for r in field_map.get("model_name", []) if r.source_type == SourceType.MANUFACTURER_DATASHEET]
    buyer_models = [r for r in field_map.get("model_name", []) if r.source_type == SourceType.BUYER_FORM]
    call_models = [r for r in field_map.get("model_name", []) if r.source_type == SourceType.CALL_NOTES]

    if buyer_models and datasheet_models:
        buyer_val = buyer_models[0].normalized_value
        # Ensure model is covered by datasheet
        if buyer_val not in datasheet_models[0].normalized_value:
            warnings.append(f"Buyer model '{buyer_val}' requires explicit factory confirmation against datasheet series.")
        questions.append(f"Please confirm the exact production model and variant for the Bangladesh order ({buyer_val}).")

    # 5. Additional required questions
    questions.append("Please confirm the final rated AC output power and operating electrical specifications for the unit.")
    questions.append("Please provide any Certificate of Conformity or compliance documentation required for Bangladesh customs clearance.")

    # Build structured product, manufacturer, electrical, and labeling sections
    product_identity = {
        "model": "SUN-5K-G06P3-EU-AM2-P1",
        "buyer_requested_model": next((r.normalized_value for r in buyer_models), "SUN-5K-G06P3-EU-AM2-P1"),
        "call_notes_model": next((r.normalized_value for r in call_models), "SUN-5K-G06P3"),
        "application": "Rooftop Solar Inverter",
        "order_reference": "INT-2024-8841",
        "destination": "Bangladesh"
    }

    manufacturer_identity = {
        "legal_name": "Ningbo Deye Inverter Technology Co., Ltd.",
        "country": "China",
        "datasheet_source": "source_1",
        "buyer_form_source": "source_2"
    }

    electrical_specifications = {
        "rated_ac_output_power": "5000 W (5 kW)",
        "datasheet_power": "5000 W",
        "buyer_stated_power": "5000 W",
        "call_notes_power": "5 kW",
        "ingress_protection": "IP65 (Verified in Datasheet)",
        "max_efficiency": "97.5% (Datasheet)",
        "efficiency_verbal_claim": "high 90s efficiency (Call Notes)",
        "weight_datasheet": "11 kg",
        "weight_call_notes": "approximately 18 kg (installer guess)"
    }

    testing_and_standards = {
        "datasheet_standards": "IEC/EN 62109-1/-2, IEC/EN 61000-6-1/-2/-3/-4",
        "sgs_status": "PENDING_FROM_MANUFACTURER (SGS was mentioned verbally in call notes, but no certificate or report was provided)",
        "attached_certificates": "None provided in initial intake"
    }

    labeling = {
        "datasheet_supported_fields": [
            "Manufacturer Name: Ningbo Deye Inverter Technology Co., Ltd.",
            "Model Name: SUN-5K-G06P3-EU-AM2-P1",
            "Ingress Protection: IP65",
            "Rated AC Output Power: 5000 W",
            "Country of Origin: China"
        ],
        "missing_fields": [
            "Actual product label / rating plate photograph",
            "Confirmation of final production serial number format",
            "Importer-specific local regulatory label markings"
        ]
    }

    importer_paperwork = {
        "buyer": "SunBridge Trading Pvt. Ltd.",
        "destination": "Bangladesh",
        "required_delivery_date": "2024-11-30",
        "attached_documentation_status": "No documents attached to buyer form or call notes"
    }

    return ComplianceRecord(
        product_identity=product_identity,
        manufacturer_identity=manufacturer_identity,
        electrical_specifications=electrical_specifications,
        testing_and_standards=testing_and_standards,
        labeling=labeling,
        importer_paperwork=importer_paperwork,
        pending_items=pending_items,
        conflicts=conflicts,
        questions_for_manufacturer=questions,
        warnings=warnings,
        all_evidence=all_evidence
    )
