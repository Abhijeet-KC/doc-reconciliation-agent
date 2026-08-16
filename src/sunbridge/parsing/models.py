from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sunbridge.ingestion.sources import SourceType

class TableData(BaseModel):
    page_number: int
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    raw_text: str = ""

class PageData(BaseModel):
    page_number: int
    text: str
    tables: List[TableData] = Field(default_factory=list)

class DocumentData(BaseModel):
    source_id: str
    source_type: SourceType
    filename: Optional[str] = None
    url: Optional[str] = None
    pages: List[PageData] = Field(default_factory=list)
    full_text: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
