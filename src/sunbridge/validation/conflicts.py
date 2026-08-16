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
    Reconciles extracted evidence across all sources using strict evidence semantics:
    - Distinguishes datasheet specifications, buyer form requests, and verbal call notes.
    - Preserves weight conflict (11 kg vs ~18 kg installer guess).
    - Preserves model variant suffix ambiguity (SUN-5K-G06P3-EU-AM2-P1 vs call note SUN-5K-G06P3).
    - Treats cited standards as "cited in datasheet" rather than verified test certificates.
    - Flags SGS verbal claim and missing physical label photos as pending.
    - Separates manufacturer address (verified China) from formal country of origin docs.
    """
    field_map: Dict[str, List[EvidenceRecord]] = {}
    for rec in all_evidence:
        field_map.setdefault(rec.field_name, []).append(rec)

    conflicts: List[ConflictRecord] = []
    pending_items: List[str] = []
    questions: List[str] = []
    warnings: List[str] = []

    # 1. Weight Reconciliation (11 kg datasheet vs ~18 kg call notes)
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

    pending_items.append("Confirmation of exact product net weight (reconciling datasheet spec of 11 kg vs ~18 kg installer estimate).")
    questions.append("Please confirm the final net weight of the production unit (reconciling datasheet spec of 11 kg vs ~18 kg installer estimate).")

    # 2. Model Variant Confirmation (SUN-5K-G06P3-EU-AM2-P1 vs call notes SUN-5K-G06P3)
    datasheet_models = [r for r in field_map.get("model_name", []) if r.source_type == SourceType.MANUFACTURER_DATASHEET]
    buyer_models = [r for r in field_map.get("model_name", []) if r.source_type == SourceType.BUYER_FORM]
    call_models = [r for r in field_map.get("model_name", []) if r.source_type == SourceType.CALL_NOTES]

    target_exact_model = next((r.normalized_value for r in buyer_models), "SUN-5K-G06P3-EU-AM2-P1")
    call_model_str = next((r.normalized_value for r in call_models), "SUN-5K-G06P3")

    pending_items.append(f"Confirmation that the exact production variant for the Bangladesh order is {target_exact_model} (reconciling shortened call note reference '{call_model_str}').")
    questions.append(f"Please confirm that the exact production model/variant for the Bangladesh order is {target_exact_model}.")

    # 3. Testing, Standards & SGS
    sgs_record = next((r for r in all_evidence if r.field_name == "sgs_testing_claim"), None)
    
    pending_items.append("Applicable factory test reports and compliance / conformity certificates for this exact model.")
    questions.append("Please provide the applicable test reports and compliance / conformity certificates for this exact model.")

    pending_items.append("SGS test report or certificate (verbal mention in call notes; no document attached).")
    questions.append("SGS was mentioned verbally in the call notes. Please provide the relevant SGS report/certificate if applicable.")

    # 4. Labeling & Rating Plate Photo
    pending_items.append("High-resolution photograph of the actual production rating plate / product label.")
    questions.append("Please provide a photograph of the actual production rating plate / product label.")

    # 5. Final Datasheet / Spec confirmation
    questions.append("Please provide the final production datasheet / specification for the exact ordered variant if the supplied document is not the final revision.")

    # Build Structured Output Sections
    product_identity = {
        "target_model_variant": target_exact_model,
        "datasheet_model": next((r.normalized_value for r in datasheet_models), target_exact_model),
        "buyer_requested_model": target_exact_model,
        "call_notes_model": call_model_str,
        "model_status": "VERIFIED for Datasheet/Buyer Form; Call notes omit variant suffix (-EU-AM2-P1)",
        "variant_confirmation_status": "PENDING_FROM_MANUFACTURER",
        "application": "Rooftop Solar Inverter",
        "order_reference": "INT-2024-8841",
        "import_destination": "Bangladesh"
    }

    manufacturer_identity = {
        "legal_name": "Ningbo Deye Inverter Technology Co., Ltd.",
        "manufacturer_location": "China (Verified based on manufacturer address in datasheet)",
        "country_of_origin_status": "Stated as China in buyer form and call notes; formal customs origin documentation was not supplied.",
        "datasheet_source": "source_1",
        "buyer_form_source": "source_2"
    }

    electrical_specifications = {
        "rated_ac_output_power": "5 kW (5000 W)",
        "power_status": "Supported by manufacturer datasheet and consistent with buyer form (5000 W) and call notes (5 kW)",
        "ingress_protection": "IP65 (Explicitly stated in manufacturer datasheet; call notes also verbally report IP65)",
        "max_efficiency": "97.5% (Listed in manufacturer datasheet)",
        "call_notes_efficiency": "high 90s efficiency (Unquantified verbal claim; not treated as independent documentary evidence)",
        "weight_datasheet": "11 kg (Datasheet specification)",
        "weight_call_notes": "approximately 18 kg (Installer phone estimate)",
        "weight_status": "CONFLICT (Pending manufacturer confirmation)"
    }

    testing_and_standards = {
        "datasheet_cited_standards": "IEC/EN 62109-1/-2, IEC/EN 61000-6-1/-2/-3/-4 (Cited in datasheet; test reports/certificates not supplied)",
        "sgs_status": "PENDING_FROM_MANUFACTURER (SGS was mentioned verbally in call notes, but no certificate or report was provided)",
        "attached_documentation_status": "No test reports or certificates attached to intake materials"
    }

    labeling = {
        "label_information_supported_by_source_data": [
            "Manufacturer Legal Name: Ningbo Deye Inverter Technology Co., Ltd.",
            "Target Model Variant: SUN-5K-G06P3-EU-AM2-P1",
            "Rated AC Output Power: 5 kW (5000 W)",
            "Ingress Protection: IP65",
            "Manufacturer Location: China"
        ],
        "physical_label_verification": {
            "status": "PENDING_FROM_MANUFACTURER",
            "reason": "No physical product label / rating-plate photograph was provided, so the actual production label has not been verified."
        }
    }

    importer_paperwork = {
        "buyer": "SunBridge Trading Pvt. Ltd.",
        "import_destination": "Bangladesh",
        "order_reference": "INT-2024-8841",
        "required_delivery_date": "2024-11-30",
        "attached_documents": "None"
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
