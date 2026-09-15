"""Technical test call for the API request specification (5.3).

Verifies that the selected endpoint, snapshot, generation settings, and
structured-output schema operate together. Uses synthetic input only;
no development-set utterance is sent. The returned category is NOT
evaluated for correctness. See decisions/05-3-call-unit-and-api-request.md,
section 6.
"""

import json
import os
import platform
import sys
from datetime import datetime, timezone

import openai
import tiktoken
from openai import OpenAI

from tags import TAG_TO_CATEGORY

MODEL = "gpt-5.5-2026-04-23"

# Provisional value for the technical test only. The final limit is fixed
# in 5.3.5 after usage.completion_tokens and finish_reason are inspected.
OUTPUT_TOKEN_LIMIT = 64

# The seven canonical names come from tags.py so that the enum cannot
# drift from the label set used in parsing and scoring.
CATEGORIES = [TAG_TO_CATEGORY[t] for t in sorted(TAG_TO_CATEGORY)]

# Single required field, enum-restricted, no extra properties, strict.
SCHEMA = {
    "name": "talkmove_category",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "category": {"type": "string", "enum": CATEGORIES}
        },
        "required": ["category"],
        "additionalProperties": False,
    },
}

# Synthetic input: not from the corpus, not the real coding manual.
# The content only needs to exercise the request path.
SYNTHETIC_PROMPT = """Task: Read the short manual below, then assign the target line to exactly one category.

Manual (synthetic, for technical testing only):
- Category A is used when the speaker asks a question.
- Category B is used when the speaker makes a statement.
- Otherwise the line is not coded.

Context:
S: Test line one.
T: Test line two.
[TARGET] T: Is this a test?
S: Test line four.

Output instruction: Respond with one category name from the allowed list."""


def main() -> int:
    # Environment record required by 5.2.3 for every calling script.
    env_line = (
        f"python: {platform.python_version()}, "
        f"openai: {openai.__version__}, "
        f"tiktoken: {tiktoken.__version__}"
    )

    # Project key only; never the default OPENAI_API_KEY (course key).
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY_ABLATION"])

    request = {
        "model": MODEL,
        "messages": [{"role": "user", "content": SYNTHETIC_PROMPT}],
        "temperature": 0,
        "reasoning_effort": "none",
        # Parameter name is itself under test: if openai 3.8.0 rejects it,
        # create() raises and the traceback is the test record.
        "max_completion_tokens": OUTPUT_TOKEN_LIMIT,
        "response_format": {"type": "json_schema", "json_schema": SCHEMA},
    }

    called_at = datetime.now(timezone.utc).isoformat()
    # Any rejected parameter raises here; reaching the next line means
    # checks 1, 3, 4, 5, 6 passed (request accepted with all settings).
    response = client.chat.completions.create(**request)

    choice = response.choices[0]
    raw_content = choice.message.content
    finish_reason = choice.finish_reason
    usage = response.usage

    parsed = json.loads(raw_content)
    category = parsed.get("category")

    # Checks numbered as in 5.3 section 6. Items 1, 3-6 are True because
    # the call returned without an exception; they are not computed.
    checks = {
        "1_request_accepted": True,
        "2_snapshot_returned": response.model == MODEL,
        "3_temperature_0_accepted": True,
        "4_reasoning_effort_none_accepted": True,
        "5_structured_output_accepted": True,
        "6_combo_ok": True,
        "7_schema_valid_category": category in CATEGORIES,
        "8_parser_unambiguous": set(parsed.keys()) == {"category"},
        "9_not_truncated": finish_reason == "stop",
        "10_usage_available": usage is not None,
    }

    # Check 11: reasoning tokens under structured output. Recorded, not
    # judged; a nonzero value updates 5.2.2 rather than failing the test.
    reasoning_tokens = None
    details = getattr(usage, "completion_tokens_details", None)
    if details is not None:
        reasoning_tokens = getattr(details, "reasoning_tokens", None)
    checks["11_reasoning_tokens"] = reasoning_tokens

    # Full record: environment, request (minus prompt body, shown
    # separately), raw response before parsing, parsed value, finish
    # status, usage.
    lines = [
        f"environment: {env_line}",
        f"called_at_utc: {called_at}",
        "endpoint: chat.completions",
        f"model_requested: {MODEL}",
        f"model_returned: {response.model}",
        f"request_parameters: {json.dumps({k: v for k, v in request.items() if k != 'messages'}, ensure_ascii=False)}",
        f"synthetic_prompt:\n{SYNTHETIC_PROMPT}",
        f"raw_response_content: {raw_content}",
        f"parsed_category: {category}",
        f"finish_reason: {finish_reason}",
        f"usage: {usage.model_dump_json() if hasattr(usage, 'model_dump_json') else usage}",
        "checks:",
    ]
    for k, v in checks.items():
        lines.append(f"  {k}: {v}")

    report = "\n".join(lines)
    print(report)

    # Report goes to reports/ (committed separately, after the script).
    out_path = f"../reports/api-request-test-{called_at[:10]}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"\nreport written: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())