# Procedural pilot record (Roadmap 10)

This record documents the procedural pilot of the execution procedure fixed in `decisions/05-6-execution-order-and-run-records.md` (5.6), under the role of the pilot in 5.5 and the change rules of 5.7.3. All numbers were read from `runs/pilot-2026-09-24/` (`manifest_pass1.json`, `attempts_pass1.jsonl`, `labels.csv`, `final_labels.csv`), `runs/pilot-2026-09-24-dryrun/` and, for comparison, `runs/validation-2026-09-23/`. The run directories are git-ignored (`.gitignore`: `runs/*`); this record is the committed trace. No human label was read at any step of the pilot.

## 1. Purpose and scope

The pilot verifies procedural execution only (5.5): human–LLM agreement statistics, including κ, are not computed or reported, and `scripts/score_run.py` is not run on the pilot output.

Completion criteria, fixed before the pilot output was inspected:

| | Criterion | Evidence required |
| --- | --- | --- |
| (a) | Execution complete | `manifest_pass1.json` written; `attempt_started` and `attempt_completed` records both 306; every completed attempt HTTP 200 and `outcome` `success` |
| (b) | Processing complete | `labels.csv` 306 rows all valid; `final_labels.csv` 102 rows all `resolved`; pass 2 and pass 3 run if any pair is `tie_pending` |
| (c) | Parser deterministic | a second run of `scripts/parse_attempts.py` reproduces both files byte for byte (sha256) |
| (d) | Scorer not run | no scoring output under the run directory |
| (e) | Operational metrics recorded | counts of HTTP 429, timeouts and retries; latency median and maximum; elapsed time; maximum concurrency |

The pilot passes when every item is recorded and every failure that occurred was handled by the rules of 5.6.

Rules fixed in advance for what the pilot can and cannot settle: pass 2, pass 3 and resume are exercised only if the real calls give rise to them; they are not simulated in the pilot. The operational settings are confirmed as the provisional values of 5.7.5 when no failure occurs; when a failure occurs, only the value corresponding to it is reconsidered (429 → concurrency and backoff; timeout → `timeout`; threshold reached → failure threshold).

Changes after inspecting output are governed by 5.7.3: a permitted change requires a defect confirmed by re-reading the raw responses, the prompts and the run records (line 51), and in the pilot "result" means a procedural failure, with changes limited to record format, response-interpretation code and the five operational settings (line 55).

## 2. Dry run

`run_id` `pilot-2026-09-24-dryrun`, pass 1, command:

```
python scripts/run_experiment.py --run-id pilot-2026-09-24-dryrun --pass 1 --input samples/dev_targets.csv --concurrency 4 --timeout 60 --backoff-initial 2 --backoff-max 60 --failure-threshold 10 --dry-run
```

stdout `wrote manifest_pass1.json: 306 calls, seed 20260918`, exit 0. Outputs: `manifest_pass1.json` (306 calls, seed 20260918) and `prompts.jsonl` (102 rows, one per (utterance_id, condition)); no attempt record. `prompts_sha256` is `033936305549604216d649a1bea25ebbacdaa0b58588a599a3ed6bb3a0b49eba`, equal to the value in the validation dry run (`validation-2026-09-23-dryrun`); the 306-entry call list (order_index, utterance_id, condition, repeat) is identical to the validation dry run; the manifest fields that differ from it are `run_id`, `created_at` and `git_commit` (`2a7a935` here, `50d6362` there).

## 3. Pilot run

`run_id` `pilot-2026-09-24`, pass 1, command:

```
python scripts/run_experiment.py --run-id pilot-2026-09-24 --pass 1 --input samples/dev_targets.csv --concurrency 4 --timeout 60 --backoff-initial 2 --backoff-max 60 --failure-threshold 10
```

The command was run by the user in a local terminal, consistent with the validation run. stdout: `wrote manifest_pass1.json: 306 calls, seed 20260918` / `pass 1: 306 calls, 0 terminated, 306 open` / `terminated 306/306`; exit code 0.

Manifest (`manifest_pass1.json`): `run_id` `pilot-2026-09-24`; `git_commit` `2a7a935f1cc5e895c8816e781f87d3abad8f0b09`; `openai_version` 3.8.0; `python_version` 3.13.9; `model` `gpt-5.5-2026-04-23`; `input_file` `samples/dev_targets.csv`, sha256 `13893677cf2073624331a0068cb2b224120d1c929ad46fbaa0213475dfd00d21`; `concurrency` 4; `sdk_settings` `{max_retries: 0, timeout: 60.0}`; `backoff` `{initial: 2.0, max: 60.0}`; `failure_threshold` 10; `seed` 20260918; `n_calls` 306; `created_at` 2026-09-23T21:14:43.568999+00:00. The call list is identical to the dry run's.

