# Main-run execution record (2026-09-24)

This record documents data collection for the main experiment under the execution procedure fixed in `decisions/05-6-execution-order-and-run-records.md` (5.6). All numbers and hashes were read from `runs/main-2026-09-24/` (`manifest_pass1.json`, `manifest_pass2.json`, `prompts.jsonl`, `attempts_pass1.jsonl`, `attempts_pass2.jsonl`, `labels.csv`, `final_labels.csv`), `runs/main-2026-09-24-precheck-dryrun/`, `runs/main-2026-09-24-dryrun/` and `reports/`. The run directories are git-ignored (`.gitignore`: `runs/*`); this record is the committed trace. No human label was read at any step recorded here.

## 1. Purpose and scope

This record covers the data collection of Roadmap 14 only. Scoring (κ, Δκ, bootstrap) was not performed and is not part of this record. The formal completeness check and the fixing of the final-label table follow in Roadmap 15; scoring follows in Roadmap 16.

| Item | Value |
| --- | --- |
| `run_id` | `main-2026-09-24` |
| Execution commit (`manifest_pass1.json` `git_commit`) | `beb3ef984f1b8bd0ec73f7c9f96171f80cddf1eb` |
| Input | `samples/main_targets.csv`, sha256 `18ec7cd05b472fb26cbf64c983a9f84614a58dc26a7ec7f4f5b7329fd19553fe` |
| Planned calls | 300 targets × 6 conditions × 3 repeats = 5,400 |

## 2. Integrity audit (Roadmap 14-0)

An independent read-only audit (Codex) was run at HEAD `d0bd38f`. Scope: agreement between the frozen protocol (freeze commit `ed13ec2` plus the post-freeze entries of `reports/protocol-freeze-record-2026-09-24.md`), HEAD, and the inputs verified in Roadmap 13. The audit did not re-evaluate the design and modified no file.

Result: NOT READY, with 3 blocking items. All three were omissions in the freeze record: the post-freeze hash of `scripts/paths.py` was not recorded; the hash of `tests/test_main_sample.py` was not recorded; the three Roadmap 13 reports were not registered. No mismatch between protocol, sample, inputs and code was reported. The 4 non-blocking items were recorded as notes.

Handling: entry 4 was appended to the section "Post-freeze implementation artifacts (no protocol change)" of the freeze record, commit `beb3ef9` (1 file, 8 insertions, append only).

Re-check: at `beb3ef9`, only the audit's hash-comparison section and append-only section were re-run; the other sections kept their `d0bd38f` results because the files they cover did not change. Blocking items: None. Conclusion: "READY FOR MAIN-RUN EXECUTION (re-check at beb3ef9)".

`beb3ef9` was used as the execution commit.

The audit reports were delivered to the user in the conversation and are not stored in the repository.

## 3. Precheck dry run

`run_id` `main-2026-09-24-precheck-dryrun`, pass 1, command:

```
python scripts/run_experiment.py --run-id main-2026-09-24-precheck-dryrun --pass 1 --input samples/main_targets.csv --concurrency 4 --timeout 60 --backoff-initial 2 --backoff-max 60 --failure-threshold 10 --dry-run
```

stdout: `wrote manifest_pass1.json: 5400 calls, seed 20260918`; exit code 0.

Manifest (`manifest_pass1.json`): `git_commit` `beb3ef984f1b8bd0ec73f7c9f96171f80cddf1eb`; `n_calls` 5400; `input_file.sha256` `18ec7cd05b472fb26cbf64c983a9f84614a58dc26a7ec7f4f5b7329fd19553fe`; `prompts_sha256` `4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140`; `created_at` 2026-09-24T05:28:09.998612+00:00. No attempt record.

Comparison with the expected values in `reports/input-verification-2026-09-24.md` §9:

