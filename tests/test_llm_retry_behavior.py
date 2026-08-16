import pytest
from unittest.mock import MagicMock, patch
import openai
from sunbridge.config import settings
from sunbridge.ingestion.sources import get_all_sources
from sunbridge.parsing import parse_text_document
from sunbridge.extraction.extractor import extract_all_evidence_unified

def test_openai_client_max_retries_zero():
    sources = get_all_sources("http://example.com/dummy.pdf")
    docs = [parse_text_document(s) for s in sources]

    with patch("sunbridge.extraction.extractor.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Stop execution")

        with patch.object(settings, "llm_api_key", "sk-test-key"):
            extract_all_evidence_unified(docs)

        mock_openai_cls.assert_called_once()
        _, kwargs = mock_openai_cls.call_args
        assert kwargs.get("max_retries") == 0, f"Expected max_retries=0, but got {kwargs.get('max_retries')}"

def test_429_does_not_trigger_sdk_retries():
    sources = get_all_sources("http://example.com/dummy.pdf")
    docs = [parse_text_document(s) for s in sources]

    rate_limit_err = openai.RateLimitError(
        message="429 Rate Limit Exceeded",
        response=MagicMock(status_code=429),
        body=None
    )

    with patch("sunbridge.extraction.extractor.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.side_effect = rate_limit_err

        with patch.object(settings, "llm_api_key", "sk-test-key"):
            records, mode, llm_err, reqs = extract_all_evidence_unified(docs)

    assert mock_client.chat.completions.create.call_count == 1
    assert mode == "RULE_BASED"
    assert llm_err == "RATE_LIMITED"
