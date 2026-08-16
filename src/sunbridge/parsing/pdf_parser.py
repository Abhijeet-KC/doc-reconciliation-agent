import logging
from pathlib import Path
from typing import Union
import pymupdf  # PyMuPDF
from sunbridge.ingestion.sources import SourceDefinition, SourceType
from sunbridge.parsing.models import DocumentData, PageData, TableData

logger = logging.getLogger(__name__)

def parse_pdf_document(pdf_path: Union[str, Path], source_def: SourceDefinition) -> DocumentData:
    """
    Parses a PDF document using PyMuPDF (fitz), preserving page numbers and table data.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")

    doc = pymupdf.open(str(pdf_path))
    pages: list[PageData] = []
    full_text_parts: list[str] = []

    for page_idx in range(len(doc)):
        page_num = page_idx + 1
        page = doc[page_idx]
        text = page.get_text("text")
        full_text_parts.append(f"--- PAGE {page_num} ---\n" + text)

        tables: list[TableData] = []
        try:
            # PyMuPDF 1.23.0+ table extraction
            finder = page.find_tables()
            for tab in finder.tables:
                extracted = tab.extract()
                if extracted and len(extracted) > 0:
                    headers = [str(cell or "").strip() for cell in extracted[0]]
                    rows = [[str(cell or "").strip() for cell in row] for row in extracted[1:]]
                    raw_tab_text = "\n".join(["\t".join(row) for row in extracted])
                    tables.append(TableData(
                        page_number=page_num,
                        headers=headers,
                        rows=rows,
                        raw_text=raw_tab_text
                    ))
        except Exception as tab_err:
            logger.debug(f"Table extraction notice on page {page_num}: {tab_err}")

        pages.append(PageData(
            page_number=page_num,
            text=text,
            tables=tables
        ))

    doc.close()
    full_text = "\n\n".join(full_text_parts)

    return DocumentData(
        source_id=source_def.id,
        source_type=source_def.type,
        filename=pdf_path.name,
        url=source_def.location,
        pages=pages,
        full_text=full_text,
        metadata=source_def.metadata
    )

def parse_text_document(source_def: SourceDefinition) -> DocumentData:
    """
    Parses a plain-text source definition (buyer form or call notes) into DocumentData.
    """
    text_content = source_def.content or ""
    page = PageData(
        page_number=1,
        text=text_content,
        tables=[]
    )
    return DocumentData(
        source_id=source_def.id,
        source_type=source_def.type,
        filename=None,
        url=source_def.location,
        pages=[page],
        full_text=text_content,
        metadata=source_def.metadata
    )

def parse_source(source_def: SourceDefinition, local_pdf_path: Union[str, Path] = None) -> DocumentData:
    """
    Routes parsing to PDF or text parser based on source definition type.
    """
    if source_def.type == SourceType.MANUFACTURER_DATASHEET:
        if not local_pdf_path:
            raise ValueError("local_pdf_path must be provided for PDF parsing")
        return parse_pdf_document(local_pdf_path, source_def)
    else:
        return parse_text_document(source_def)
