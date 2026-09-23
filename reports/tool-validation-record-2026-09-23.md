# Tool validation record (Roadmap 9)

This record documents the execution of the tool validation whose rules are fixed in `decisions/05-7-tool-validation.md` (5.7.1–5.7.5). All numbers below were read from `runs/validation-2026-09-23/` (`manifest_pass1.json`, `attempts_pass1.jsonl`, `labels.csv`, `final_labels.csv`, `score_report.txt`, `score_summary.json`) and from the reports under `reports/` named in each section. The run directory is git-ignored; this record and the reports are the committed trace.

## 1. Commits and environment

| Item | Value |
| --- | --- |
| Audit baseline commit | `a058391` |
| Pre-validation execution commit | `50d6362` (equal to `git_commit` in `runs/validation-2026-09-23/manifest_pass1.json`: `50d636203abfc52eeb1b8462e3a9ab763cae4fdb`) |
| Working tree at validation start | clean |
| Python | 3.13.9 (manifest `python_version`; `score_report.txt` header) |
| openai SDK | 3.8.0 (manifest `openai_version`) |
| NumPy | 2.3.5 (`score_report.txt` header) |
| Model snapshot | `gpt-5.5-2026-04-23` (manifest `model`; `raw_response.model` in all 306 completed attempts) |

Commits between the audit baseline and the execution commit:

| Commit | Content |
| --- | --- |
| `fc5f61b` | `scripts/build_dev_targets.py`, `tests/test_dev_targets.py`, path constants in `scripts/paths.py` |
| `c911acb` | `samples/dev_targets.csv`, `reports/dev-targets-2026-09-23.txt` |
| `0d42989` | `decisions/05-7-tool-validation.md` (new), 2.3 sampling-frame revision, 6.2.1 draw-order wording, `DECISIONS.md` index |
| `50d6362` | `reports/token-matching-check-2026-09-23.txt`, `reports/input-examples-2026-09-23.txt` |

## 2. Independent audit (Codex, 2026-09-23)

A read-only audit at commit `a058391` concluded READY FOR TOOL/TASK VALIDATION with no blocking item. Five non-blocking items and their handling:

| Item | Finding | Handling |
| --- | --- | --- |
| 4.1 | 6.2.1 said the replicate indices are generated "before any statistic is computed", while the scorer computes point estimates first | Wording aligned with the implemented order; no numeric effect (commit `0d42989`) |
| 4.2 | Guidance on where outputs are written | Local instruction file revised; no commit |
| 4.3 | Basis sentence of 5.1.6(c) | To be revised when 5.1.6 is moved to [decided] |
| 4.4 | Old [unresolved] wording in 5.2.2 | To be handled in the protocol freeze (Roadmap 11) |
| 4.5 | The runner does not enforce eligibility of input utterances | See section 7 |

Function-role map of `scripts/parse_attempts.py` from the audit: `labels_from_records` = API-response interpretation; `aggregate`, `tie_pairs`, `final_rows` = aggregation; no function mixes the two roles.

API specification comparison (2026-09-23, about 13:00 KST): no discrepancy between the request built by `scripts/run_experiment.py` and the provider documentation at
https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create ,
https://developers.openai.com/api/docs/models/gpt-5.5 ,
https://developers.openai.com/api/docs/guides/structured-outputs ,
https://developers.openai.com/api/docs/guides/error-codes .

## 3. Development targets D

Rule (5.7.2): 2 utterances per Tag 0–6 drawn from the eligible rows of `data/frame.csv` joined with `data/scoring_labels.csv`, with `numpy.random.default_rng(20260923)`, Tags in ascending order, `source_id` sorted ascending within Tag, `rng.choice(size=2, replace=False)`; plus the boundary cases `source_id` 0, 7 and 23541; overlap removed with the boundary reason taking precedence. Script `scripts/build_dev_targets.py` (commit `fc5f61b`); list `samples/dev_targets.csv`; selection report `reports/dev-targets-2026-09-23.txt` (eligible labelled rows 150,644; final count 17; overlap: no).

