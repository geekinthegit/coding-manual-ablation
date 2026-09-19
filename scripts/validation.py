"""Shared response validation and error classification.

Imported by both run_experiment.py (at call time) and parse_attempts.py (when
re-deriving labels from raw_response), so that the two can never disagree on
what counts as a valid label.

* validate_body   -- 5.4.4 normalization, 5.4.5 validity, 5.6.7 invalid_reason
                     order (first match wins).
* classify_http_status / error_code_from_body -- 5.4.6 as revised 2026-09-18:
                     429 is retryable unless its body error code marks a quota
                     or billing condition; other 4xx are fatal; 5xx retryable.
* parse_retry_after -- Retry-After header as seconds (delta-seconds or HTTP
                     date); None when absent or unparseable.

No network access and no openai import: this module only inspects strings.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from tags import TAG_TO_CATEGORY

# Same expression as test_api_request.CATEGORIES (the schema enum); a test
# asserts the two lists are identical.
CATEGORIES = [TAG_TO_CATEGORY[t] for t in sorted(TAG_TO_CATEGORY)]

OUTCOMES = ("success", "invalid_response", "retryable_error", "fatal_error")
INVALID_REASONS = (
    "refusal",
    "truncated",
    "finish_reason_other",
    "malformed_json",
    "schema_mismatch",
    "label_not_in_enum",
)

# 429 codes that waiting does not resolve (5.4.6 revised 2026-09-18).
# Unknown or missing codes are retryable.
NON_RETRYABLE_429_CODES = frozenset({
    "insufficient_quota",
    "billing_hard_limit_reached",
    "billing_not_active",
})


@dataclass(frozen=True)
class ValidationResult:
    outcome: str                      # "success" or "invalid_response"
    invalid_reason: str | None
    category: str | None              # normalized canonical name on success
    finish_reason: str | None
    response_model: str | None
    system_fingerprint: str | None
    usage: dict | None


def normalize_category(value: str) -> str:
    """5.4.4: strip leading/trailing whitespace only; no other transformation."""
    return value.strip()


def validate_body(body_text: str) -> ValidationResult:
    """Classify one HTTP 200 Chat Completions body (as text) per 5.4.5 / 5.6.7."""
    finish_reason = response_model = system_fingerprint = None
    usage = None

    def invalid(reason: str) -> ValidationResult:
        return ValidationResult("invalid_response", reason, None, finish_reason,
                                response_model, system_fingerprint, usage)

    try:
        body = json.loads(body_text)
    except (TypeError, ValueError):
        return invalid("malformed_json")
    if not isinstance(body, dict):
        return invalid("malformed_json")

    response_model = body.get("model")
    system_fingerprint = body.get("system_fingerprint")
    usage = body.get("usage") if isinstance(body.get("usage"), dict) else None

    choices = body.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return invalid("schema_mismatch")
    choice = choices[0]
    message = choice.get("message") if isinstance(choice.get("message"), dict) else {}
    finish_reason = choice.get("finish_reason")

    # Classification order fixed in 5.6.7; first match wins.
    if message.get("refusal") is not None:
        return invalid("refusal")
    if finish_reason == "length":
        return invalid("truncated")
    if finish_reason != "stop":
        return invalid("finish_reason_other")

    content = message.get("content")
    try:
        parsed = json.loads(content)
    except (TypeError, ValueError):
        return invalid("malformed_json")
    if not isinstance(parsed, dict) or set(parsed.keys()) != {"category"}:
        return invalid("schema_mismatch")
    raw_category = parsed["category"]
    if not isinstance(raw_category, str):
        return invalid("schema_mismatch")

    category = normalize_category(raw_category)
    if category not in CATEGORIES:
        return invalid("label_not_in_enum")
    return ValidationResult("success", None, category, finish_reason,
                            response_model, system_fingerprint, usage)


def error_code_from_body(body_text: str | None) -> str | None:
    """Return the error code from an OpenAI error body, or None."""
    if not body_text:
        return None
    try:
        body = json.loads(body_text)
    except (TypeError, ValueError):
        return None
    if not isinstance(body, dict):
        return None
    err = body.get("error")
    if isinstance(err, dict):
        code = err.get("code")
    else:
        code = body.get("code")
    return code if isinstance(code, str) else None


def classify_http_status(status_code: int | None, error_code: str | None) -> str:
    """Return "retryable_error" or "fatal_error" for a non-200 status (5.4.6 revised)."""
    if status_code is None:            # no HTTP response: connection error / timeout
        return "retryable_error"
    if status_code == 429:
        return "fatal_error" if error_code in NON_RETRYABLE_429_CODES else "retryable_error"
    if status_code >= 500:
        return "retryable_error"
    return "fatal_error"


def parse_retry_after(value: str | None, now: datetime | None = None) -> float | None:
    """Return Retry-After as non-negative seconds, or None if absent/unparseable."""
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        seconds = float(text)
        return seconds if seconds >= 0 else None
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(text)
    except (TypeError, ValueError, IndexError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    now = now or datetime.now(timezone.utc)
    return max(0.0, (when - now).total_seconds())