| Item | Expected (§9) | Precheck dry run | Match |
| --- | --- | --- | --- |
| `prompts_sha256` | `4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140` | `4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140` | yes |
| `n_calls` | 5400 | 5400 | yes |
| `input_file.sha256` | `18ec7cd05b472fb26cbf64c983a9f84614a58dc26a7ec7f4f5b7329fd19553fe` | `18ec7cd05b472fb26cbf64c983a9f84614a58dc26a7ec7f4f5b7329fd19553fe` | yes |

Compared with the Roadmap 13 dry run (`main-2026-09-24-dryrun`, `git_commit` `6673383fb28476740c5ee1d22aa969b769e5c391`), the manifest fields that differ are `run_id`, `created_at` and `git_commit`; the 5,400-entry call list is identical. The two `prompts.jsonl` files are byte-identical (14,358,858 B each, recomputed sha256 `4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140` for both).

## 4. Main run, pass 1

`run_id` `main-2026-09-24`, pass 1, command:

```
python scripts/run_experiment.py --run-id main-2026-09-24 --pass 1 --input samples/main_targets.csv --concurrency 4 --timeout 60 --backoff-initial 2 --backoff-max 60 --failure-threshold 10
```

The command was run by the user in a local terminal, consistent with the validation and pilot runs. stdout: `wrote manifest_pass1.json: 5400 calls, seed 20260918` / `pass 1: 5400 calls, 0 terminated, 5400 open` / `terminated 5400/5400`; exit code 0.

Manifest (`manifest_pass1.json`): `run_id` `main-2026-09-24`; `created_at` 2026-09-24T05:43:31.595339+00:00; `git_commit` `beb3ef984f1b8bd0ec73f7c9f96171f80cddf1eb`; `openai_version` 3.8.0; `python_version` 3.13.9; `seed` 20260918; `model` `gpt-5.5-2026-04-23`; `request_params` `{model: gpt-5.5-2026-04-23, temperature: 0, reasoning_effort: none, max_completion_tokens: 64, response_format: json_schema talkmove_category (strict, one required field category, enum of the seven category names, additionalProperties false)}`; `concurrency` 4; `sdk_settings` `{max_retries: 0, timeout: 60.0}`; `backoff` `{initial: 2.0, max: 60.0}`; `failure_threshold` 10; `n_calls` 5400 (repeat 1: 1,800; repeat 2: 1,800; repeat 3: 1,800); `prompts_sha256` `4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140`; `input_file` `samples/main_targets.csv`, sha256 `18ec7cd05b472fb26cbf64c983a9f84614a58dc26a7ec7f4f5b7329fd19553fe`. The manifest fields that differ from the precheck dry run are `run_id` and `created_at`.

Attempt records (`attempts_pass1.jsonl`):

| Item | main-2026-09-24, pass 1 |
| --- | --- |
| Records (`attempt_started` / `attempt_completed` / other) | 10,800 (5,400 / 5,400 / 0) |
| `run_stopped` | none |
| Calls with a `success` attempt | 5,400 of 5,400 |
| HTTP status | 200 × 5,400 |
| `outcome` | `success` × 5,400 |
| `response_model` (and `raw_response.model`) | `gpt-5.5-2026-04-23` × 5,400 |
| `finish_reason` | `stop` × 5,400 |
| `refusal` not null | 0 |
| `openai_error_code` / `openai_error_type` not null | 0 / 0 |
| `invalid_response` | 0 |
| Attempt number ≥ 2 | 0 |
| HTTP 429 | 0 |
| Timeouts and connection errors (`error.type` not null) | 0 |
| `planned_wait_sec` not null | 0 |

## 5. Tie-break passes

After pass 1 was aggregated, one pair was `tie_pending`: (54297, names_only), with repeats 1 / 2 / 3 labelled Pressing for Reasoning / Pressing for Accuracy / Not coded (`labels.csv`).

Pass 2, command:

```
python scripts/run_experiment.py --run-id main-2026-09-24 --pass 2 --concurrency 4 --timeout 60 --backoff-initial 2 --backoff-max 60 --failure-threshold 10
```

stdout: `wrote manifest_pass2.json: 1 calls, seed 20260919` / `pass 2: 1 calls, 0 terminated, 1 open` / `terminated 1/1`; exit code 0.