| source_id | Tag | selection_reason |
| --- | --- | --- |
| 0 | 0 | boundary_first_row |
| 7 | 0 | boundary_full_window |
| 9340 | 4 | category_random |
| 15952 | 0 | category_random |
| 23541 | 5 | boundary_empty_text_in_window |
| 28650 | 5 | category_random |
| 37242 | 2 | category_random |
| 59121 | 3 | category_random |
| 61884 | 5 | category_random |
| 72131 | 3 | category_random |
| 97832 | 1 | category_random |
| 157587 | 6 | category_random |
| 160076 | 2 | category_random |
| 167853 | 6 | category_random |
| 191127 | 4 | category_random |
| 198479 | 1 | category_random |
| 202369 | 0 | category_random |

D is excluded from target selection in the main experiment (2.3, revision of 2026-09-23): the main sampling frame is 150,644 − 17 = 150,627.

## 4. Static checks before any call

**check_inputs.py.** Run on the 17 source_ids as positional arguments. The script prints to stdout only; its result is copied here: every source_id line reads `PASS`, and the final line reads `All checks passed for 17 target(s) x 6 conditions.` (17 × 6 = 102 checks).

**check_token_matching.py.** Report `reports/token-matching-check-2026-09-23.txt` (script commit `0d42989`, tiktoken 0.14.0, encoding `o200k_base`): 17 source_ids × 90 site checks = 1,530 checks, 0 mismatches, `RESULT: 0 failing condition/source_id pairs; 1530 site checks run`. Site counts per condition are the same for every source_id: negative_control 1, definition_replacement 6, example_replacement 72, exclusion_rule_replacement 11. The total token count of every replacement condition equals the baseline total:

| source_id | tokens (baseline = each replacement condition) |
| --- | --- |
| 0 | 2093 |
| 7 | 2202 |
| 9340 | 2102 |
| 15952 | 2035 |
| 23541 | 2054 |
| 28650 | 2080 |
| 37242 | 2173 |
| 59121 | 2077 |
| 61884 | 2097 |
| 72131 | 2053 |
| 97832 | 2113 |
| 157587 | 2068 |
| 160076 | 2087 |
| 167853 | 2073 |
| 191127 | 2096 |
| 198479 | 2089 |
| 202369 | 2068 |

**pytest.** `PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider`: 160 passed. `tests/test_validation.py` checks that the response-format schema enum, the output instruction and `scripts/tags.py` list the same seven categories.

**Human reading of assembled prompts.** `reports/input-examples-2026-09-23.txt` holds the full prompts of source_id 23541 and 157587 under all six conditions (12 prompts, 92,636 bytes), built with `build_inputs.build_prompt` from the real condition files. Read by the user; no wording was changed. Items confirmed: exactly one `[TARGET] T:` line per prompt; the Context block is byte-identical across the six conditions of each source_id; the replacement conditions carry the filler only at the specified sites (token-matching report above); the names_only prompt has no `Coding manual:` section; the empty-text row inside the window of 23541 is rendered as `S:` with nothing after it.

**Earlier verifications reused, not repeated.**

| Roadmap | Scripts | Report files |
| --- | --- | --- |
| 3 | `scripts/test_api_request.py` | `reports/api-request-test-2026-09-15.txt` |
| 4 | `scripts/build_frame.py`, `scripts/build_inputs.py`; `scripts/check_inputs.py` and `scripts/check_frame_outputs.py` print to stdout only | `reports/frame-summary-2026-09-15.txt`, `reports/input-examples-2026-09-15.txt` |
| 5 | `scripts/check_token_matching.py`, `scripts/check_manual.py` | `reports/token-matching-check-2026-09-15.txt`, `reports/manual-inventory-check-2026-09-15.txt` |
| 7, 8 | `tests/` (151 tests at that time; 160 at commit `50d6362` after `tests/test_dev_targets.py` was added) | no report file; the test files are committed |

## 5. Validation run

**Dry run.** `run_id` `validation-2026-09-23-dryrun`, pass 1, `--dry-run`: `manifest_pass1.json` with 306 planned calls (102 pairs × 3 repeats), seed 20260918, and `prompts.jsonl` with 102 rows; no attempt record. Recomputing `plan_pass1(ids, 20260918)` reproduces the manifest call list exactly. Provisional operational settings (5.7.5): concurrency 4, timeout 60, backoff-initial 2, backoff-max 60, failure-threshold 10, taken from the usage example in `scripts/run_experiment.py`; they are fixed in the procedural pilot (Roadmap 10), not here.