Attempt records (`attempts_pass1.jsonl`), with the validation run alongside:

| Item | pilot-2026-09-24 | validation-2026-09-23 |
| --- | --- | --- |
| Records (`attempt_started` / `attempt_completed` / other) | 612 (306 / 306 / 0) | 612 (306 / 306 / 0) |
| HTTP status | 200 × 306 | 200 × 306 |
| `outcome` | `success` × 306 | `success` × 306 |
| `raw_response.model` | `gpt-5.5-2026-04-23` × 306 | same |
| `finish_reason` | `stop` × 306 | `stop` × 306 |
| `refusal` not null | 0 | 0 |
| `reasoning_tokens` | 0 × 306 | 0 × 306 |
| Attempt number | 1 × 306 (no retry) | 1 × 306 (no retry) |
| `prompt_tokens` sum (min–max) | 569,190 (310–2,269) | 569,190 (310–2,269) |
| `completion_tokens` min–max | 14–17 | 14–17 |

## 4. Response processing

`python scripts/parse_attempts.py --run-id pilot-2026-09-24`: stdout `wrote …/labels.csv: 306 attempt rows` / `wrote …/final_labels.csv: 102 (utterance, condition) rows` / `resolved: 102`, exit 0. `labels.csv` 306 rows, `valid` True 306; `final_labels.csv` 102 rows, status `resolved` 102, `tie_pending` 0, `valid_repeats` 3 for all 102 pairs.

Determinism (criterion c): after a second run of the same command the sha256 values were unchanged: `labels.csv` `49624044cde57068520587b6f5ca11549dff947ed15993260b9b1fa97feb537d`, `final_labels.csv` `853abe83f35ef846350bb45228ce7167e23096195317a593c5f7d6bbeb3cb695`.

Not exercised by real calls: pass 2 and pass 3 (no `tie_pending` pair), resume (no interruption), repair (no truncated file). These paths are covered by unit tests only: `tests/test_parse.py` (`test_aggregate_plurality_tie_and_insufficient`, `test_exhausted_tiebreak_call_counts_as_a_round`, `test_pass2_targets_equal_tie_pending_rows_of_final_labels`, `test_pass3_selects_only_pairs_still_tied_after_pass2`, `test_pass3_unresolved_after_five_repeats`, `test_pass3_not_needed_when_pass2_resolves`, `test_pass2_not_needed_when_pass1_has_no_ties`, `test_prepare_pass2_refuses_open_pass1_calls`), `tests/test_planning.py` (`test_plan_tiebreak_single_block_per_pass`), `tests/test_records.py` (`test_resume_verification_passes_on_intact_run`, `test_resume_refuses_dirty_tree`, `test_resume_refuses_other_commit`, `test_resume_refuses_manifest_mismatches`, `test_resume_refuses_changed_input_prompts_and_settings`, `test_truncated_last_line_is_detected_then_scan_after_repair`, `test_repair_is_noop_on_intact_file`), `tests/test_unexpected_exceptions.py` (`test_resume_continues_with_next_attempt_and_aggregates_normally`), and `tests/test_scorer_entry.py` (`test_pass2_manifest_without_attempts_or_attempts_without_manifest_refused`, `test_pass1_and_pass3_without_pass2_refused`).

## 5. Operational metrics and settings

Metrics from `attempts_pass1.jsonl` (criterion e); latency = `completed_at` of the `attempt_completed` record minus `started_at` of the matching `attempt_started` record; elapsed = last `completed_at` minus first `started_at`; concurrency = maximum number of attempts in flight in a sweep over all start and completion times.

| Metric | pilot-2026-09-24 | validation-2026-09-23 |
| --- | --- | --- |
| HTTP 429 | 0 | 0 |
| Timeouts | 0 | 0 |
| Other errors (`outcome` ≠ `success`) | 0 | 0 |
| Retries (attempts with number > 1) | 0 | 0 |
| Latency median / min / max / sum | 0.957 / 0.742 / 4.605 / 326.592 s | 0.931 / 0.721 / 3.276 / 313.480 s |
| First `started_at` | 2026-09-23T21:14:43.623891+00:00 | 2026-09-23T11:37:54.476538+00:00 |
| Last `completed_at` | 2026-09-23T21:16:06.431533+00:00 | 2026-09-23T11:39:14.025285+00:00 |
| Elapsed | 82.808 s | 79.549 s |
| Maximum concurrent attempts | 4 | 4 |
| `planned_wait_sec` not null | 0 | 0 |

