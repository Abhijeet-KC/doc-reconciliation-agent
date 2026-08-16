import sys
import time
import logging
from pathlib import Path

# Add src to sys.path if needed
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sunbridge.config import settings
from sunbridge.graph import build_compliance_pipeline, PipelineState
from sunbridge.extraction import reset_llm_requests_counter, get_llm_requests_counter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sunbridge.main")

def run_pipeline() -> PipelineState:
    t_start = time.time()
    reset_llm_requests_counter()
    settings.ensure_directories()
    
    pipeline = build_compliance_pipeline()
    
    initial_state: PipelineState = {
        "sources": [],
        "local_pdf_path": None,
        "raw_documents": [],
        "extracted_evidence": [],
        "compliance_record": None,
        "json_output_path": None,
        "draft_output_path": None,
        "extraction_mode": "RULE_BASED",
        "llm_error": None,
        "llm_requests_made": 0,
        "timings": {},
        "is_valid": False,
        "errors": []
    }

    final_state = pipeline.invoke(initial_state)

    total_time = time.time() - t_start
    timings = final_state.get("timings", {})
    timings["Total"] = total_time

    rec = final_state.get("compliance_record")
    num_sources = len(final_state.get("sources", []))
    num_evidence = len(final_state.get("extracted_evidence", []))
    num_conflicts = len(rec.conflicts) if rec else 0
    num_pending = len(rec.pending_items) if rec else 0

    mode = final_state.get("extraction_mode", "RULE_BASED")
    llm_err = final_state.get("llm_error")
    reqs_made = final_state.get("llm_requests_made", get_llm_requests_counter())

    print("\n==================================================")
    print("      SUNBRIDGE COMPLIANCE PIPELINE SUMMARY      ")
    print("==================================================")
    print(f"Sources processed:    {num_sources}")
    print(f"Fields extracted:     {num_evidence}")
    print(f"Conflicts detected:   {num_conflicts}")
    print(f"Pending items:        {num_pending}")
    print(f"LLM requests made:    {reqs_made}")
    print(f"Extraction mode:      {mode}")
    
    if llm_err:
        print(f"LLM error:            {llm_err}")
        print("Fallback:             DETERMINISTIC_RULE_BASED")

    print("\nTiming:")
    print(f"  Download:   {timings.get('Download', 0.0):.2f}s")
    print(f"  Parsing:    {timings.get('Parsing', 0.0):.2f}s")
    print(f"  LLM:        {timings.get('LLM', 0.0):.2f}s")
    print(f"  Validation: {timings.get('Validation', 0.0):.2f}s")
    print(f"  Rendering:  {timings.get('Rendering', 0.0):.2f}s")
    print(f"  Total:      {timings.get('Total', 0.0):.2f}s")

    print("\nDraft generated:      " + str(final_state.get('draft_output_path')))
    print("Structured output:    " + str(final_state.get('json_output_path')))
    print("Pipeline Status:      " + ("SUCCESS" if final_state.get("is_valid") else "FAILED"))
    print("==================================================\n")

    return final_state

if __name__ == "__main__":
    run_pipeline()