**Real run.** `run_id` `validation-2026-09-23`, pass 1, `--input samples/dev_targets.csv` (sha256 `13893677cf2073624331a0068cb2b224120d1c929ad46fbaa0213475dfd00d21`), same settings, git commit `50d6362`. The command was run by the user in a terminal so that the API key was never placed in the assistant's working session.

Results read from `attempts_pass1.jsonl` (612 records: 306 `attempt_started`, 306 `attempt_completed`):

| Item | Value |
| --- | --- |
| Logical calls terminated | 306 / 306 (one attempt each; no retry) |
| HTTP status | 200 × 306 |
| `raw_response.model` | `gpt-5.5-2026-04-23` × 306 |
| `finish_reason` | `stop` × 306 |
| `refusal` not null | 0 |
| `outcome` | `success` × 306; `invalid_reason` null × 306; `error` null × 306 |
| `reasoning_tokens` | 0 × 306 |
| `prompt_tokens` | sum 569,190; min 310; max 2,269 |
| `completion_tokens` | sum 4,587; min 14; max 17 |
| Latency (`completed_at` − `started_at`) | median 0.931 s; max 3.276 s; min 0.721 s |
| Wall clock, first start to last completion | 79.5 s |
| `planned_wait_sec` not null | 0; `wait_source` null × 306 |

**Parser.** `python scripts/parse_attempts.py --run-id validation-2026-09-23`: `labels.csv` 306 rows (valid True 306, False 0); `final_labels.csv` 102 rows, status `resolved` 102, `valid_repeats` 3 and `repeats_used` 3 for every pair; `tie_pending` 0, so no pass 2 or pass 3. Repeat patterns over the three valid repeats: identical 3/3 in 96 pairs; 2/1 in 6 pairs: (9340, exclusion_rule_replacement), (28650, baseline), (37242, definition_replacement), (37242, exclusion_rule_replacement), (37242, names_only), (191127, definition_replacement); 1/1/1 in 0 pairs.

**Raw response against parsed label** (five calls, repeat 1, attempt 1):

| Call | `message.content` | finish / refusal | `labels.csv` valid, category |
| --- | --- | --- | --- |
| (23541, baseline) | `{"category":"Restating"}` | stop / null | True, Restating |
| (23541, names_only) | `{"category":"Restating"}` | stop / null | True, Restating |
| (157587, baseline) | `{"category":"Pressing for Reasoning"}` | stop / null | True, Pressing for Reasoning |
| (157587, example_replacement) | `{"category":"Pressing for Reasoning"}` | stop / null | True, Pressing for Reasoning |
| (0, negative_control) | `{"category":"Not coded"}` | stop / null | True, Not coded |

## 6. Agreement diagnostics (5.7.4)

The values below are diagnostic information for further inspection (5.7.1, 5.7.4). They are not a pass criterion, and they are kept separate from the procedural pilot (5.5).

`python scripts/score_run.py --run-id validation-2026-09-23` (exit 0) wrote `runs/validation-2026-09-23/score_report.txt` and `score_summary.json`. The entry checks of 6.1.1 (`require_run_complete`: pass layout, termination of every call, current `final_labels.csv`, coverage) passed; a failure would have ended the process with `Refused`. Human labels were read from `data/scoring_labels.csv` (sha256 `44e95948c340184e204856bda7d7c56cc17b1b7e7ba9ae8eb3f9f6b583340e58`) at this step only. Bootstrap: 10,000 replicates, seed 20260919, `Generator(PCG64)`, NumPy 2.3.5; undefined replicates 0 for all 18 statistics.

**Standalone κ per condition (6.1.1)**, n = 17 in every condition:

| Condition | P_o | P_e | κ | 95% CI |
| --- | --- | --- | --- | --- |
| baseline | 0.7059 | 0.1661 | 0.6473 | [0.3790, 0.8559] |
| definition_replacement | 0.7647 | 0.1696 | 0.7167 | [0.4516, 0.9261] |
| example_replacement | 0.7647 | 0.1661 | 0.7178 | [0.4603, 0.9261] |
| exclusion_rule_replacement | 0.6471 | 0.1384 | 0.5904 | [0.3173, 0.8522] |
| negative_control | 0.7059 | 0.1661 | 0.6473 | [0.3790, 0.8559] |
| names_only | 0.6471 | 0.1557 | 0.5820 | [0.3139, 0.8373] |

