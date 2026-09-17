## 5.4 Repetition and label aggregation

[proposed 2026-09-17]

This section defines how repeated API calls for one item-condition are executed, how their outputs are validated, and how they are aggregated into one final label. An item-condition is one sampled utterance under one of the six prompt conditions (baseline, three component replacements, negative control, names-only reference). The rules below apply identically to all six conditions. Rationales are procedural and resource-based; no rule was chosen with reference to a desired agreement outcome.

Terminology used in this section:

* Repeat: one of the R planned independent calls for an item-condition, plus any tie-break calls added under 5.4.3.
* Attempt: one API request made to obtain the response for a repeat. A repeat may consume several attempts under 5.4.6 and 5.4.7.
* Valid response: a response that yields a valid label under 5.4.5.

### 5.4.1 Number of repeats

R = 3 independent calls per item-condition.

Because generation uses `temperature = 0` and `reasoning_effort = none` (5.3.5), the purpose of repetition is to verify the stability of the label-generation procedure, not to enlarge the sample. Three is the smallest R at which an aggregation rule over repeats is non-trivial; a larger R has no procedural justification that outweighs its cost. The planned number of calls, excluding retries and tie-break calls, is 300 utterances × 6 conditions × 3 repeats = 5,400. The magnitude of repeat-to-repeat variation actually observed is checked in the procedural pilot (5.5), not assumed here.

### 5.4.2 Aggregation rule

The final label of an item-condition is the plurality label, i.e., the label with the largest count among valid repeats.

With seven categories, a majority (more than half of repeats) is not guaranteed even when R is odd. At R = 3 the possible count patterns are 3-0, 2-1, and 1-1-1; in the first two, the plurality label coincides with the majority label, so plurality only differs from majority in the tied case, which 5.4.3 handles.

### 5.4.3 Tie handling

If two or more labels share the largest count among valid repeats, one additional independent call is made and plurality is re-evaluated over all valid repeats, including the added one. This step is repeated at most twice, so an item-condition receives at most 5 repeats in total. If a tie remains after the second additional call, the item-condition receives no final label and is recorded with reason `unresolved tie`.

A fixed cap on tie-break calls bounds the cost per item-condition and prevents open-ended calling for items that do not stabilise. Recording an unresolved tie as "no final label" rather than assigning a label by any other rule keeps the final-label procedure identical across conditions and avoids introducing a condition-dependent default.

Tie-break calls are executed in a second pass after all scheduled repeats have completed, in an order shuffled across all tied item-conditions with a recorded seed. Their placement within the run is recorded as pass 2. Concurrency and retry placement follow the runner specification (roadmap 7).

### 5.4.4 Parser normalization

The parser reads the `category` value from the response JSON, strips leading and trailing whitespace, and requires a case-sensitive exact match against one of the seven canonical category names defined in `scripts/tags.py` (listed in 5.3.4). No other transformation (case folding, punctuation removal, fuzzy matching, synonym mapping) is applied.

The strict enum schema (5.3.4) should prevent any string outside the seven names from being returned. The parser rule is nevertheless specified independently of the schema so that label validity does not depend on the API enforcing the schema correctly, and so that any deviation is detected rather than silently accepted.

### 5.4.5 Valid-label criterion

A response yields a valid label if and only if parsing under 5.4.4 succeeds with exactly one of the seven canonical names. The following are all classified as invalid responses:

* `finish_reason` is not `stop` (e.g., `length`, `content_filter`).
* A `refusal` field is present in the message.
* The response content cannot be parsed as JSON.
* The `category` field is missing, or any additional field is present.
* The `category` value is outside the seven-name enum after normalization.

`Not coded` is a valid substantive label and is never merged with, or used as a fallback for, an invalid response.

Invalid responses and the substantive category `Not coded` answer different questions: the former means no label was obtained, the latter is a coder decision that the utterance does not fit any talk move. Conflating them would bias the `Not coded` count in whichever condition produces more invalid responses.

### 5.4.6 Retryable errors

The following outcomes are retried as a new attempt within the same repeat, with exponential backoff: network errors, timeouts, HTTP 429, and HTTP 5xx. An invalid response under 5.4.5 is also treated as "no label obtained" and retried under the same rule.

HTTP 4xx responses other than 429 (e.g., authentication errors, malformed requests) are not retried; the run is halted and the error is reported.

Transient transport and rate-limit failures do not carry information about the utterance or the condition, so retrying them is appropriate. Client-side 4xx errors indicate a configuration or request defect that would affect all subsequent calls, so continuing the run would produce systematically compromised records.

### 5.4.7 Maximum attempts per repeat

Each repeat is allowed at most 3 attempts. Every attempt, successful or not, is written to the raw log with its request parameters, timestamp, raw response or error, and attempt index.

A fixed attempt cap bounds cost and run time under persistent failures. Logging all attempts, not only the accepted one, preserves the record needed to verify afterwards that the retry rule was applied as specified.

### 5.4.8 Handling after retry exhaustion

If a repeat has no valid response after 3 attempts, that repeat is recorded as invalid. Aggregation (5.4.2) is then performed over valid repeats only, and only when at least 2 valid repeats exist:

* If the valid repeats are 2 and their labels differ (1-1), the tie rule in 5.4.3 applies.
* If at most 1 valid repeat exists, the item-condition receives no final label and is recorded with reason `insufficient valid repeats`.

An item-condition without a final label is never converted to `Not coded` and is never silently dropped from analysis. All such cases are reported, by condition and by reason, in the completeness report produced under roadmap step 15.

Requiring at least 2 valid repeats keeps the final label a product of aggregation rather than a single call, so the same procedure defines every final label. This section fixes only the recording and reporting of missing final labels. Their treatment in the analysis, including whether such item-conditions are included in or excluded from κ, is decided under roadmap step 15, not here.
