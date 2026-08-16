import pytest
from unittest.mock import MagicMock, patch
import openai
from sunbridge.config import settings
from sunbridge.graph import build_compliance_pipeline, PipelineState
from sunbridge.schemas.compliance import CandidateFieldWithSource, UnifiedExtractedCandidates
from sunbridge.extraction import reset_llm_requests_counter

def test_full_graph_successful_llm_request_count():
    reset_llm_requests_counter()
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

    mock_parsed = UnifiedExtractedCandidates(
        candidates=[
            CandidateFieldWithSource(
                source_id="source_1",
                field_name="model_name",
                normalized_value="SUN-5K-G06P3-EU-AM2-P1"
            ),
            CandidateFieldWithSource(
                source_id="source_1",
                field_name="weight",
                normalized_value="11",
                raw_value="11 kg"
            ),
            CandidateFieldWithSource(
                source_id="source_3",
                field_name="weight",
                normalized_value="18",
                raw_value="18 kg"
            )
        ]
    )

    mock_choice = MagicMock()
    mock_choice.message.parsed = mock_parsed
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("sunbridge.extraction.extractor.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.beta.chat.completions.parse.return_value = mock_response

        with patch.object(settings, "llm_api_key", "sk-test-key"):
            final_state = pipeline.invoke(initial_state)

    # Hard Assertion: Exactly 1 LLM HTTP call across the entire pipeline
    assert final_state["llm_requests_made"] == 1
    assert final_state["extraction_mode"] == "LLM"
    assert mock_client.beta.chat.completions.parse.call_count == 1
    assert final_state["is_valid"] is True

def test_full_graph_429_rate_limit_request_count():
    reset_llm_requests_counter()
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

    rate_limit_err = openai.RateLimitError(
        message="429 Too Many Requests",
        response=MagicMock(status_code=429),
        body=None
    )

    with patch("sunbridge.extraction.extractor.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.beta.chat.completions.parse.side_effect = rate_limit_err

        with patch.object(settings, "llm_api_key", "sk-test-key"):
            final_state = pipeline.invoke(initial_state)

    # Hard Assertion: Exactly 1 LLM HTTP call, 0 SDK retries, fallback to RULE_BASED
    assert final_state["llm_requests_made"] == 1
    assert final_state["extraction_mode"] == "RULE_BASED"
    assert final_state["llm_error"] == "RATE_LIMITED"
    assert mock_client.beta.chat.completions.parse.call_count == 1
    assert final_state["is_valid"] is True