**Paired contrasts against baseline (6.1.2)**, paired n = 17 for every contrast (both 17, baseline only 0, condition only 0, neither 0; no missing status on either side). names_only has no paired contrast (3.3, 6.5) and is absent from the `paired` section of the JSON.

| Condition | baseline κ (paired set) | condition κ | Δκ | 95% CI | discordant |
| --- | --- | --- | --- | --- | --- |
| definition_replacement | 0.6473 | 0.7167 | 0.0694 | [0.0000, 0.2186] | 1 |
| example_replacement | 0.6473 | 0.7178 | 0.0705 | [-0.0047, 0.2204] | 2 |
| exclusion_rule_replacement | 0.6473 | 0.5904 | -0.0569 | [-0.2800, 0.1507] | 4 |
| negative_control | 0.6473 | 0.6473 | 0.0000 | [0.0000, 0.0000] degenerate | 0 |

With n = 17, defined intervals for all statistics and the degenerate [0, 0] interval of the negative control with 0 discordant labels are the outcomes the rules in 6.2.2 and 6.2.3 produce for these records; the degenerate interval is reported with its paired n and discordant count and is not read as equivalence (2.3.7).

**Confusion matrices (6.5)**, rows human, columns predicted, tag order 0–6 (NC, KET, GSR, RS, RV, PA, PR). Human marginal in every condition: NC 4, KET 2, GSR 2, RS 2, RV 2, PA 3, PR 2.

baseline (predicted marginal NC 6, KET 3, GSR 1, RS 3, RV 0, PA 2, PR 2):

|  | NC | KET | GSR | RS | RV | PA | PR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NC | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| KET | 0 | 2 | 0 | 0 | 0 | 0 | 0 |
| GSR | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
| RS | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| RV | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| PA | 0 | 1 | 0 | 1 | 0 | 1 | 0 |
| PR | 0 | 0 | 0 | 0 | 0 | 0 | 2 |

definition_replacement (predicted marginal NC 6, KET 2, GSR 1, RS 3, RV 0, PA 3, PR 2):

|  | NC | KET | GSR | RS | RV | PA | PR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NC | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| KET | 0 | 2 | 0 | 0 | 0 | 0 | 0 |
| GSR | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
| RS | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| RV | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| PA | 0 | 0 | 0 | 1 | 0 | 2 | 0 |
| PR | 0 | 0 | 0 | 0 | 0 | 0 | 2 |

example_replacement (predicted marginal NC 6, KET 3, GSR 1, RS 3, RV 0, PA 2, PR 2):

|  | NC | KET | GSR | RS | RV | PA | PR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NC | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| KET | 0 | 2 | 0 | 0 | 0 | 0 | 0 |
| GSR | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| RS | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| RV | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| PA | 0 | 0 | 0 | 1 | 0 | 2 | 0 |
| PR | 0 | 0 | 0 | 0 | 0 | 0 | 2 |

exclusion_rule_replacement (predicted marginal NC 2, KET 6, GSR 1, RS 3, RV 1, PA 2, PR 2):

|  | NC | KET | GSR | RS | RV | PA | PR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NC | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| KET | 0 | 2 | 0 | 0 | 0 | 0 | 0 |
| GSR | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
| RS | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| RV | 0 | 1 | 0 | 0 | 1 | 0 | 0 |
| PA | 0 | 1 | 0 | 1 | 0 | 1 | 0 |
| PR | 0 | 0 | 0 | 0 | 0 | 0 | 2 |

negative_control (predicted marginal NC 6, KET 3, GSR 1, RS 3, RV 0, PA 2, PR 2; identical to baseline):

|  | NC | KET | GSR | RS | RV | PA | PR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NC | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| KET | 0 | 2 | 0 | 0 | 0 | 0 | 0 |
| GSR | 0 | 0 | 1 | 0 | 0 | 1 | 0 |
| RS | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| RV | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| PA | 0 | 1 | 0 | 1 | 0 | 1 | 0 |
| PR | 0 | 0 | 0 | 0 | 0 | 0 | 2 |

names_only (predicted marginal NC 5, KET 3, GSR 2, RS 4, RV 0, PA 1, PR 2):

