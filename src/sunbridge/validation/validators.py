import json
import logging
from typing import Dict, Any
from sunbridge.schemas.compliance import ComplianceRecord
from sunbridge.config import settings

logger = logging.getLogger(__name__)

FORBIDDEN_PHRASES = [
    "destination port",
    "sgs certified",
    "sgs compliance verified",
    "sgs certification confirmed",
    "country of origin: china (verified)",
    "certified to iec"
]

def validate_compliance_record(record: ComplianceRecord) -> bool:
    """
    Validates the generated ComplianceRecord against required system assertions & semantic guardrails:
    1. Every non-null extracted fact has source attribution.
    2. Every conflict has more than one evidence record.
    3. No secret/API key is present in output text.
    4. Required source types are represented.
    5. Pending items and factory questions exist.
    6. Semantic Guardrails: No overclaiming or hallucinated origin/certification phrases.
    """
    # 1. Source attribution check
    for ev in record.all_evidence:
        if not ev.source_id or not ev.source_type:
            raise ValueError(f"Evidence record for field '{ev.field_name}' is missing source_id or source_type")

    # 2. Conflicts check
    for conf in record.conflicts:
        if len(conf.conflicting_evidence) < 2:
            raise ValueError(f"Conflict record for field '{conf.field_name}' must contain at least 2 conflicting evidence records")

    # 3. Secret check & Semantic Guardrails
    dump_str = json.dumps(record.model_dump(), default=str)
    dump_str_lower = dump_str.lower()

    if settings.llm_api_key and len(settings.llm_api_key) > 5:
        if settings.llm_api_key in dump_str:
            raise ValueError("SECURITY RISK: LLM API key detected in output compliance record!")

    for phrase in FORBIDDEN_PHRASES:
        if phrase in dump_str_lower:
            raise ValueError(f"SEMANTIC GUARDRAIL ERROR: Forbidden overclaiming phrase '{phrase}' detected in compliance record output!")

    # 4. Source types check
    sources = set(ev.source_type for ev in record.all_evidence)
    if len(sources) < 2:
        logger.warning(f"Only {len(sources)} source types represented in evidence list.")

    # 5. Pending & Questions check
    if not record.pending_items:
        raise ValueError("Compliance record must contain pending-from-manufacturer items")
    if not record.questions_for_manufacturer:
        raise ValueError("Compliance record must contain questions for manufacturer")

    logger.info("ComplianceRecord successfully passed all validation checks and semantic guardrails.")
    return True

def serialize_compliance_json(record: ComplianceRecord) -> str:
    """
    Serializes ComplianceRecord to structured JSON string with evidence attribution.
    """
    validate_compliance_record(record)
    return record.model_dump_json(indent=2)