Manifest (`manifest_pass2.json`): `created_at` 2026-09-24T06:29:42.405740+00:00; `seed` 20260919; `n_calls` 1; call list `[{order_index: 0, utterance_id: 54297, condition: names_only, repeat: 4}]`. `model`, `request_params`, `sdk_settings`, `concurrency`, `failure_threshold`, `backoff`, `prompts_sha256`, `input_file`, `git_commit`, `openai_version` and `python_version` are equal to `manifest_pass1.json`. Additional fields:

| Field | Value | Compared with | Match |
| --- | --- | --- | --- |
| `attempts_pass1_sha256` | `c47cc626556ba42af810694c3cab1469b5b116782ce1be62bf8ba69c6e730cbe` | sha256 of `attempts_pass1.jsonl`, recomputed | yes |
| `final_labels_sha256` | `50563ffb1e2ffbc79cd929201dda3b7394af214a094a95b790d5371311e8b390` | sha256 of `final_labels.csv` after pass 1 aggregation (Roadmap 14-5) | yes |
| `parse_attempts_git_commit` | `beb3ef984f1b8bd0ec73f7c9f96171f80cddf1eb` | execution commit | yes |
| `n_tie_pairs` | 1 | `tie_pending` rows after pass 1 | yes |

Attempt records (`attempts_pass2.jsonl`): 2 records (`attempt_started` 1, `attempt_completed` 1), no `run_stopped`. The completed attempt: attempt 1, HTTP 200, `outcome` `success`, `response_model` `gpt-5.5-2026-04-23`, `finish_reason` `stop`, `refusal` null; repeat 4 label Not coded. After re-aggregation over passes 1 and 2, `tie_pending` was 0.

Pass 3, command:

```
python scripts/run_experiment.py --run-id main-2026-09-24 --pass 3 --concurrency 4 --timeout 60 --backoff-initial 2 --backoff-max 60 --failure-threshold 10
```

stdout: `pass 3 not needed: no tie_pending rows in final_labels.csv`; exit code 0. No `manifest_pass3.json` or `attempts_pass3.jsonl` was written and no API call was made. This is the basis for there being no further pass to call, under 5.6.1 (line 23): "A tie-break pass that has no target pairs is not needed and is not run; the runner reports this."

Total API calls: 5,401 (pass 1: 5,400; pass 2: 1).

## 6. Response processing

`python scripts/parse_attempts.py --run-id main-2026-09-24`: stdout `wrote …/labels.csv: 5401 attempt rows` / `wrote …/final_labels.csv: 1800 (utterance, condition) rows` / `resolved: 1800`, exit 0.

| Item | Value |
| --- | --- |
| `labels.csv` rows | 5,401 (pass 1: 5,400; pass 2: 1) |
| `labels.csv` `valid` True | 5,401 |
| `final_labels.csv` rows | 1,800 |
| status `resolved` / `tie_pending` / `unresolved_tie` / `insufficient_valid_repeats` | 1,800 / 0 / 0 / 0 |
| `valid_repeats` | 3 × 1,799; 4 × 1 |
| `repeats_used` | 3 × 1,799; 4 × 1 |

Determinism: after one further run of the same command the sha256 values were unchanged: `labels.csv` `13bbc66526a1c686a96eb33f08a20217fa73f25e5dba5e6485d5617a0cfbe5d1`, `final_labels.csv` `c1e7af7cc1ec3b3608b40218ab67cc37305f4bc99580821eed696c16bfd24110`.

Raw-response check: the `category` value in `raw_response` was compared with the `labels.csv` row for the same (utterance_id, condition, repeat) in 6 records, all equal: 5 pass 1 records spread over `order_index` (0, 1350, 2700, 4049, 5399; Roadmap 14-5) and the single pass 2 record (Roadmap 14-6).

