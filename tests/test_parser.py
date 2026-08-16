import pytest
from pathlib import Path
from sunbridge.ingestion.sources import get_all_sources
from sunbridge.parsing import parse_source, DocumentData
from sunbridge.config import DOCS_FALLBACK_DIR

def test_parse_pdf_document():
    sources = get_all_sources("http://example.com/dummy.pdf")
    ds_source = sources[0]
    fallback_pdf = DOCS_FALLBACK_DIR / "src1_task2.pdf"
    
    assert fallback_pdf.exists(), "Fallback PDF does not exist"
    
    doc = parse_source(ds_source, fallback_pdf)
    assert isinstance(doc, DocumentData)
    assert doc.source_id == "source_1"
    assert len(doc.pages) > 0
    assert "SUN-5K" in doc.full_text or "Deye" in doc.full_text

def test_parse_text_documents():
    sources = get_all_sources("http://example.com/dummy.pdf")
    buyer_source = sources[1]
    call_source = sources[2]
    
    doc_buyer = parse_source(buyer_source)
    assert doc_buyer.source_id == "source_2"
    assert "SunBridge Trading" in doc_buyer.full_text
    
    doc_call = parse_source(call_source)
    assert doc_call.source_id == "source_3"
    assert "Ramesh" in doc_call.full_text
