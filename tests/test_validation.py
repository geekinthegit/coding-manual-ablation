"""validation.py: invalid_reason classification and order (5.6.7), 429 codes (5.4.6 revised)."""

import json
from datetime import datetime, timezone

import pytest

import validation as v
from test_api_request import SCHEMA
from tests.conftest import ok_body


def test_categories_match_schema_enum():
    assert v.CATEGORIES == SCHEMA["schema"]["properties"]["category"]["enum"]
    assert len(v.CATEGORIES) == 7


def test_success_normalizes_whitespace_only():
    r = v.validate_body(ok_body(category="  Revoicing\n"))
    assert (r.outcome, r.invalid_reason, r.category) == ("success", None, "Revoicing")
    assert r.finish_reason == "stop" and r.usage["total_tokens"] == 15


@pytest.mark.parametrize("body,reason", [
    (ok_body(refusal="I cannot help"), "refusal"),
    (ok_body(finish="length"), "truncated"),
    (ok_body(finish="content_filter"), "finish_reason_other"),
    (ok_body(content="not json"), "malformed_json"),
    (ok_body(extra_fields={"confidence": 0.9}), "schema_mismatch"),
    (ok_body(content=json.dumps({"label": "Restating"})), "schema_mismatch"),
    (ok_body(content=json.dumps({"category": 3})), "schema_mismatch"),
    (ok_body(category="revoicing"), "label_not_in_enum"),
    (ok_body(category="Pressing for accuracy"), "label_not_in_enum"),
    ("<html>", "malformed_json"),
])
def test_each_invalid_reason(body, reason):
    r = v.validate_body(body)
    assert (r.outcome, r.invalid_reason, r.category) == ("invalid_response", reason, None)


def test_classification_order_first_match_wins():
    # refusal beats length beats other beats malformed content
    assert v.validate_body(ok_body(refusal="no", finish="length", content="x")).invalid_reason == "refusal"
    assert v.validate_body(ok_body(finish="length", content="x")).invalid_reason == "truncated"
    assert v.validate_body(ok_body(finish="tool_calls", content="x")).invalid_reason == "finish_reason_other"
    assert v.validate_body(ok_body(content="x", finish="stop")).invalid_reason == "malformed_json"
    # schema mismatch is checked before enum membership
    assert v.validate_body(ok_body(category="nope", extra_fields={"a": 1})).invalid_reason == "schema_mismatch"


@pytest.mark.parametrize("status,code,expected", [
    (429, "rate_limit_exceeded", "retryable_error"),
    (429, None, "retryable_error"),
    (429, "something_new", "retryable_error"),
    (429, "insufficient_quota", "fatal_error"),
    (429, "billing_hard_limit_reached", "fatal_error"),
    (429, "billing_not_active", "fatal_error"),
    (500, None, "retryable_error"),
    (503, "server_error", "retryable_error"),
    (401, "invalid_api_key", "fatal_error"),
    (400, None, "fatal_error"),
    (None, None, "retryable_error"),
])
def test_429_and_status_classification(status, code, expected):
    assert v.classify_http_status(status, code) == expected


def test_error_code_from_body():
    assert v.error_code_from_body(json.dumps({"error": {"code": "insufficient_quota"}})) == "insufficient_quota"
    assert v.error_code_from_body(json.dumps({"error": {"code": None}})) is None
    assert v.error_code_from_body("not json") is None
    assert v.error_code_from_body(None) is None


def test_parse_retry_after():
    now = datetime(2026, 9, 18, 12, 0, 0, tzinfo=timezone.utc)
    assert v.parse_retry_after("7") == 7.0
    assert v.parse_retry_after(" 2.5 ") == 2.5
    assert v.parse_retry_after("Thu, 18 Sep 2026 12:00:30 GMT", now) == 30.0
    assert v.parse_retry_after("Thu, 18 Sep 2026 11:00:00 GMT", now) == 0.0
    assert v.parse_retry_after("soon") is None
    assert v.parse_retry_after("-1") is None
    assert v.parse_retry_after(None) is None
