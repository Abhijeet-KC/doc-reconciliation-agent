import logging
from pathlib import Path
from langgraph.graph import StateGraph, START, END
from sunbridge.config import settings, OUTPUT_DIR
from sunbridge.ingestion import get_all_sources, fetch_datasheet
from sunbridge.parsing import parse_source
from sunbridge.extraction import extract_evidence_from_document
from sunbridge.validation import reconcile_evidence, serialize_compliance_json, validate_compliance_record
from sunbridge.reporting import generate_draft_file
from sunbridge.graph.state import PipelineState

logger = logging.getLogger(__name__)

def fetch_sources_node(state: PipelineState) -> PipelineState:
    logger.info("Node [FETCH_SOURCES]: Fetching source definitions and downloading datasheet...")
    sources = get_all_sources(settings.source1_url)
    try:
        pdf_path = fetch_datasheet(settings.source1_url)
        local_pdf_str = str(pdf_path)
    except Exception as e:
        logger.error(f"Error fetching datasheet: {e}")
        state["errors"].append(str(e))
        local_pdf_str = None

    return {
        **state,
        "sources": sources,
        "local_pdf_path": local_pdf_str
    }

def parse_documents_node(state: PipelineState) -> PipelineState:
    logger.info("Node [PARSE_DOCUMENTS]: Parsing documents with PyMuPDF fitz...")
    parsed_docs = []
    pdf_path = state.get("local_pdf_path")

    for src in state["sources"]:
        try:
            doc_data = parse_source(src, pdf_path)
            parsed_docs.append(doc_data)
        except Exception as e:
            logger.error(f"Failed to parse source {src.id}: {e}")
            state["errors"].append(f"Parse error {src.id}: {e}")

    return {
        **state,
        "raw_documents": parsed_docs
    }

def extract_candidate_fields_node(state: PipelineState) -> PipelineState:
    logger.info("Node [EXTRACT_CANDIDATE_FIELDS]: Extracting fields...")
    all_ev = []
    for doc in state["raw_documents"]:
        ev_records = extract_evidence_from_document(doc)
        all_ev.extend(ev_records)

    return {
        **state,
        "extracted_evidence": all_ev
    }

def normalize_fields_node(state: PipelineState) -> PipelineState:
    logger.info("Node [NORMALIZE_FIELDS]: Normalizing extracted values...")
    # Standardize values (units, text capitalization)
    normalized_ev = []
    for ev in state["extracted_evidence"]:
        if ev.unit and "kg" in ev.unit.lower():
            ev.unit = "kg"
        elif ev.unit and "w" in ev.unit.lower():
            ev.unit = "W"
        normalized_ev.append(ev)
        
    return {
        **state,
        "extracted_evidence": normalized_ev
    }

def validate_and_compare_sources_node(state: PipelineState) -> PipelineState:
    logger.info("Node [VALIDATE_AND_COMPARE_SOURCES]: Reconciling multi-source evidence...")
    compliance_rec = reconcile_evidence(state["extracted_evidence"])
    return {
        **state,
        "compliance_record": compliance_rec
    }

def classify_evidence_node(state: PipelineState) -> PipelineState:
    logger.info("Node [CLASSIFY_EVIDENCE]: Classifying evidence status and pending items...")
    # Verified by compliance record build
    return state

def generate_structured_output_node(state: PipelineState) -> PipelineState:
    logger.info("Node [GENERATE_STRUCTURED_OUTPUT]: Writing compliance.json...")
    rec = state["compliance_record"]
    json_path = OUTPUT_DIR / "compliance.json"
    if rec:
        json_str = serialize_compliance_json(rec)
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_str)
        return {
            **state,
            "json_output_path": str(json_path)
        }
    return state

def generate_human_draft_node(state: PipelineState) -> PipelineState:
    logger.info("Node [GENERATE_HUMAN_DRAFT]: Rendering sunbridge_draft.md...")
    rec = state["compliance_record"]
    if rec:
        draft_path = generate_draft_file(rec)
        return {
            **state,
            "draft_output_path": str(draft_path)
        }
    return state

def validate_output_node(state: PipelineState) -> PipelineState:
    logger.info("Node [VALIDATE_OUTPUT]: Verifying final pipeline output integrity...")
    rec = state["compliance_record"]
    if rec:
        try:
            is_valid = validate_compliance_record(rec)
            return {
                **state,
                "is_valid": is_valid
            }
        except Exception as e:
            logger.error(f"Output validation error: {e}")
            return {
                **state,
                "is_valid": False,
                "errors": state["errors"] + [str(e)]
            }
    return state

def build_compliance_pipeline():
    builder = StateGraph(PipelineState)

    builder.add_node("FETCH_SOURCES", fetch_sources_node)
    builder.add_node("PARSE_DOCUMENTS", parse_documents_node)
    builder.add_node("EXTRACT_CANDIDATE_FIELDS", extract_candidate_fields_node)
    builder.add_node("NORMALIZE_FIELDS", normalize_fields_node)
    builder.add_node("VALIDATE_AND_COMPARE_SOURCES", validate_and_compare_sources_node)
    builder.add_node("CLASSIFY_EVIDENCE", classify_evidence_node)
    builder.add_node("GENERATE_STRUCTURED_OUTPUT", generate_structured_output_node)
    builder.add_node("GENERATE_HUMAN_DRAFT", generate_human_draft_node)
    builder.add_node("VALIDATE_OUTPUT", validate_output_node)

    # Wire graph edges
    builder.add_edge(START, "FETCH_SOURCES")
    builder.add_edge("FETCH_SOURCES", "PARSE_DOCUMENTS")
    builder.add_edge("PARSE_DOCUMENTS", "EXTRACT_CANDIDATE_FIELDS")
    builder.add_edge("EXTRACT_CANDIDATE_FIELDS", "NORMALIZE_FIELDS")
    builder.add_edge("NORMALIZE_FIELDS", "VALIDATE_AND_COMPARE_SOURCES")
    builder.add_edge("VALIDATE_AND_COMPARE_SOURCES", "CLASSIFY_EVIDENCE")
    builder.add_edge("CLASSIFY_EVIDENCE", "GENERATE_STRUCTURED_OUTPUT")
    builder.add_edge("GENERATE_STRUCTURED_OUTPUT", "GENERATE_HUMAN_DRAFT")
    builder.add_edge("GENERATE_HUMAN_DRAFT", "VALIDATE_OUTPUT")
    builder.add_edge("VALIDATE_OUTPUT", END)

    return builder.compile()
