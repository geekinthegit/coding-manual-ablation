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
    # the five non-retryable codes (OpenAI Help Center, checked 2026-09-19)
    (429, "insufficient_quota", "fatal_error"),
    (429, "credit_balance_exhausted", "fatal_error"),
    (429, "organization_usage_limit_exceeded", "fatal_error"),
    (429, "organization_spend_limit_exceeded", "fatal_error"),
    (429, "project_spend_limit_exceeded", "fatal_error"),
    # removed 2026-09-19: no longer in the documented list, so unknown -> retryable
    (429, "billing_hard_limit_reached", "retryable_error"),
    (429, "billing_not_active", "retryable_error"),
    (500, None, "retryable_error"),
    (503, "server_error", "retryable_error"),
    (401, "invalid_api_key", "fatal_error"),
    (400, None, "fatal_error"),
    (None, None, "retryable_error"),
])
def test_429_and_status_classification(status, code, expected):
    assert v.classify_http_status(status, code) == expected                 # error_type omitted
    assert v.classify_http_status(status, code, "synthetic") == expected    # unknown type


def test_non_retryable_code_set_is_exactly_the_documented_five():
    assert v.NON_RETRYABLE_429_CODES == {
        "insufficient_quota", "credit_balance_exhausted", "organization_usage_limit_exceeded",
        "organization_spend_limit_exceeded", "project_spend_limit_exceeded",
    }
    assert v.NON_RETRYABLE_429_TYPE == "insufficient_quota"


@pytest.mark.parametrize("code,error_type,expected", [
    ("rate_limit_exceeded", "insufficient_quota", "fatal_error"),   # type wins over unrelated code
    ("something_new", "insufficient_quota", "fatal_error"),
    (None, "insufficient_quota", "fatal_error"),
    ("rate_limit_exceeded", "tokens", "retryable_error"),
    ("rate_limit_exceeded", None, "retryable_error"),
    ("something_new", "something_else", "retryable_error"),         # unknown code and type
    (None, None, "retryable_error"),
    ("project_spend_limit_exceeded", "requests", "fatal_error"),    # code wins over unrelated type
])
def test_429_classification_by_error_type(code, error_type, expected):
    assert v.classify_http_status(429, code, error_type) == expected


def test_error_type_only_applies_to_429():
    # error.type = insufficient_quota on a 5xx does not change the status-based rule
    assert v.classify_http_status(500, None, "insufficient_quota") == "retryable_error"
    assert v.classify_http_status(400, None, "insufficient_quota") == "fatal_error"


def test_error_code_from_body():
    assert v.error_code_from_body(json.dumps({"error": {"code": "insufficient_quota"}})) == "insufficient_quota"
    assert v.error_code_from_body(json.dumps({"error": {"code": None}})) is None
    assert v.error_code_from_body("not json") is None
    assert v.error_code_from_body(None) is None


def test_error_type_from_body():
    body = json.dumps({"error": {"code": "rate_limit_exceeded", "type": "insufficient_quota"}})
    assert v.error_type_from_body(body) == "insufficient_quota"
    assert v.error_code_from_body(body) == "rate_limit_exceeded"
    assert v.error_type_from_body(json.dumps({"error": {"code": "x"}})) is None
    assert v.error_type_from_body(json.dumps({"error": {"type": 3}})) is None
    assert v.error_type_from_body("not json") is None
    assert v.error_type_from_body(None) is None


def test_parse_retry_after():
    now = datetime(2026, 9, 18, 12, 0, 0, tzinfo=timezone.utc)
    assert v.parse_retry_after("7") == 7.0
    assert v.parse_retry_after(" 2.5 ") == 2.5
    assert v.parse_retry_after("Thu, 18 Sep 2026 12:00:30 GMT", now) == 30.0
    assert v.parse_retry_after("Thu, 18 Sep 2026 11:00:00 GMT", now) == 0.0
    assert v.parse_retry_after("soon") is None
    assert v.parse_retry_after("-1") is None
    assert v.parse_retry_after(None) is None