Provenance: (a) During Roadmap 14-5 the parser was first run in an assistant session that was interrupted by a usage limit before its report was completed; the parser was then re-run in a new session and the outputs were byte-identical. (b) The runner re-runs the parser before preparing each tie-break pass, including the pass 3 invocation that found no targets (scripts/run_experiment.py, prepare_tiebreak_pass). The files listed in section 10 were last written by the determinism re-run in this section (2026-09-24T06:52:40Z) and are byte-identical to those produced after pass 2.

The `labels.csv` and `final_labels.csv` of this stage serve the tie-break pass decisions; the formal completeness check is carried out in Roadmap 15.

## 7. Operational metrics

Latency = `completed_at` of the `attempt_completed` record minus `started_at` of the matching `attempt_started` record; `attempt_completed` has no latency field. Elapsed = last `completed_at` minus first `started_at`; concurrency = maximum number of attempts in flight in a sweep over all start and completion times.

| Metric | Pass 1 | Pass 2 |
| --- | --- | --- |
| First `started_at` | 2026-09-24T05:43:31.692423+00:00 | 2026-09-24T06:29:42.486302+00:00 |
| Last `completed_at` | 2026-09-24T06:06:44.486858+00:00 | 2026-09-24T06:29:44.961738+00:00 |
| Elapsed | 1,392.794 s | 2.475 s |
| Latency median / min / max / sum | 0.970 / 0.671 / 12.387 / 5,560.062 s | 2.475 s (one attempt) |
| Latency sum ÷ elapsed | 3.99 | 1.00 |
| Maximum concurrent attempts | 4 | 1 |
| `prompt_tokens` sum (min–max) | 10,127,124 (260–2,328) | 427 |
| `prompt_tokens` min–max, names_only | 260–536 | 427 |
| `prompt_tokens` min–max, other five conditions | 2,052–2,328 | — |
| `completion_tokens` sum (min–max) | 79,184 (14–17) | 14 |
| `reasoning_tokens` sum | 0 | 0 |

The operational settings were not changed between passes. There was no resume, no `run.lock` left in the run directory, no `recovery_log.jsonl`, and no manual intervention.

## 8. Observations (descriptive only)

Prompt caching was observed in pass 1: `cached_tokens` sum 8,001,280, 79.01% of `prompt_tokens` (74.62% in the procedural pilot, `reports/procedural-pilot-record-2026-09-24.md` §6). In pass 2, `cached_tokens` was 0. This is recorded as descriptive operational information only and was not used for any decision.

## 9. Changes made after inspecting output

None. No script, prompt template, condition file, decision document, sample or operational setting was changed between the precheck dry run and the completion of data collection.

## 10. Artifacts

`runs/main-2026-09-24/` (git-ignored under `runs/*`; this table is the record):

| File | Size | sha256 |
| --- | --- | --- |
| manifest_pass1.json | 601,435 B | `faabb4a6c5480bd39f9955b1ea5cb9f746692712ae27cd30ed202855cf528abf` |
| manifest_pass2.json | 1,848 B | `065c7ed568544fc14d10005fb6cc7ae8b670ca56b9b8437f4e90dacf7775a308` |
| prompts.jsonl | 14,358,858 B | `4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140` |
| attempts_pass1.jsonl | 14,426,505 B | `c47cc626556ba42af810694c3cab1469b5b116782ce1be62bf8ba69c6e730cbe` |
| attempts_pass2.jsonl | 2,635 B | `374113a1aad2a483724e325b5de3824db59efbce9c34200dbad407790ddc4fb6` |
| labels.csv | 365,089 B | `13bbc66526a1c686a96eb33f08a20217fa73f25e5dba5e6485d5617a0cfbe5d1` |
| final_labels.csv | 125,338 B | `c1e7af7cc1ec3b3608b40218ab67cc37305f4bc99580821eed696c16bfd24110` |

No scoring file (`score_report.txt`, `score_summary.json`) exists under the run directory.

Related commits: `d0bd38f` (Roadmap 13 input verification), `beb3ef9` (execution commit), `112b4ea` (HEAD when this record was written).
