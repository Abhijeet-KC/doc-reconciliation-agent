"""
Extraction module for structured document field extraction.
"""

from .prompts import SYSTEM_EXTRACTION_PROMPT, USER_EXTRACTION_PROMPT
from .extractor import extract_candidates_llm, extract_candidates_rules, extract_evidence_from_document

__all__ = [
    "SYSTEM_EXTRACTION_PROMPT",
    "USER_EXTRACTION_PROMPT",
    "extract_candidates_llm",
    "extract_candidates_rules",
    "extract_evidence_from_document"
]
