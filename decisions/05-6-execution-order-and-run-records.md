## 5.6 Execution order and run records

[proposed 2026-09-18]

This section fixes how the calls defined in 5.3 (request structure), 5.3.10 (call unit and independence) and 5.4 (repeats, validity, retry, aggregation) are scheduled, executed, recorded and resumed. It does not restate those rules; where a term below is defined there, that definition applies.

Terms used in this section:

* Call: one (utterance, condition, repeat) triple, i.e., one repeat in the sense of 5.4. A call is terminated when it has a valid response or when its 3 attempts (5.4.7) are exhausted.
* Attempt: one API request for a call (5.4). One runner attempt is one SDK call.
* Pass: one scheduled set of calls. Pass 1 holds the planned repeats; pass 2 holds the first tie-break call (repeat 4) and pass 3 the second (repeat 5), one at a time as 5.4.3 requires.
* Block: the subset of pass 1 calls sharing one repeat number.
* Run: one execution of the runner identified by `run_id`, covering its passes and any resumptions.

### 5.6.1 Execution order

[proposed 2026-09-18]

The 5,400 planned calls (300 utterances × 6 conditions × R = 3, per 5.4.1) are split into three blocks by repeat number; each block holds all 1,800 (utterance, condition) pairs. Within-block order is a seeded shuffle; block order is fixed 1 → 2 → 3. The next block starts only after every call of the previous block is terminated; while the previous block's last retries are in flight, no call from the next block is sent.

Pass 1 seed = 20260918. Pass 2 seed = 20260919. Pass 3 seed = 20260920.

Tie-break calls are executed one round at a time, as 5.4.3 requires: pass 2 makes repeat 4 for every (utterance, condition) still tied after pass 1; pass 3 makes repeat 5 only for pairs still tied after pass 2 is aggregated. Each tie-break pass is a single block, shuffled with its own seed. A tie-break pass that has no target pairs is not needed and is not run; the runner reports this.

Rejected alternatives: a full shuffle of all 5,400 calls, because a partial run could not guarantee a completed "all utterances × all conditions for repeat 1" unit; blocking by utterance, because time-of-execution effects would then coincide with the sampling unit. Blocking by repeat keeps every condition interleaved within each time period, which is the purpose stated in 5.3.10.

### 5.6.2 Manifests

[proposed 2026-09-18]

Before pass 1, the runner writes `manifest_pass1.json` containing: `run_id`, `pass`, `created_at`, `seed`, the complete ordered call list (`order_index`, `utterance_id`, `condition`, `repeat`), `request_params` (from 5.3, i.e., every request field except the message content), SDK settings (`max_retries = 0`, `timeout`), `concurrency`, the consecutive-failure threshold, backoff settings, the sha256 of `prompts.jsonl`, the path and sha256 of the utterance input file, the runner git commit, the openai SDK version and the Python version. The stored list, not the seed, is the reference for reproduction.

`manifest_pass2.json` is created only after pass 1 is fully terminated. Its call list is the set of `tie_pending` rows of `final_labels.csv` (5.6.8), shuffled with the pass 2 seed and assigned `repeat = 4`. It additionally records the sha256 of `attempts_pass1.jsonl` used for tie selection (`attempts_pass1_sha256`), the sha256 of `final_labels.csv` (`final_labels_sha256`), and the git commit of `parse_attempts.py` (`parse_attempts_git_commit`).

`manifest_pass3.json` is created only after pass 2 is fully terminated, in the same way: its call list is the `tie_pending` rows of `final_labels.csv` re-derived from passes 1 and 2, shuffled with the pass 3 seed and assigned `repeat = 5`; it records the sha256 of `attempts_pass2.jsonl` used for selection (`attempts_pass2_sha256`), the sha256 of `final_labels.csv` (`final_labels_sha256`), and the git commit of `parse_attempts.py` (`parse_attempts_git_commit`). Both tie-break manifests carry the same `request_params`, settings, `prompts_sha256`, input-file record and environment fields as `manifest_pass1.json`.

### 5.6.3 Prompts file

[proposed 2026-09-18]

Before pass 1 the runner writes `prompts.jsonl`: one line per unique (`utterance_id`, `condition`), 1,800 lines, holding the complete user-message string exactly as sent (`build_inputs.build_prompt`) and its sha256. Attempt records carry only `prompt_sha256`. Pass 2 uses the same file. A test asserts that building the same prompt twice yields identical strings.

