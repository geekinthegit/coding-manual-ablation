# Input verification record (Roadmap 13)

This record documents the verification of every main-experiment input (300 target utterances × 6 conditions) before any main-run API call. All values below were read from the two check reports written on 2026-09-24 (`reports/check-inputs-main-2026-09-24.txt`, `reports/token-matching-check-2026-09-24.txt`), from the dry-run artifacts under `runs/main-2026-09-24-dryrun/` (`manifest_pass1.json`, `prompts.jsonl`; the run directory is git-ignored) and from the repository files named in each section. No API call was made and no human label was read.

## 1. Commits and environment

Purpose: to check, at the commit from which the main run will be executed, that the assembled inputs satisfy the frozen input specification (5.1, 3.2.3) and that the runner's plan for the main sample is reproducible. The commit that adds this record is the execution reference commit for Roadmap 14.

| Item | Value |
| --- | --- |
| Verification commit | `6673383` (parent `eaa155d`, "Draw main sample n=300 (seed 20260924) and record it (Roadmap 12)") |
| Working tree at start | clean; 169 tests passed |
| Frozen protocol | freeze commit `ed13ec2`; `reports/protocol-freeze-record-2026-09-24.md`, including its section "Post-freeze implementation artifacts (no protocol change)" for the sampling script and the sample |
| Python | 3.13.9 |
| numpy | 2.3.5 |
| pandas | 2.3.3 |
| tiktoken | 0.14.0 (encoding `o200k_base`) |
| openai | 3.8.0 |

## 2. Inputs

| File | Content | sha256 (recomputed) |
| --- | --- | --- |
| `samples/main_targets.csv` | 300 source_ids, one column `source_id`; drawn by `scripts/build_main_sample.py` with seed 20260924 (`reports/main-sample-manifest-2026-09-24.json`) | `18ec7cd05b472fb26cbf64c983a9f84614a58dc26a7ec7f4f5b7329fd19553fe` |
| `samples/dev_targets.csv` | 17 source_ids (development targets D, 5.7.2) | `13893677cf2073624331a0068cb2b224120d1c929ad46fbaa0213475dfd00d21` |
| `data/frame.csv` | teacher-row frame with `eligible` column (git-ignored) | `39506e9cb60fe4786057e8993f713127d8f89ca5ffbd8f9344ffed1aea333154`, equal to the value in the freeze record (line "data/frame.csv") |

## 3. Eligibility checks

Command: `python scripts/check_inputs.py --ids-file samples/main_targets.csv > reports/check-inputs-main-2026-09-24.txt`; exit code 0. Report: `reports/check-inputs-main-2026-09-24.txt`, 7,151 B, 302 lines (one input-file line, one line per target, one summary line).

Number of checks: 300 targets × 6 conditions. The checks, as listed in the script's docstring: (1) neither input CSV carries a label column (checked once); (2) the Context block has exactly one `[TARGET]` line, it is a teacher line, and it sits at the expected position within the window; (3) window size equals min(7, rows available before) + 1 + min(7, rows available after), computed independently from `rows_all.csv`; (4) every context line starts with `T:` or `S:`; (5) no gold leaks in the task instruction and the Context block (no `Tag`/`StudentTag`, no `Tag <number>` pattern, no category name, no `nan`/`[MISSING]` stand-in), and each category name exactly once in the output instruction; (6) the Context block is byte-identical across all conditions; (7) `build_prompt()` equals the blank-line join of `prompt_parts()`. Before these checks the script refuses any target that is not an eligible row of `data/frame.csv`.

Result: last line `All checks passed for 300 target(s) x 6 conditions.`; lines containing `PASS` 300, lines containing `FAIL` 0.

## 4. Token matching

Command: `python scripts/check_token_matching.py $(tail -n +2 samples/main_targets.csv)` (the 300 source_ids as positional arguments); exit code 0. Report: `reports/token-matching-check-2026-09-24.txt`, 138,672 B.

Report header: `Script commit: 6673383fb28476740c5ee1d22aa969b769e5c391`; `tiktoken 0.14.0, encoding o200k_base`.

Result line: `RESULT: 0 failing condition/source_id pairs; 27000 site checks run`. Lines beginning with `PASS` 1,200 (300 targets × 4 replacement conditions), lines beginning with `FAIL` 0; 300 distinct source_ids in the report; 90 site checks per target (negative_control 1, definition_replacement 6, example_replacement 72, exclusion_rule_replacement 11), 27,000 in total. The baseline and names_only conditions are not length-matched by construction: the script iterates over `LETTER_CONDITION` in `scripts/manual_sites.py`, which lists the four replacement conditions only.

## 5. Dry run

Command:

```
python scripts/run_experiment.py --run-id main-2026-09-24-dryrun --pass 1 --input samples/main_targets.csv --concurrency 4 --timeout 60 --backoff-initial 2 --backoff-max 60 --failure-threshold 10 --dry-run
```

stdout: `wrote manifest_pass1.json: 5400 calls, seed 20260918`; exit code 0.

Files produced under `runs/main-2026-09-24-dryrun/` (git-ignored, `.gitignore` rule `runs/*`): `manifest_pass1.json` 601,442 B; `prompts.jsonl` 14,358,858 B. `run.lock` absent after the run; no attempts file.

