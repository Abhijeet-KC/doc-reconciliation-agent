import pytest
import json
from unittest.mock import MagicMock, patch
import openai
from sunbridge.config import settings
from sunbridge.ingestion.sources import get_all_sources
from sunbridge.parsing import parse_text_document
from sunbridge.extraction.extractor import (
    sanitize_json_text,
    extract_all_evidence_unified,
    reset_llm_requests_counter
)
from sunbridge.schemas.compliance import CandidateFieldWithSource, UnifiedExtractedCandidates

def test_sanitize_json_text_valid():
    raw = '{"candidates": [{"source_id": "source_1", "field_name": "model_name", "normalized_value": "SUN-5K"}]}'
    cleaned = sanitize_json_text(raw)
    assert cleaned == raw
    data = json.loads(cleaned)
    assert "candidates" in data

def test_sanitize_json_text_fenced():
    raw = '''```json
{
  "candidates": [
    {"source_id": "source_1", "field_name": "ip_rating", "normalized_value": "IP65"}
  ]
}
```'''
    cleaned = sanitize_json_text(raw)
    data = json.loads(cleaned)
    assert data["candidates"][0]["field_name"] == "ip_rating"

def test_sanitize_json_text_surrounding_prose():
    raw = '''Here is the extracted json output:
{
  "candidates": [
    {"source_id": "source_2", "field_name": "buyer_name", "normalized_value": "SunBridge"}
  ]
}
Hope this helps!'''
    cleaned = sanitize_json_text(raw)
    data = json.loads(cleaned)
    assert data["candidates"][0]["normalized_value"] == "SunBridge"

def test_malformed_json_fallback_single_request():
    reset_llm_requests_counter()
    sources = get_all_sources("http://example.com/dummy.pdf")
    docs = [parse_text_document(s) for s in sources]

    mock_choice = MagicMock()
    mock_choice.finish_reason = "stop"
    mock_choice.message.content = '{"candidates": [{"source_id": "source_1", "field_name": "model_name", "normalized_value": ' # broken JSON
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("sunbridge.extraction.extractor.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(settings, "llm_api_key", "sk-test-key"):
            records, mode, llm_err, reqs = extract_all_evidence_unified(docs)

    assert reqs == 1
    assert mode == "RULE_BASED"
    assert llm_err == "INVALID_RESPONSE"
    assert mock_client.chat.completions.create.call_count == 1
    assert len(records) > 0

def test_truncated_json_fallback_single_request():
    reset_llm_requests_counter()
    sources = get_all_sources("http://example.com/dummy.pdf")
    docs = [parse_text_document(s) for s in sources]

    mock_choice = MagicMock()
    mock_choice.finish_reason = "length" # truncated finish reason
    mock_choice.message.content = '{"candidates": [{"source_id": "source_1", "field_name": "model_name"'
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch("sunbridge.extraction.extractor.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create.return_value = mock_response

        with patch.object(settings, "llm_api_key", "sk-test-key"):
            records, mode, llm_err, reqs = extract_all_evidence_unified(docs)

    assert reqs == 1
    assert mode == "RULE_BASED"
    assert llm_err == "TRUNCATED_RESPONSE"
    assert mock_client.chat.completions.create.call_count == 1

def test_compact_schema_instantiation():
    cand = CandidateFieldWithSource(
        source_id="source_1",
        field_name="weight",
        normalized_value="11",
        unit="kg"
    )
    container = UnifiedExtractedCandidates(candidates=[cand])
    dump = container.model_dump()
    assert dump["candidates"][0]["field_name"] == "weight"
