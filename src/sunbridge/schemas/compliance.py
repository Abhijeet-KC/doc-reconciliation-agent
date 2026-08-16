from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sunbridge.ingestion.sources import SourceType

class EvidenceStatus(str, Enum):
    VERIFIED = "VERIFIED"
    SOURCE_REPORTED = "SOURCE_REPORTED"
    CONFLICT = "CONFLICT"
    PENDING_FROM_MANUFACTURER = "PENDING_FROM_MANUFACTURER"
    NOT_FOUND = "NOT_FOUND"

class EvidenceRecord(BaseModel):
    field_name: str
    normalized_value: Optional[str] = None
    raw_value: Optional[str] = None
    unit: Optional[str] = None
    source_id: str
    source_type: SourceType
    location: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    status: EvidenceStatus = EvidenceStatus.VERIFIED
    notes: Optional[str] = None

class ConflictRecord(BaseModel):
    field_name: str
    conflicting_evidence: List[EvidenceRecord]
    resolution: Optional[str] = "PENDING_FROM_MANUFACTURER"
    notes: Optional[str] = None

class CandidateField(BaseModel):
    field_name: str
    normalized_value: Optional[str] = None
    raw_value: Optional[str] = None
    unit: Optional[str] = None
    location: Optional[str] = None
    confidence: float = 1.0
    notes: Optional[str] = None

class ExtractedCandidates(BaseModel):
    source_id: str
    source_type: SourceType
    candidates: List[CandidateField] = Field(default_factory=list)

class CandidateFieldWithSource(BaseModel):
    source_id: str
    field_name: str
    normalized_value: Optional[str] = None
    raw_value: Optional[str] = None
    unit: Optional[str] = None
    location: Optional[str] = None
    confidence: float = 1.0
    notes: Optional[str] = None

class UnifiedExtractedCandidates(BaseModel):
    candidates: List[CandidateFieldWithSource] = Field(default_factory=list)

class ComplianceRecord(BaseModel):
    product_identity: Dict[str, Any] = Field(default_factory=dict)
    manufacturer_identity: Dict[str, Any] = Field(default_factory=dict)
    electrical_specifications: Dict[str, Any] = Field(default_factory=dict)
    testing_and_standards: Dict[str, Any] = Field(default_factory=dict)
    labeling: Dict[str, Any] = Field(default_factory=dict)
    importer_paperwork: Dict[str, Any] = Field(default_factory=dict)
    pending_items: List[str] = Field(default_factory=list)
    conflicts: List[ConflictRecord] = Field(default_factory=list)
    questions_for_manufacturer: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    all_evidence: List[EvidenceRecord] = Field(default_factory=list)
