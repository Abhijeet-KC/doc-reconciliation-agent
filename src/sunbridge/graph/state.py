from typing import List, Optional, Dict, Any, TypedDict
from sunbridge.ingestion.sources import SourceDefinition
from sunbridge.parsing.models import DocumentData
from sunbridge.schemas.compliance import EvidenceRecord, ComplianceRecord

class PipelineState(TypedDict):
    sources: List[SourceDefinition]
    local_pdf_path: Optional[str]
    raw_documents: List[DocumentData]
    extracted_evidence: List[EvidenceRecord]
    compliance_record: Optional[ComplianceRecord]
    json_output_path: Optional[str]
    draft_output_path: Optional[str]
    is_valid: bool
    errors: List[str]
