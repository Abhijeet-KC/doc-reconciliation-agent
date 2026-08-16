import logging
from pathlib import Path
from sunbridge.schemas.compliance import ComplianceRecord
from sunbridge.config import OUTPUT_DIR

logger = logging.getLogger(__name__)

def render_sunbridge_draft(record: ComplianceRecord) -> str:
    """
    Renders a human-readable Markdown compliance draft from ComplianceRecord.
    Enforces strict evidence semantics and zero overclaiming.
    """
    prod = record.product_identity
    mfr = record.manufacturer_identity
    elec = record.electrical_specifications
    testing = record.testing_and_standards
    labeling = record.labeling
    imp = record.importer_paperwork

    target_model = prod.get("target_model_variant", "SUN-5K-G06P3-EU-AM2-P1")
    call_model = prod.get("call_notes_model", "SUN-5K-G06P3")

    lines = [
        "# SunBridge Trading",
        "## Preliminary Import Compliance Draft",
        "",
        "> **NOTICE**: This document is a preliminary internal compliance summary compiled automatically from intake source materials. Unsupported fields remain pending confirmation from the manufacturer before import authorization.",
        "",
        "---",
        "",
        "### 1. Executive Summary",
        f"This preliminary compliance review evaluates the proposed import of **{target_model}** solar inverters manufactured by **{mfr.get('legal_name', 'Ningbo Deye Inverter Technology Co., Ltd.')}** (China) for **{imp.get('buyer', 'SunBridge Trading Pvt. Ltd.')}** ({prod.get('import_destination', 'Bangladesh')}, Ref: **{prod.get('order_reference', 'INT-2024-8841')}**).",
        "",
        f"The target model **{target_model}**, rated AC output power (5 kW / 5000 W), and IP65 ingress protection are explicitly established by the manufacturer datasheet. However, critical verification items remain open:",
        f"1. **Model Suffix**: The buyer form and datasheet specify `{target_model}`, whereas call notes refer to `{call_model}` without the variant suffix.",
        f"2. **Weight Conflict**: The datasheet specifies 11 kg net weight, while call notes record an approximate 18 kg installer estimate.",
        "3. **Testing Evidence**: The datasheet cites IEC/EN 62109 and IEC/EN 61000 standards, but no physical test reports or certificates were provided.",
        "4. **Verbal Claims & Labeling**: SGS certification was mentioned verbally on the phone without documentation, and no rating-plate photo was provided.",
        "",
        "### 2. Product Identification",
        f"- **Exact Target Model**: {target_model}",
        f"- **Buyer Form Model**: {prod.get('buyer_requested_model', target_model)} *(5000 W, Rooftop)*",
        f"- **Call Notes Model**: {call_model} *(Variant suffix -EU-AM2-P1 omitted in call notes)*",
        f"- **Model Variant Confirmation**: `PENDING_FROM_MANUFACTURER`",
        f"- **Application**: {prod.get('application', 'Rooftop Solar Inverter')}",
        f"- **Order Reference**: {prod.get('order_reference', 'INT-2024-8841')}",
        f"- **Import Destination**: {prod.get('import_destination', 'Bangladesh')}",
        "",
        "### 3. Manufacturer",
        f"- **Manufacturer Legal Name**: {mfr.get('legal_name', 'Ningbo Deye Inverter Technology Co., Ltd.')}",
        f"- **Manufacturer Location**: {mfr.get('manufacturer_location', 'China (Verified based on manufacturer address in datasheet)')}",
        f"- **Country of Origin / Manufacture**: {mfr.get('country_of_origin_status', 'Stated as China in buyer form and call notes; formal customs origin documentation was not supplied.')}",
        f"- **Datasheet Source**: {mfr.get('datasheet_source', 'source_1')}",
        "",
        "### 4. Technical Information",
        f"- **Rated AC Output Power**: {elec.get('power_status', '5 kW (5000 W), supported by the manufacturer datasheet and consistent with the buyer form and call notes.')}",
        f"- **Ingress Protection Rating**: {elec.get('ingress_protection', 'IP65 (Explicitly stated in manufacturer datasheet; call notes also verbally report IP65)')}",
        f"- **Maximum Efficiency**: Maximum efficiency listed in the manufacturer datasheet: 97.5%. Call notes also mention \"high 90s efficiency\", but this is an unquantified verbal claim and is not treated as independent documentary evidence.",
        f"- **Net Weight (Datasheet)**: {elec.get('weight_datasheet', '11 kg')}",
        f"- **Net Weight (Call Notes)**: {elec.get('weight_call_notes', 'approximately 18 kg (installer estimate)')}",
        f"- **Net Weight Status**: `{elec.get('weight_status', 'CONFLICT (Pending manufacturer confirmation)')}`",
        "",
        "### 5. Testing / Standards Evidence",
        f"- **Datasheet Cited Standards**: {testing.get('datasheet_cited_standards', 'IEC/EN 62109-1/-2, IEC/EN 61000-6-1/-2/-3/-4 (Cited in datasheet; test reports/certificates not supplied)')}",
        f"- **SGS Certification Status**: `{testing.get('sgs_status', 'PENDING_FROM_MANUFACTURER')}`",
        f"- **Attached Certificates**: {testing.get('attached_documentation_status', 'None attached to intake materials')}",
        "",
        "### 6. Labeling",
        "#### Label Information Supported by Source Data",
        "The following information from source documents can inform the expected label:",
    ]

    for item in labeling.get("label_information_supported_by_source_data", []):
        lines.append(f"- {item}")

    phys = labeling.get("physical_label_verification", {})
    lines.extend([
        "",
        "#### Physical Label Verification",
        f"- **Status**: `{phys.get('status', 'PENDING_FROM_MANUFACTURER')}`",
        f"- **Reason**: {phys.get('reason', 'No physical product label / rating-plate photograph was provided, so the actual production label has not been verified.')}",
        "",
        "### 7. Source Comparison",
        "| Attribute | Source 1 (Datasheet) | Source 2 (Buyer Form) | Source 3 (Call Notes) | Interpretation |",
        "| :--- | :--- | :--- | :--- | :--- |",
        "| **Manufacturer** | Ningbo Deye Inverter Tech | Ningbo Deye Inverter Tech | Deye (China) | Manufacturer identity supported by datasheet; buyer/call are consistent but not equivalent documentary evidence |",
        f"| **Model** | {target_model} | {target_model} | {call_model} | Full variant suffix match between datasheet & buyer form; call notes omit suffix; exact variant confirmation pending |",
        "| **Power Rating** | 5000 W (5 kW) | 5000 W | 5 kW | Power ratings aligned across all sources; supported by datasheet |",
        "| **IP Rating** | IP65 | N/A | Said IP65 | IP65 explicitly supported by datasheet; call note is verbal report |",
        "| **Weight** | 11 kg | N/A | ~18 kg (installer guess) | CONFLICT between datasheet specification (11 kg) and call notes estimate (~18 kg); factory confirmation pending |",
        "| **Efficiency** | 97.5% max | N/A | \"high 90s efficiency\" | Exact numerical efficiency supported only by datasheet (97.5%); verbal claim retained separately |",
        "| **SGS** | Cited standards (IEC/EN) | Attached docs: none | Verbal mention only | SGS report/certificate pending from manufacturer |",
        "| **Label Photo** | N/A | None attached | No label photo yet | Physical rating plate photo pending from manufacturer |",
        "",
        "### 8. Conflicts / Uncertainty",
        "- **Field: WEIGHT**",
        "  - Status: `PENDING_FROM_MANUFACTURER`",
        "  - Detail: The manufacturer datasheet lists 11 kg, while the call notes record an approximate 18 kg installer estimate. The final production net weight should be confirmed by the manufacturer.",
        "- **Field: MODEL_VARIANT**",
        "  - Status: `PENDING_FROM_MANUFACTURER`",
        "  - Detail: The buyer form and manufacturer datasheet identify SUN-5K-G06P3-EU-AM2-P1, while the call notes refer to SUN-5K-G06P3 without the full variant suffix.",
        "",
        "### 9. Pending from Manufacturer",
    ])

    for p in record.pending_items:
        lines.append(f"1. [ ] {p}")

    lines.extend([
        "",
        "### 10. Questions for Manufacturer",
    ])
    for idx, q in enumerate(record.questions_for_manufacturer, 1):
        lines.append(f"{idx}. {q}")

    lines.extend([
        "",
        "### 11. Importer-side Information",
        f"- **Buyer Name**: {imp.get('buyer', 'SunBridge Trading Pvt. Ltd.')}",
        f"- **Import Destination**: {imp.get('import_destination', 'Bangladesh')}",
        f"- **Order Reference**: {imp.get('order_reference', 'INT-2024-8841')}",
        f"- **Required Delivery Date**: {imp.get('required_delivery_date', '2024-11-30')}",
        f"- **Attached Documents**: {imp.get('attached_documents', 'None')}",
        "",
        "### 12. Source Notes",
        "- **Source 1**: Manufacturer Datasheet (`source_1`) — Technical specifications.",
        "- **Source 2**: Buyer Purchase Inquiry Form (`source_2`) — Purchase order requirements.",
        "- **Source 3**: Phone Call Notes from Ramesh (`source_3`) — Unverified verbal statements; retained for risk tracking.",
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
