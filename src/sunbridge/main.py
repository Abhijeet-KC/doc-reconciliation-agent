import sys
import logging
from pathlib import Path

# Add src to sys.path if needed
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sunbridge.config import settings
from sunbridge.graph import build_compliance_pipeline, PipelineState

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sunbridge.main")

def run_pipeline() -> PipelineState:
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
        "is_valid": False,
        "errors": []
    }

    final_state = pipeline.invoke(initial_state)

    rec = final_state.get("compliance_record")
    num_sources = len(final_state.get("sources", []))
    num_evidence = len(final_state.get("extracted_evidence", []))
    num_conflicts = len(rec.conflicts) if rec else 0
    num_pending = len(rec.pending_items) if rec else 0

    print("\n==================================================")
    print("      SUNBRIDGE COMPLIANCE PIPELINE SUMMARY      ")
    print("==================================================")
    print(f"Sources processed:    {num_sources}")
    print(f"Fields extracted:     {num_evidence}")
    print(f"Conflicts detected:   {num_conflicts}")
    print(f"Pending items:        {num_pending}")
    print(f"Draft generated:      {final_state.get('draft_output_path')}")
    print(f"Structured output:    {final_state.get('json_output_path')}")
    print("Pipeline Status:      " + ("SUCCESS" if final_state.get("is_valid") else "FAILED"))
    print("==================================================\n")

    return final_state

if __name__ == "__main__":
    run_pipeline()
