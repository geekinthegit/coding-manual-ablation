"""Shared response validation and error classification.

Imported by both run_experiment.py (at call time) and parse_attempts.py (when
re-deriving labels from raw_response), so that the two can never disagree on
what counts as a valid label.

* validate_body   -- 5.4.4 normalization, 5.4.5 validity, 5.6.7 invalid_reason
                     order (first match wins).
* classify_http_status / error_code_from_body / error_type_from_body --
                     5.4.6 as revised 2026-09-19: 429 is retryable unless its
                     body error.code is in NON_RETRYABLE_429_CODES or its
                     error.type is "insufficient_quota"; other 4xx are fatal;
                     5xx retryable.
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

# 429 error.code values that waiting does not resolve (5.4.6 revised 2026-09-19).
# Source: OpenAI Help Center, "Troubleshooting API rate limits and 429 errors",
# checked 2026-09-19. Unknown or missing codes are retryable.
NON_RETRYABLE_429_CODES = frozenset({
    "insufficient_quota",
    "credit_balance_exhausted",
    "organization_usage_limit_exceeded",
    "organization_spend_limit_exceeded",
    "project_spend_limit_exceeded",
})
# Same source: billing-related errors may carry this error.type regardless of
# error.code, so a 429 with this type is non-retryable whatever its code.
NON_RETRYABLE_429_TYPE = "insufficient_quota"


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


def _error_field_from_body(body_text: str | None, key: str) -> str | None:
    """Return the string field ``key`` of an OpenAI error body, or None."""
    if not body_text:
        return None
    try:
        body = json.loads(body_text)
    except (TypeError, ValueError):
        return None
    if not isinstance(body, dict):
        return None
    err = body.get("error")
    value = err.get(key) if isinstance(err, dict) else body.get(key)
    return value if isinstance(value, str) else None


def error_code_from_body(body_text: str | None) -> str | None:
    """Return error.code from an OpenAI error body, or None (input to 5.4.6).

    5.4.6 defines the 429 rule on the response body rather than on the SDK
    exception, so the code is read from the same body text that 5.6.7 stores in
    the attempt record; the classification can then be re-checked afterwards
    from the record alone. A body that is missing, not JSON, or carrying a
    non-string code yields None, which 5.4.6 treats as unknown and therefore
    retryable: inferring a code from an unreadable body would turn a transport
    problem into a halt the decision does not authorise.
    """
    return _error_field_from_body(body_text, "code")


def error_type_from_body(body_text: str | None) -> str | None:
    """Return error.type from an OpenAI error body, or None (input to 5.4.6).

    5.4.6 makes error.type = "insufficient_quota" non-retryable whatever
    error.code says, because billing conditions may arrive under codes this
    project has not enumerated. Read separately from error_code_from_body so
    that either field on its own can decide the outcome.
    """
    return _error_field_from_body(body_text, "type")


def classify_http_status(status_code: int | None, error_code: str | None,
                         error_type: str | None = None) -> str:
    """Return "retryable_error" or "fatal_error" for a non-200 status (5.4.6 revised 2026-09-19).

    A 429 is fatal when error.code is in NON_RETRYABLE_429_CODES or error.type
    equals NON_RETRYABLE_429_TYPE; any other, missing or unknown code/type is
    retryable.
    """
    if status_code is None:            # no HTTP response: connection error / timeout
        return "retryable_error"
    if status_code == 429:
        non_retryable = (error_code in NON_RETRYABLE_429_CODES
                         or error_type == NON_RETRYABLE_429_TYPE)
        return "fatal_error" if non_retryable else "retryable_error"
    if status_code >= 500:
        return "retryable_error"
    return "fatal_error"


def parse_retry_after(value: str | None, now: datetime | None = None) -> float | None:
    """Return Retry-After as non-negative seconds, or None (5.6.4 wait source).

    Under 5.6.4 a parseable Retry-After is the wait before the next attempt
    (wait_source "retry_after") and backoff applies only when the header is
    absent or unparseable. An unreadable header must therefore be reported as
    None and not as 0.0, which would retry immediately. Both the delta-seconds
    and the HTTP-date form are accepted because either may be sent, and a date
    already past gives 0.0 rather than a negative wait.

    The value is deliberately not capped here: 5.6.4 requires a Retry-After
    above backoff_max to be recorded unclipped and to stop the run, so the
    comparison belongs to the caller, not to the parser.
    """
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
