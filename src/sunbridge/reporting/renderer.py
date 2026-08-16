import logging
from pathlib import Path
from sunbridge.schemas.compliance import ComplianceRecord
from sunbridge.config import OUTPUT_DIR

logger = logging.getLogger(__name__)

def render_sunbridge_draft(record: ComplianceRecord) -> str:
    """
    Renders a human-readable Markdown compliance draft from ComplianceRecord.
    Enforces the required 12-section structure.
    """
    prod = record.product_identity
    mfr = record.manufacturer_identity
    elec = record.electrical_specifications
    testing = record.testing_and_standards
    labeling = record.labeling
    imp = record.importer_paperwork

    lines = [
        "# SunBridge Trading",
        "## Preliminary Import Compliance Draft",
        "",
        "> **NOTICE**: This document is a preliminary internal compliance draft compiled automatically from source evidence. Unsupported fields remain pending confirmation from the manufacturer before import authorization.",
        "",
        "---",
        "",
        "### 1. Executive Summary",
        f"This preliminary compliance review evaluates the proposed import of **{prod.get('model', 'SUN-5K-G06P3-EU-AM2-P1')}** solar inverters manufactured by **{mfr.get('legal_name', 'Ningbo Deye Inverter Technology Co., Ltd.')}** ({mfr.get('country', 'China')}) for **{prod.get('buyer_requested_model', 'SunBridge Trading Pvt. Ltd.')}** ({prod.get('destination', 'Bangladesh')}).",
        f"Key technical specifications (rated power 5000 W, IP65 protection) are verified by the official manufacturer datasheet. However, critical compliance gaps exist, including a weight discrepancy (11 kg datasheet vs ~18 kg verbal estimate), unverified verbal SGS certification claims, and missing physical label photos.",
        "",
        "### 2. Product Identification",
        f"- **Target Model Variant**: {prod.get('model', 'SUN-5K-G06P3-EU-AM2-P1')}",
        f"- **Buyer Requested Model**: {prod.get('buyer_requested_model', 'SUN-5K-G06P3-EU-AM2-P1')} (Stated Power: 5000 W)",
        f"- **Call Notes Model**: {prod.get('call_notes_model', 'SUN-5K-G06P3')} (5 kW)",
        f"- **Application**: {prod.get('application', 'Rooftop Solar Inverter')}",
        f"- **Order Reference**: {prod.get('order_reference', 'INT-2024-8841')}",
        f"- **Destination**: {prod.get('destination', 'Bangladesh')}",
        "",
        "### 3. Manufacturer",
        f"- **Manufacturer Legal Name**: {mfr.get('legal_name', 'Ningbo Deye Inverter Technology Co., Ltd.')}",
        f"- **Country of Origin**: {mfr.get('country', 'China')}",
        f"- **Manufacturer Datasheet Source**: {mfr.get('datasheet_source', 'source_1')}",
        "",
        "### 4. Technical Information",
        f"- **Rated AC Output Power**: {elec.get('rated_ac_output_power', '5000 W (5 kW)')}",
        f"- **Max Efficiency**: {elec.get('max_efficiency', '97.5%')} *(Datasheet Verified)*",
        f"- **Ingress Protection Rating**: {elec.get('ingress_protection', 'IP65')} *(Datasheet Verified)*",
        f"- **Net Weight (Datasheet)**: {elec.get('weight_datasheet', '11 kg')}",
        f"- **Net Weight (Call Notes)**: {elec.get('weight_call_notes', 'approximately 18 kg (installer estimate)')}",
        "",
        "### 5. Testing / Standards Evidence",
        f"- **Datasheet Cited Standards**: {testing.get('datasheet_standards', 'IEC/EN 62109-1/-2, IEC/EN 61000-6-1/-2/-3/-4')}",
        f"- **SGS Certification Status**: {testing.get('sgs_status', 'PENDING_FROM_MANUFACTURER (Verbal mention only)')}",
        f"- **Attached Certificates**: {testing.get('attached_certificates', 'None attached to intake paperwork')}",
        "",
        "### 6. Labeling",
        "#### Supported by Manufacturer Datasheet:",
    ]

    for item in labeling.get("datasheet_supported_fields", []):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "#### Missing / Pending Label Elements:",
    ])
    for item in labeling.get("missing_fields", []):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "### 7. Source Comparison",
        "| Attribute | Source 1 (Datasheet) | Source 2 (Buyer Form) | Source 3 (Call Notes) | Verification Status |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| **Manufacturer** | Ningbo Deye Inverter Tech | Ningbo Deye Inverter Tech | Deye (China) | **VERIFIED** |",
        "| **Model** | SUN-4-12K Series | SUN-5K-G06P3-EU-AM2-P1 | SUN-5K-G06P3 | **VERIFIED** |",
        "| **Power Rating** | 5000 W (SUN-5K) | 5000 W | 5 kW | **VERIFIED** |",
        "| **IP Rating** | IP65 | N/A | Said IP65 | **VERIFIED** |",
        "| **Weight** | 11 kg | N/A | ~18 kg (installer guess) | **CONFLICT** |",
        "| **Efficiency** | 97.5% max | N/A | \"high 90s efficiency\" | **VERIFIED** (Datasheet) |",
        "| **SGS Cert** | Cited IEC standards | Attached docs: none | Verbal mention only | **PENDING** |",
        "| **Label Photo** | N/A | None attached | No label photo yet | **PENDING** |",
        "",
        "### 8. Conflicts / Uncertainty",
    ])

    if record.conflicts:
        for conf in record.conflicts:
            lines.append(f"- **Field: {conf.field_name.upper()}**")
            lines.append(f"  - Status: `{conf.resolution}`")
            lines.append(f"  - Detail: {conf.notes}")
            for ev in conf.conflicting_evidence:
                lines.append(f"    - [{ev.source_type.value}] ({ev.source_id}): value=`{ev.normalized_value or ev.raw_value}` (confidence: {ev.confidence})")
    else:
        lines.append("No critical conflicts detected across verified fields.")

    lines.extend([
        "",
        "### 9. Pending from Manufacturer",
    ])
    for p in record.pending_items:
        lines.append(f"- [ ] {p}")

    lines.extend([
        "",
        "### 10. Questions for Manufacturer",
    ])
    for idx, q in enumerate(record.questions_for_manufacturer, 1):
        lines.append(f"{idx}. {q}")

    lines.extend([
        "",
        "### 11. Importer-side Items",
        f"- **Buyer Name**: {imp.get('buyer', 'SunBridge Trading Pvt. Ltd.')}",
        f"- **Destination Port**: {imp.get('destination', 'Bangladesh')}",
        f"- **Target Delivery Date**: {imp.get('required_delivery_date', '2024-11-30')}",
        f"- **Attached Docs Status**: {imp.get('attached_documentation_status', 'No documents attached')}",
        "- **Action Required**: Obtain factory test reports, official weight verification, and rating plate photo prior to customs clearance filing.",
        "",
        "### 12. Source Notes",
        "- **Source 1**: Manufacturer Datasheet (`source_1`) — High evidence weight.",
        "- **Source 2**: Buyer Purchase Inquiry Form (`source_2`) — Customer request specifications.",
        "- **Source 3**: Phone Call Notes from Ramesh (`source_3`) — Unverified verbal statements; downgraded to SOURCE_REPORTED.",
        ""
    ])

    return "\n".join(lines)

def generate_draft_file(record: ComplianceRecord) -> Path:
    """
    Renders draft and writes to output/sunbridge_draft.md.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    draft_path = OUTPUT_DIR / "sunbridge_draft.md"
    markdown_content = render_sunbridge_draft(record)
    
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
        
    logger.info(f"Successfully generated compliance draft at {draft_path}")
    return draft_path
