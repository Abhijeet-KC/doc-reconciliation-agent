import pytest
from sunbridge.config import settings
from sunbridge.graph import build_compliance_pipeline, PipelineState

@pytest.mark.integration
def test_live_pipeline_integration():
    """
    Live integration test using the actual configured OpenRouter LLM endpoint.
    Executed ONLY when pytest is run with '-m integration'.
    """
    if not settings.llm_api_key or settings.llm_api_key == "your_api_key_here":
        pytest.skip("No valid LLM_API_KEY configured in environment.")

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

    assert final_state["is_valid"] is True
    assert final_state["compliance_record"] is not None
    assert final_state["llm_requests_made"] == 1
