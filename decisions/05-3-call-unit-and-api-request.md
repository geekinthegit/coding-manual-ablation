# API Request Specification

## Status

[proposed 2026-09-15]

This specification defines the API request structure to be used across all experimental conditions. It will be promoted to `[decided]` only after a technical test call confirms that the selected endpoint, model snapshot, generation settings, and structured-output configuration operate together as intended.

## 1. Endpoint

Proposed endpoint: **Chat Completions**.

The experiment has already produced a successful validation call through Chat Completions. No change of endpoint is introduced unless required by a technical incompatibility discovered during structured-output testing.

The endpoint will be held constant across all experimental conditions.

## 2. Message-role structure

The complete experimental prompt will be sent as **one `user` message**. No `developer` or `system` message will contain the coding manual or other experimental instructions.

This choice keeps the experimental manipulation at the level of prompt text. Placing the coding manual in a higher-priority instruction role would make the manipulated object not merely the manual text but the manual text in a distinct API instruction hierarchy. A single user message therefore better matches the research question, which concerns changes produced by replacing specific components of the coding manual.

A secondary implementation advantage is that the researcher-constructed prompt can be treated as one continuous text sequence for token-count and token-position verification.

## 3. Prompt-content order

The previously decided prompt order is retained:

1. Task instruction
2. Coding manual
3. Context and target utterance
4. Output instruction

These components will appear in this order within the single `user` message.

The ordering itself is not reopened at this stage.

## 4. Structured output

Structured output is proposed for all experimental conditions.

The response will contain a single required field:

`category`

The value of `category` will be restricted to exactly one of the seven canonical category names:

* Not coded
* Keeping Everyone Together
* Getting Students to Relate
* Restating
* Revoicing
* Pressing for Accuracy
* Pressing for Reasoning

No explanatory text, confidence score, rationale, or additional output field will be requested.

The schema will reject additional properties and will use strict schema enforcement if supported by the selected model snapshot and endpoint configuration.

The identical output schema will be used for the baseline, all component-replacement conditions, the negative control, and the names-only condition.

## 5. Model and generation settings

The following previously decided settings are retained and are not reopened in this stage:

* Model snapshot: `gpt-5.5-2026-04-23`
* Tokenizer: `o200k_base`
* Temperature: `0`
* Reasoning effort: `none`

The exact API parameter name used to impose the output-token limit will not be entered into the final specification until it has been verified against the installed `openai 3.8.0` client and a successful request.

A small output-token limit will be tested because the expected response consists only of a single-field structured object. The final value will be fixed after confirming that the output is not truncated.

## 6. Technical verification call

Before this specification is promoted to `[decided]`, a small technical test call will be performed using **synthetic input rather than a development-set or experimental utterance**.

The purpose of this call is API and pipeline verification, not classification-performance evaluation.

The test will verify:

1. The selected endpoint accepts the request.
2. The specified model snapshot is accessible.
3. `temperature = 0` is accepted.
4. `reasoning_effort = none` is accepted.
5. Structured output with the proposed schema is accepted.
6. Structured output and `reasoning_effort = none` operate successfully in the same request.
7. The returned response satisfies the seven-category schema.
8. The planned parser can extract the category without ambiguity.
9. The response is not truncated under the tested output-token limit.
10. Usage metadata is available and recorded.
11. The reported reasoning-token usage is checked explicitly. In particular, whether `reasoning_tokens = 0` remains true when structured output is enabled will be recorded.

If structured output causes nonzero reasoning-token usage, the existing record stating `reasoning_tokens = 0` will be updated rather than treating the discrepancy as a test failure.

## 7. Success criterion

This API request specification can be finalized when the technical test confirms that:

* the endpoint accepts all required settings together;
* the model returns a schema-valid category;
* the parser processes the returned object successfully;
* the output is not truncated; and
* no unsupported or ambiguous request setting remains.

Any incompatibility affecting the endpoint, message structure, structured output, or required generation settings blocks progression until resolved.

## 8. Freezing rule

The API request structure must be finalized before the procedural pilot and before main-experiment data collection.

After finalization, the following will remain identical across experimental conditions:

* endpoint;
* message-role structure;
* prompt-component order;
* output schema;
* model snapshot;
* generation settings; and
* output parsing procedure.

If the request structure is changed after token-matching or prompt-input verification has been completed, all affected inputs must be revalidated before experimental use.

## 9. Verification record

Pending technical test.

After the test, this section will record:

* test date and time;
* exact endpoint;
* exact request parameters;
* synthetic test input;
* raw response;
* parsed response;
* finish status;
* usage metadata, including reasoning-token usage;
* output-token-limit result; and
* any API errors or warnings.

Upon successful verification, the status of this document will be changed from `[proposed 2026-09-15]` to `[decided YYYY-MM-DD]`, while retaining the original proposal date in the record.