|  | NC | KET | GSR | RS | RV | PA | PR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NC | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| KET | 0 | 1 | 0 | 1 | 0 | 0 | 0 |
| GSR | 0 | 0 | 2 | 0 | 0 | 0 | 0 |
| RS | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| RV | 1 | 0 | 0 | 0 | 0 | 1 | 0 |
| PA | 0 | 2 | 0 | 1 | 0 | 0 | 0 |
| PR | 0 | 0 | 0 | 0 | 0 | 0 | 2 |

**Repeated-call diagnostics (4.2)**, per condition; n_items 17, initial_valid_denominator 17, items lacking all initial valid labels 0, items with a tie 0, additional calls 0, unresolved_tie 0, insufficient_valid_repeats 0 in every condition:

| Condition | 3/3 | 2/1 | 1/1/1 | unanimity rate | mean agreement with final (17 items) |
| --- | --- | --- | --- | --- | --- |
| baseline | 16 | 1 | 0 | 0.9412 | 0.9804 |
| definition_replacement | 15 | 2 | 0 | 0.8824 | 0.9608 |
| example_replacement | 17 | 0 | 0 | 1.0000 | 1.0000 |
| exclusion_rule_replacement | 15 | 2 | 0 | 0.8824 | 0.9608 |
| negative_control | 17 | 0 | 0 | 1.0000 | 1.0000 |
| names_only | 16 | 1 | 0 | 0.9412 | 0.9804 |

## 7. Anomaly inspection (5.7.4)

| 5.7.4 item | Observation |
| --- | --- |
| A category never produced under any condition | None. Revoicing was produced once, in exclusion_rule_replacement only (predicted marginal 0 in the other five conditions). |
| Systematic disagreement with human labels | No inverted mapping: every produced category matches the human category in at least one item where it was produced. Diagonal sums of the confusion matrices: baseline 12/17, definition_replacement 13/17, example_replacement 13/17, exclusion_rule_replacement 11/17, negative_control 12/17, names_only 11/17. The two human Revoicing items are the largest off-diagonal block; see the two inspections below. |
| Responses coding a non-target row | No direct evidence. All 306 responses are valid category strings; the `[TARGET]` line is unique in every prompt (section 4). Whether an individual label reflects a neighbouring row cannot be read from the output alone. |
| Excessive invalid responses | 0 invalid responses out of 306. |

**Inspection 1 — source_id 9340** (human Revoicing; LLM Not coded in five conditions, Keeping Everyone Together in exclusion_rule_replacement). Three data layers were compared for the target and its neighbouring teacher rows:

| Layer | Row | Speaker | Sentence | Label |
| --- | --- | --- | --- | --- |
| `train_data_504.xlsx` row position 9338 (`Unnamed: 0` = 9347) | 9338 | T | First of all you started with a line didnt you | Tag 1 |
| row position 9339 (9348) | 9339 | S | Oh yeah | — |
| row position 9340 (9349) | 9340 | T | Yep | Tag 4 |
| row position 9341 (9350) | 9341 | S | And then 60 degrees | — |
| row position 9342 (9351) | 9342 | T | Right so you draw a line 60 degrees here | Tag 4 |
| `data/frame.csv` | source_id 9338 / 9340 / 9342 | T / T / T | same three sentences, source_row_id 9347 / 9349 / 9351, eligible True | — |
| `data/scoring_labels.csv` | source_id 9338 / 9340 / 9342 | — | — | Tag 1 / 4 / 4 |

The three layers agree: source_id 9340 is the teacher line "Yep" with Tag 4 (Revoicing) in the raw file, in `frame.csv` and in `scoring_labels.csv`, and the neighbouring rows are aligned by row position and provider id. The gold–target alignment and the category mapping are correct. The disagreement is a coding judgement recorded in the dataset's gold label for a one-word utterance, not a tool defect. No change was made. As a single case it is not generalised into the Known issues of 2.1.3.

**Inspection 2 — source_id 191127** (human Revoicing; LLM Not coded in five conditions, Revoicing in exclusion_rule_replacement). Context immediately before the target, from `data/rows_all.csv`:

| source_id | Speaker | Sentence |
| --- | --- | --- |
| 191125 | S | Oh I was doing it as like 16two whats half of two |
| 191126 | S | Thats one and then |
| 191127 (target) | T | Because youve got a 16 there |

