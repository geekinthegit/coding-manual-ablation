## 5.3 Call unit and API request

[decided 2026-09-15; proposed 2026-09-15] Promoted after the technical verification recorded in 5.3.9.

This section defines the API request structure used across all experimental conditions.

### 5.3.1 Endpoint

The endpoint is Chat Completions.

The experiment had already produced a successful validation call through Chat Completions (5.2.1). No change of endpoint was introduced because no technical incompatibility appeared during structured-output testing (5.3.9).

The endpoint is held constant across all experimental conditions.

### 5.3.2 Message-role structure

The complete experimental prompt is sent as one `user` message. No `developer` or `system` message contains the coding manual or other experimental instructions.

This choice keeps the experimental manipulation at the level of prompt text. Placing the coding manual in a higher-priority instruction role would make the manipulated object not merely the manual text but the manual text in a distinct API instruction hierarchy. A single user message therefore matches the research question, which concerns changes produced by replacing specific components of the coding manual.

A secondary implementation advantage is that the researcher-constructed prompt can be treated as one continuous text sequence for token-count and token-position verification (3.2.3).

### 5.3.3 Prompt-content order

The order decided in 5.1.4 is retained:

1. Task instruction
2. Coding manual
3. Context and target utterance
4. Output instruction

These components appear in this order within the single `user` message. The ordering itself is not reopened here.

### 5.3.4 Structured output

Structured output is used for all experimental conditions.

The response contains a single required field, `category`, restricted to exactly one of the seven canonical category names defined in `scripts/tags.py`:

* Not coded
* Keeping Everyone Together
* Getting Students to Relate
* Restating
* Revoicing
* Pressing for Accuracy
* Pressing for Reasoning

No explanatory text, confidence score, rationale, or additional output field is requested.

The schema rejects additional properties (`additionalProperties: false`) and uses strict schema enforcement (`strict: true`). Both were accepted by the selected snapshot and endpoint (5.3.9).

The identical output schema is used for the baseline, all component-replacement conditions, the negative control, and the names-only reference.

### 5.3.5 Model and generation settings

The following settings, decided in 5.2, are retained and were not reopened:

* Model snapshot: `gpt-5.5-2026-04-23`
* Tokenizer: `o200k_base`
* Temperature: `0`
* Reasoning effort: `none`

Output-token limit. The parameter name was not entered into this specification until verified against the installed `openai 3.8.0` client. Verified name: `max_completion_tokens`. A provisional value of 64 was used for the technical test; the observed output was 14 completion tokens with `finish_reason = stop`. The limit is fixed at 64 for all conditions.

### 5.3.6 Technical verification call

Before promotion to `[decided]`, a technical test call was performed using synthetic input rather than a development-set or experimental utterance. The purpose was API and pipeline verification, not classification-performance evaluation; the returned category was not evaluated for correctness.

The test verified:

1. The selected endpoint accepts the request.
2. The specified model snapshot is accessible and is returned unchanged in the response.
3. `temperature = 0` is accepted.
4. `reasoning_effort = none` is accepted.
5. Structured output with the proposed schema is accepted.
6. Structured output and `reasoning_effort = none` operate successfully in the same request.
7. The returned response satisfies the seven-category schema.
8. The planned parser extracts the category without ambiguity.
9. The response is not truncated under the tested output-token limit.
10. Usage metadata is available and recorded.
11. Reasoning-token usage is checked explicitly, including whether `reasoning_tokens = 0` remains true when structured output is enabled.

Rule fixed before the test: if structured output had caused nonzero reasoning-token usage, the existing 5.2.2 record stating `reasoning_tokens = 0` would have been updated rather than treating the discrepancy as a test failure.

### 5.3.7 Success criterion

The specification was finalized when the technical test confirmed that the endpoint accepts all required settings together; the model returns a schema-valid category; the parser processes the returned object successfully; the output is not truncated; and no unsupported or ambiguous request setting remains.

### 5.3.8 Freezing rule

The API request structure is finalized before the procedural pilot and before main-experiment data collection.

The following remain identical across experimental conditions: endpoint; message-role structure; prompt-component order; output schema; model snapshot; generation settings; output-token limit; and output parsing procedure.

If the request structure is changed after token-matching or prompt-input verification has been completed, all affected inputs must be revalidated before experimental use.

### 5.3.9 Verification record

Technical test performed 2026-09-15T02:38:28Z with `scripts/test_api_request.py` (commit 062ab0b). Environment: Python 3.13.9, openai 3.8.0, tiktoken 0.14.0.

* Endpoint: chat.completions. Model requested and returned: `gpt-5.5-2026-04-23`.
* Request parameters: `temperature=0`, `reasoning_effort="none"`, `max_completion_tokens=64`, `response_format` = json_schema (strict, single field `category`, seven-name enum, `additionalProperties: false`).
* Input: synthetic prompt, recorded in full in the report; no corpus text.
* Raw response: `{"category":"Not coded"}`. Parsed category in enum. `finish_reason = stop`.
* Usage: prompt 170, completion 14, total 184; `reasoning_tokens = 0`; `cached_tokens = 0`.
* All eleven checks in 5.3.6 passed. `reasoning_tokens = 0` holds with structured output enabled; the 5.2.2 record stands.

Full record: `reports/api-request-test-2026-09-15.txt`.

### 5.3.10 Call unit, request independence, and call order

[proposed 2026-09-15]

One utterance per call. Each API call codes exactly one target utterance. Multiple targets are not batched into one request, because labels produced within one response are not independent of each other and the repetition procedure (5.4) is defined per utterance.

Independent requests. Every call is a new request with no conversation history, no prior output, and no continuation state. Utterance, condition, and repetition changes each produce a separate request.

Call order. The execution order of utterance × condition × repetition is shuffled with a recorded seed so that no condition is systematically executed in a distinct time period. Block-level shuffling is permitted if full interleaving is impractical; the method used and its purpose (preventing time-of-execution from coinciding with condition) are recorded. This rule is an additional control of this study rather than a requirement drawn from the workflow literature. Concurrency and retry placement are fixed in the runner specification (roadmap 7).