Settings fixed for the main run (5.6.4, decided 2026-09-24): concurrency 4; `timeout` 60 s, `backoff_initial` 2 s, `backoff_max` 60 s, consecutive-failure threshold 10. Concurrency is fixed from the metrics above (no 429, no timeout, 326.592 / 82.808 ≈ 3.94 attempts in flight on average, maximum 4). The other four values had no triggering event in the pilot (no 429, timeout, retry or consecutive failure) and are confirmed as the provisional values of 5.7.5 under the rule in section 1.

Expected elapsed time of the main run at the same settings: 5,400 calls (300 utterances × 6 conditions × 3 repeats) ÷ 306 × 82.808 s ≈ 1,461 s, before any tie-break pass.

## 6. Observations (descriptive only)

Repeat patterns over the three valid repeats: identical 3/3 in 94 pairs, 2/1 in 8 pairs (validation: 96 and 6). The 2/1 pairs and their responses (repeats 1 / 2 / 3):

| Pair | Repeat 1 / 2 / 3 |
| --- | --- |
| (9340, exclusion_rule_replacement) | Keeping Everyone Together / Not coded / Not coded |
| (28650, baseline) | Keeping Everyone Together / Pressing for Accuracy / Keeping Everyone Together |
| (28650, negative_control) | Keeping Everyone Together / Pressing for Accuracy / Pressing for Accuracy |
| (37242, definition_replacement) | Keeping Everyone Together / Pressing for Accuracy / Pressing for Accuracy |
| (37242, exclusion_rule_replacement) | Pressing for Accuracy / Keeping Everyone Together / Pressing for Accuracy |
| (37242, names_only) | Keeping Everyone Together / Getting Students to Relate / Getting Students to Relate |
| (191127, definition_replacement) | Revoicing / Revoicing / Not coded |
| (191127, names_only) | Pressing for Reasoning / Pressing for Accuracy / Pressing for Accuracy |

Final labels differing from the validation run (`final_labels.csv` joined on (utterance_id, condition); 102 pairs, 3 differ):

| Pair | validation-2026-09-23 | pilot-2026-09-24 |
| --- | --- | --- |
| (9340, exclusion_rule_replacement) | Keeping Everyone Together | Not coded |
| (28650, negative_control) | Keeping Everyone Together | Pressing for Accuracy |
| (191127, definition_replacement) | Not coded | Revoicing |

Prompt caching was observed in both runs. Cached-input ratio was 75.56% in the validation run and 74.62% in the pilot run. This was recorded as descriptive operational information only and was not used to set the pilot completion criterion or operational parameters.

## 7. Changes

No procedural failure occurred, so no change under the conditions of 5.7.3 was made: no change to record format, response-interpretation code, parser, prompt construction or operational settings. The only document change is in 5.6.4 of `decisions/05-6-execution-order-and-run-records.md`: the four values previously tagged [unresolved — pilot operational setting] (`timeout`, `backoff_initial`, `backoff_max`, consecutive-failure threshold) were fixed at 60 s, 2 s, 60 s and 10 with the tag [decided 2026-09-24; unresolved since 2026-09-18], and the main-run concurrency 4 was recorded in the concurrency paragraph with the tag [decided 2026-09-24]. The section and file tags [proposed 2026-09-18] and 5.6.10 were not changed. As a consequential consistency update following that decision, the sentence in 5.7.5 of `decisions/05-7-tool-validation.md` that said the final values were still to be fixed in the pilot was rewritten to state that they were fixed on 2026-09-24 and recorded in 5.6.4; this is not a new decision.

## 8. Artifacts

`runs/pilot-2026-09-24/` (git-ignored under `runs/*`):

| File | Size | sha256 |
| --- | --- | --- |
| manifest_pass1.json | 34,915 B | `7e514f04f30fcd7b50febbf54eebaf6baf3ab89fe10a47be58078feb22a9e7d0` |
| attempts_pass1.jsonl | 817,127 B | `c350c4991dd2b1cd8087b01dd571c0e932583b0598e5b0fbd01b892e6684e036` |
| prompts.jsonl | 805,630 B | `033936305549604216d649a1bea25ebbacdaa0b58588a599a3ed6bb3a0b49eba` |
| labels.csv | 21,420 B | `49624044cde57068520587b6f5ca11549dff947ed15993260b9b1fa97feb537d` |
| final_labels.csv | 7,391 B | `853abe83f35ef846350bb45228ce7167e23096195317a593c5f7d6bbeb3cb695` |

`runs/pilot-2026-09-24-dryrun/` (git-ignored): `manifest_pass1.json` 34,922 B, `prompts.jsonl` 805,630 B. No scoring file (`score_report.txt`, `score_summary.json`) exists under either directory.