The student utterances that the target could restate are present in the window with text; the three layers agree on Speaker T and Tag 4 for source_id 191127 (`train_data_504.xlsx` row position 191127, `Unnamed: 0` 191173; `frame.csv` source_row_id 191173, eligible True; `scoring_labels.csv` Tag 4). This is a borderline coding judgement, not a rendering or alignment defect. No change was made.

**Pairs with a 2/1 repeat pattern** (human label from `data/scoring_labels.csv`; responses from `labels.csv`, repeats 1 / 2 / 3; final label by plurality, 5.4.2):

| Pair | Human | Repeat 1 / 2 / 3 | Final |
| --- | --- | --- | --- |
| (9340, exclusion_rule_replacement) | Revoicing | KET / KET / Not coded | KET |
| (28650, baseline) | Pressing for Accuracy | PA / KET / KET | KET |
| (37242, definition_replacement) | Getting Students to Relate | KET / PA / PA | PA |
| (37242, exclusion_rule_replacement) | Getting Students to Relate | PA / PA / KET | PA |
| (37242, names_only) | Getting Students to Relate | KET / GSR / GSR | GSR |
| (191127, definition_replacement) | Revoicing | Revoicing / Not coded / Not coded | Not coded |

**Audit item 4.5.** The runner does not enforce eligibility of the utterances in `--input`; the only input file used for the validation run was `samples/dev_targets.csv`, the same file that passed `check_inputs.py` (section 4), whose check 2 requires each target to be an eligible teacher row.

## 8. Changes made after inspecting output

None. No change within the permitted list of 5.7.3 (instruction wording, serialisation, target marker, empty-text rendering, response interpretation, parser, mapping, record format) was made, and no change outside it was proposed.

## 9. Status of proposed clauses

The prompts generated for this validation (`runs/validation-2026-09-23/prompts.jsonl`; excerpts in `reports/input-examples-2026-09-23.txt`) implement 5.1.2 and 5.1.6 (a)–(d) as written. Whether these clauses are moved from [proposed] to [decided] is a separate decision; this record supplies the evidence for it.

## 10. Tool use

| Tool | Use in this step |
| --- | --- |
| Codex (OpenAI) | Read-only audit at `a058391` and API-specification comparison (section 2). No code was modified. |
| Claude Code (Claude Fable 5.1) | Implementation of `scripts/build_dev_targets.py` and its tests; drafts of `decisions/05-7-tool-validation.md` and of the 2.3 and 6.2.1 revisions; execution of the static checks, the dry run, the parser and the scorer; this record. |
| Claude (Fable 5.1, decision session) | Consolidation of decisions and drafting of the task prompts. |
| User | All decisions, reading of the assembled prompts, execution of the real API run, all commits. |

## 11. Procedure log

| Order | Step | Commit or run_id | Outputs |
| --- | --- | --- | --- |
| 1 | Independent audit (Codex), read-only | `a058391` (baseline) | audit findings (section 2) |
| 2 | Development-target script and tests | `fc5f61b` | `scripts/build_dev_targets.py`, `tests/test_dev_targets.py`, `scripts/paths.py` constants |
| 3 | Development targets drawn | `c911acb` | `samples/dev_targets.csv`, `reports/dev-targets-2026-09-23.txt` |
| 4 | Decision documents | `0d42989` | `decisions/05-7-tool-validation.md`; 2.3 revision; 6.2.1 wording; `DECISIONS.md` |
| 5 | Static checks on D | `50d6362` | `reports/token-matching-check-2026-09-23.txt`, `reports/input-examples-2026-09-23.txt`; `check_inputs.py` stdout (section 4); pytest 160 passed |
| 6 | Dry run | `validation-2026-09-23-dryrun` | `manifest_pass1.json` (306 calls), `prompts.jsonl` (102 rows) |
| 7 | Real run, pass 1 (user) | `validation-2026-09-23` | `manifest_pass1.json`, `prompts.jsonl`, `attempts_pass1.jsonl` (612 records) |
| 8 | Parser | `validation-2026-09-23` | `labels.csv` (306), `final_labels.csv` (102, all resolved) |
| 9 | Scorer | `validation-2026-09-23` | `score_report.txt`, `score_summary.json` |
| 10 | This record | — | `reports/tool-validation-record-2026-09-23.md` |
