"""
Document parsing module using PyMuPDF fitz.
"""

from .models import DocumentData, PageData, TableData
from .pdf_parser import parse_pdf_document, parse_text_document, parse_source

__all__ = [
    "DocumentData",
    "PageData",
    "TableData",
    "parse_pdf_document",
    "parse_text_document",
    "parse_source"
]