### 5.6.4 Concurrency and retry

[proposed 2026-09-18]

Concurrency is a CLI argument recorded in the manifest. The pilot starts at 4. The main-run value is fixed from pilot operational metrics only (429 rate, latency, timeout occurrence, throughput), never from κ or labels, and is recorded in this section before the main run.

The OpenAI client is constructed with `max_retries = 0` and an explicit timeout, so that one runner attempt is exactly one SDK call and every retry appears in the run records.

Retryable outcomes (5.4.6 as revised 2026-09-18) are retried in the same worker slot after a wait:

* HTTP 429 with a parseable `Retry-After` header: that value.
* HTTP 429 without a parseable `Retry-After`, and every other retryable outcome including invalid responses: exponential backoff with jitter. The base is `backoff_initial × 2^(attempt − 1)` capped at `backoff_max`; the wait is the base halved plus a uniform random draw between 0 and half the base, so it lies within [base/2, base].

If `Retry-After` exceeds `backoff_max`, the runner does not clip it: the attempt is recorded as `retryable_error` with the header value as `planned_wait_sec`, no new attempt is started, and the runner stops normally with `run_stopped` reason `retry_after_exceeds_max`. Resumption is manual (5.6.6).

Values left to the pilot [unresolved — pilot operational setting]: `timeout`, `backoff_initial`, `backoff_max`, consecutive-failure threshold. The runner has no defaults for these; each must be given on the command line and is recorded in the manifest.

### 5.6.5 Stop rules

[proposed 2026-09-18]

Each `attempt_completed` record receives a global sequence number `completed_seq` assigned inside the write lock (5.6.7). The consecutive-failure counter is evaluated in `completed_seq` order: +1 for `retryable_error` and `invalid_response`, reset to 0 on `success`. The stop decision and the permission to start a new attempt are taken under the same lock: a worker writes `attempt_started` only if the run is not in the stopped state.

Once stopped (threshold reached, a fatal error, or `retry_after_exceeds_max`), the state does not revert in that session; late successes do not cancel it. The runner starts no new attempts or retries, waits for in-flight attempts to complete and be recorded, writes a `run_stopped` event, and exits. On resume the counter starts at 0.

Unexpected exceptions (added 2026-09-21). An exception raised while an attempt is executed, other than the SDK status and connection errors classified in 5.4.6, is recorded as an `attempt_completed` with `outcome = fatal_error` (5.6.7) and stops the run. If an exception escapes after `attempt_started` was written and no `attempt_completed` can be written (for example, the record itself cannot be written), the worker puts the run in the stopped state with reason `fatal_error`, so that no new attempt starts; that attempt stays interrupted in the sense of 5.6.6.

### 5.6.6 Resume

[proposed 2026-09-18]

For each pass of a run, the single source of truth for progress is that pass's attempts JSONL file; there is no separate checkpoint. Each attempt produces an `attempt_started` and an `attempt_completed` record. An attempt is consumed the moment `attempt_started` is durably on disk (flush and fsync before the API call). On resume, an `attempt_started` with no matching `attempt_completed` is an interrupted attempt; the next attempt number is used, and whether the request reached the server is not assessed.

Before retrying a call on resume, the runner reads that call's most recent `attempt_completed`; if it carries `planned_wait_sec`, the runner waits until `completed_at + planned_wait_sec` (a zero or negative remainder starts immediately).

A call with a valid response is permanently complete; the runner has no option to re-run a specific call. A full re-run requires a new `run_id`, and both runs' records are kept. Creating a new run, and choosing which run to analyse, follow pre-specified technical invalidation criteria only: failed resume verification, log corruption, or a run with wrong settings. κ, Δκ or label patterns are never grounds. If a defect is found after results were seen, the record states the defect, when results were seen, and the reason for re-running.

Resume verification, all of which must pass or the runner refuses to start:

1. `model`, `request_params`, `seed` and the ordered call list match the manifest (the list is recomputed from the seed and the input file for pass 1; for passes 2 and 3, the sha256 of the previous pass's attempts file must match the manifest and the tie list is re-derived from the attempts files of the preceding passes with the `parse_attempts.py` functions).
2. The sha256 recomputed from each prompt body in `prompts.jsonl` matches the stored value, and the file's sha256 matches the manifest.
3. The (`utterance_id`, `condition`) set in the manifest equals the set in `prompts.jsonl` for pass 1; for passes 2 and 3 it must be a subset, since only tied pairs are scheduled.
4. The input-file sha256 matches the manifest.
5. The git commit matches the manifest and the working tree is clean (the existing `-dirty` detection in `build_inputs.git_commit_hash` is reused).

Pass 2 starts only after every pass 1 call is terminated, and pass 3 only after every pass 2 call is terminated. Each tie-break pass applies the same record format, stop rules, resume rules and repair rules with its own manifest and attempts file. `run.lock` in the run directory prevents two processes on the same run; a stale lock is removed manually after inspection.

Operational note. Because the manifest records the runner's git commit and the working tree must be clean, a run is started only after all code changes are committed. The intended sequence is `--dry-run` on a clean tree, then `--resume`.

### 5.6.7 Record format and write rules

[proposed 2026-09-18]

Attempts are JSONL, one file per pass. The runner uses the file append-only and never modifies or deletes existing records; this is a runner rule, not a property of the format. Append, flush, fsync of one record and the assignment of `completed_seq` happen inside one lock; both `attempt_started` and `attempt_completed` are fsynced.

Truncated-last-line rule: if only the final record is incomplete and fails JSON parsing, the runner stops and refuses to proceed automatically. A manual `--repair` command copies the file to `attempts_passN.jsonl.bak-<timestamp>`, removes only the incomplete final line, appends a record (time, file, bytes removed, removed string) to `recovery_log.jsonl`, and then allows resume. This repair is the only exception to append-only. If any non-final record fails parsing, the file is treated as corrupted and resume is refused.

`attempt_started` fields: `event`, `run_id`, `pass`, `order_index`, `utterance_id`, `condition`, `repeat`, `attempt`, `started_at`, `actual_wait_sec`, `prompt_sha256`, `request_params`. `actual_wait_sec` is the elapsed time from the same call's previous `attempt_completed.completed_at` to this `started_at`; it is null when there is no such previous record (attempt 1, or the previous attempt was interrupted without a completed record).

`attempt_completed` fields: `event`, `run_id`, `pass`, `order_index`, `utterance_id`, `condition`, `repeat`, `attempt`, `completed_seq`, `completed_at`, `outcome`, `invalid_reason`, `http_status`, `openai_request_id`, `openai_error_code`, `openai_error_type`, `response_model`, `system_fingerprint`, `finish_reason`, `usage`, `raw_response`, `error` {`type`, `message`, `retry_after`}, `planned_wait_sec`, `wait_source`.

`run_stopped` fields: `event`, `run_id`, `pass`, `stopped_at`, `reason` ∈ {`failure_threshold`, `fatal_error`, `retry_after_exceeds_max`}, `completed_seq_at_stop`, `triggering` (`order_index`, `attempt`).

`raw_response` is the HTTP response body as a string, obtained through the SDK's `with_raw_response` interface (also for error responses that carry a body); `openai_request_id` comes from the response headers and is null when no response was received; `openai_error_code` and `openai_error_type` are `error.code` and `error.type` from the response body when present (both used by the 429 rule in 5.4.6; added `openai_error_type` 2026-09-19). `response_model`, `system_fingerprint`, `finish_reason` and `usage` are extracted from the body for convenience.

`outcome` ∈ {`success`, `invalid_response`, `retryable_error`, `fatal_error`}.

`fatal_error` covers non-retryable HTTP errors (5.4.6) and, as of 2026-09-21, any unexpected exception during an attempt (5.6.5). For an unexpected exception, `error.type` and `error.message` hold the exception class name and message, and `http_status`, `openai_request_id` and `raw_response` hold whatever had been received before the exception (null otherwise).

`invalid_reason` (only when `outcome = invalid_response`, else null) ∈ {`refusal`, `truncated`, `finish_reason_other`, `malformed_json`, `schema_mismatch`, `label_not_in_enum`}. Classification order, first match wins: `refusal` field present (non-null) → `refusal`; `finish_reason = length` → `truncated`; `finish_reason` ∉ {`stop`, `length`} → `finish_reason_other`; message content not parseable as JSON → `malformed_json`; missing or extra fields, or a non-string `category` → `schema_mismatch`; `category` not an exact, case-sensitive match to one of the seven names in `scripts/tags.py` after whitespace strip → `label_not_in_enum`. This makes the 5.4.5 invalid-response definition operational; 5.4.5 itself is not changed.

`planned_wait_sec` is the value passed to sleep before the next attempt (null on success or when no retry follows); `wait_source` ∈ {`retry_after`, `backoff`, null}.

### 5.6.8 Parsing

[proposed 2026-09-18]

`scripts/parse_attempts.py` reads every attempts JSONL file present in the run directory (`attempts_pass1.jsonl`, and `attempts_pass2.jsonl`, `attempts_pass3.jsonl` when they exist) without modifying them and writes two files. It is deterministic and re-runnable. The parser re-derives `outcome`, `invalid_reason` and `category` from `raw_response` with the same validation function the runner used (`scripts/validation.py`) and refuses to write if the re-derived values differ from the recorded ones.

Exception to re-derivation (added 2026-09-21): a record whose recorded `outcome` is `fatal_error` is not re-derived, even when it carries an HTTP 200 body, and yields a row with no category and `valid` false. Such a record arises only from an unexpected exception after the response was received (5.6.5); the runner did not establish validity at call time, so the body is kept for inspection and is not counted as a label.

* `labels.csv`: one row per `attempt_completed` (`run_id`, `pass`, `utterance_id`, `condition`, `repeat`, `attempt`, `category`, `valid`).
* `final_labels.csv`: one row per (`utterance_id`, `condition`) with `run_id`, `utterance_id`, `condition`, `final_label` (empty when none), `status` ∈ {`resolved`, `tie_pending`, `unresolved_tie`, `insufficient_valid_repeats`}, `valid_repeats`, `repeats_used`. This is the 5.4 aggregation result: `resolved` when one label has the largest count among valid repeats (5.4.2); `tie_pending` when the largest count is shared and fewer than 5 repeats have been used, so a further tie-break call is allowed (5.4.3); `unresolved_tie` when the tie remains at 5 repeats (5.4.3); `insufficient_valid_repeats` when fewer than 2 repeats are valid (5.4.8).

The targets of pass 2 and pass 3 are the `tie_pending` rows of `final_labels.csv`, read from the file after the parser has been re-run on all attempts files present; the runner does not aggregate in memory. Pass 2 therefore covers pairs whose pass 1 calls are all terminated, that have at least 2 valid repeats, and whose largest count is shared by two or more labels; pass 3 covers pairs that remain `tie_pending` after pass 2. Termination conditions and the retryable status of invalid responses follow 5.4.6–5.4.8.

Exhaustion of a tie-break call. Per 5.4.3 (sentence added 2026-09-19), a tie-resolution call whose 3 attempts are all exhausted counts as one of the two additional calls, and a still-tied pair proceeds to the next round if any. In the implementation this holds because `repeats_used` is the highest repeat number present in `labels.csv`, valid or not: an exhausted repeat 4 gives `repeats_used = 4` with the valid counts unchanged, the pair stays `tie_pending`, and pass 3 sends repeat 5 for it; an exhausted repeat 5 gives `repeats_used = 5` and the pair becomes `unresolved_tie`.

Known limitation (recorded 2026-09-21): a pair whose nine attempts (3 repeats × 3 attempts) are all interrupted has terminated calls but no `attempt_completed` record, so it has no row in `final_labels.csv`, and the scorer refuses the run (6.1.1). This requires all nine attempts of one pair to end without an `attempt_completed` record (a process interruption, or a failure that prevents the record from being written; see 5.6.5) and is not handled further; see `tests/test_scorer_entry.py`.

After the last pass has terminated, run `python scripts/parse_attempts.py --run-id <run_id>` once more so labels.csv and final_labels.csv reflect all passes. Analysis reads final_labels.csv only after this step.

### 5.6.9 Directory layout

[proposed 2026-09-18]

```
runs/<run_id>/
  prompts.jsonl
  manifest_pass1.json
  attempts_pass1.jsonl
  manifest_pass2.json  (only if pass 1 leaves tie_pending pairs)
  attempts_pass2.jsonl
  manifest_pass3.json  (only if pass 2 leaves tie_pending pairs)
  attempts_pass3.jsonl
  labels.csv
  final_labels.csv
  recovery_log.jsonl   (only after a repair)
  run.lock             (only while running)
```

`runs/` is git-ignored except for a README describing this layout.

### 5.6.10 Status

[proposed 2026-09-18]

All subsections are [proposed 2026-09-18]. Promotion to [decided] happens at the roadmap 11 protocol freeze together with 5.3.10 and 5.4. After that, changes are made only when a test reveals a specification conflict or an execution failure.