| manifest field | Value |
| --- | --- |
| run_id | `main-2026-09-24-dryrun` |
| created_at | 2026-09-24T03:48:59.326232+00:00 |
| git_commit | `6673383fb28476740c5ee1d22aa969b769e5c391` |
| seed | 20260918 |
| concurrency / timeout / backoff initial, max / failure_threshold | 4 / 60.0 s / 2.0 s, 60.0 s / 10 (`max_retries` 0) |
| model | `gpt-5.5-2026-04-23` |
| schema enum count | 7 |
| n_calls | 5400 |
| calls per repeat | 1: 1800, 2: 1800, 3: 1800 |
| input_file.path | `samples/main_targets.csv` |
| input_file.sha256 | `18ec7cd05b472fb26cbf64c983a9f84614a58dc26a7ec7f4f5b7329fd19553fe` |
| prompts_sha256 | `4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140` |

`prompts.jsonl`: 1,800 rows (one per (utterance_id, condition)); file sha256 recomputed as `4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140`, equal to the manifest's `prompts_sha256`.

plan_pass1 recomputation: `run_experiment.plan_pass1(ids, PASS_SEEDS[1])` on the 300 ids of `samples/main_targets.csv` in file order reproduces the manifest call list; all 5,400 (order_index, utterance_id, condition, repeat) tuples are identical, and each repeat block covers the 1,800 (utterance_id, condition) pairs.

## 6. prompts.jsonl checks

Computed from `runs/main-2026-09-24-dryrun/prompts.jsonl` with pandas, json and hashlib only. Criteria: the gold-leak patterns are the five `GOLD_PATTERNS` of `scripts/check_inputs.py` (lines 47–53: `StudentTag`, `\bTag\b`, `\bTag\s*[:=]?\s*\d`, `\[MISSING\]`, `^(\[TARGET\] )?[TS]:\s*nan\s*$`) and the seven `CATEGORY_NAMES` (`scripts/build_inputs.py` line 91, from `scripts/tags.py`); the scan covers the task instruction and the Context block, not the manual, and each category name must occur exactly once in the Output instruction, the same rule as `scan_gold` and check 5 of `check_inputs.py`; the hash is `hashlib.sha256(text.encode("utf-8")).hexdigest()`, the definition of `sha256_text` in `scripts/run_experiment.py` (lines 87–88).

| Item | Value |
| --- | --- |
| Rows | 1,800 |
| utterance_id set size; equals the `samples/main_targets.csv` set | 300; True |
| Rows per condition | baseline 300, definition_replacement 300, example_replacement 300, exclusion_rule_replacement 300, negative_control 300, names_only 300 |
| Rows whose Context block contains `[TARGET]` ≠ 1 time | 0 |
| Rows whose whole prompt contains `[TARGET]` exactly 2 times | 1,800 (see note) |
| Rows whose `[TARGET] T:` line count ≠ 1 | 0 |
| Rows with any of the five gold-leak patterns in task instruction + Context block | 0 for each pattern |
| Rows with a category name in task instruction + Context block | 0 |
| Rows where any category name occurs ≠ 1 time in the Output instruction | 0 |
| names_only rows containing `Coding manual` | 0 |
| Rows whose prompt contains a local absolute path (home-directory prefix) | 0 |
| Rows where the recomputed sha256 differs from `prompt_sha256` | 0 |

Note on the `[TARGET]` counts: in every row the literal `[TARGET]` occurs twice in the whole prompt because `TASK_INSTRUCTION` (`scripts/build_inputs.py` lines 94–101) contains it once, in the sentence "Exactly one line is marked [TARGET].", and the Context block contains the marker once. `check_inputs.py` (line 110) counts within the Context block only, where the count is 1 in all 1,800 rows. The task-instruction sentence is part of the frozen `build_inputs.py` and is the same as in the validation and pilot inputs.

## 7. Development-target overlap

Recomputed from `samples/main_targets.csv` and `samples/dev_targets.csv` (pandas, `source_id` cast to int):

```
main_ids = set(int(x) for x in pd.read_csv("samples/main_targets.csv", keep_default_na=False, na_values=[""])["source_id"])
dev_ids = set(int(x) for x in pd.read_csv("samples/dev_targets.csv", keep_default_na=False, na_values=[""])["source_id"])
len(main_ids & dev_ids)
```

Output: `0`.

## 8. Changes made after inspecting output

None. No script, prompt template, condition file, decision document or sample was changed during Roadmap 13.

## 9. Expected prompts_sha256 for Roadmap 14

| Item | Expected value |
| --- | --- |
| prompts_sha256 of the main run | `4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140` |
| n_calls | 5400 |
| input_file.sha256 | `18ec7cd05b472fb26cbf64c983a9f84614a58dc26a7ec7f4f5b7329fd19553fe` |

Rule: Before the first API call of the main run, Roadmap 14 runs a dry run at the execution commit (run_id main-<date>-precheck-dryrun) and compares its prompts_sha256 with the expected value above. If the values differ, the actual run is not started. The actual run's manifest prompts_sha256 is compared again after the run. No change to run_experiment.py is required for this rule.

run_id convention for Roadmap 14: `main-<date>-precheck-dryrun` for the pre-check dry run and `main-<date>` for the actual run (5.7.5 prefix `main-`; a dry run and a real run use different run_ids because the runner refuses a re-run when `manifest_pass1.json` exists).
