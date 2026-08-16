import pytest
from unittest.mock import MagicMock, patch
import openai
from sunbridge.config import settings
from sunbridge.ingestion.sources import get_all_sources, SourceType
from sunbridge.parsing import parse_text_document
from sunbridge.extraction.extractor import extract_all_evidence_unified, reset_llm_requests_counter
from sunbridge.schemas.compliance import CandidateFieldWithSource, UnifiedExtractedCandidates

def test_single_llm_call_success():
    reset_llm_requests_counter()
    sources = get_all_sources("http://example.com/dummy.pdf")
    docs = [parse_text_document(s) for s in sources]

    mock_parsed = UnifiedExtractedCandidates(
        candidates=[
            CandidateFieldWithSource(
                source_id="source_1",
                field_name="model_name",
                normalized_value="SUN-5K-G06P3-EU-AM2-P1"
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
            records, mode, llm_err, reqs = extract_all_evidence_unified(docs)

    assert reqs == 1
    assert mode == "LLM"
    assert llm_err is None
    assert mock_client.beta.chat.completions.parse.call_count == 1

def test_rate_limit_429_single_call_and_fallback():
    reset_llm_requests_counter()
    sources = get_all_sources("http://example.com/dummy.pdf")
    docs = [parse_text_document(s) for s in sources]

    with patch("sunbridge.extraction.extractor.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        
        # Simulate OpenRouter 429 RateLimitError
        rate_limit_err = openai.RateLimitError(
            message="429 Too Many Requests",
            response=MagicMock(status_code=429),
            body=None
        )
        mock_client.beta.chat.completions.parse.side_effect = rate_limit_err

        with patch.object(settings, "llm_api_key", "sk-test-key"):
            records, mode, llm_err, reqs = extract_all_evidence_unified(docs)

    assert reqs == 1
    assert mode == "RULE_BASED"
    assert llm_err == "RATE_LIMITED"
    assert mock_client.beta.chat.completions.parse.call_count == 1
    assert len(records) > 0
