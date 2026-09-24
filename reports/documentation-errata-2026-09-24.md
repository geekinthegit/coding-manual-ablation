# Documentation errata (2026-09-24)

This document records stale wording and terminology differences in the repository documentation that were identified during Roadmap 15. The text of the frozen decision documents was not edited before main-study scoring, and the items recorded here do not change the protocol. Each item states the location, the current wording, the fact that currently holds, and the basis for that fact.

## A. Known stale or inaccurate documentation

1. `decisions/05-4-repetition-and-label-aggregation.md:31`
   - Current wording: "Their placement within the run is recorded as pass 2."
   - Current fact: the first tie-break call (repeat 4) is recorded as pass 2 and the second tie-break call (repeat 5) as pass 3.
   - Basis: `decisions/05-6-execution-order-and-run-records.md:23` (5.6.1: "pass 2 makes repeat 4 … pass 3 makes repeat 5"); `scripts/run_experiment.py:66-67` (`PASS_SEEDS`, `PASS_REPEAT = {2: R_PLANNED + 1, 3: R_PLANNED + 2}`).

2. `decisions/05-6-execution-order-and-run-records.md:41`
   - Current wording: "Pass 2 uses the same file."
   - Current fact: pass 2 and pass 3 both use the `prompts.jsonl` written before pass 1.
   - Basis: `scripts/run_experiment.py:903` (`prepare_tiebreak_pass` records the sha256 of the existing `run_dir / "prompts.jsonl"` in the manifest of pass 2 or 3); `scripts/run_experiment.py:982` (a fresh pass of any number loads that file); `scripts/run_experiment.py:769-770` (`verify_for_resume` requires the pairs of pass 2 and later to be a subset of that file).

3. `decisions/05-6-execution-order-and-run-records.md:90`
   - Current wording: "The intended sequence is `--dry-run` on a clean tree, then `--resume`."
   - Current fact: the dry run and the real run use different `run_id`s; the real run is started as a fresh run, not by `--resume` of the dry run.
   - Basis: `decisions/05-7-tool-validation.md:75` ("A dry run and a real run use different `run_id`s … because `scripts/run_experiment.py` refuses a re-run when `manifest_pass1.json` exists"); `reports/main-run-record-2026-09-24.md` §3–§4 (`main-2026-09-24-precheck-dryrun`, then `main-2026-09-24`).

4. Sentences written before the step they describe was completed:
   - `decisions/05-2-model-and-api-parameters.md:114`: "The same scripts are run on the 300 main-sample inputs before the first main-run call." Current fact: this verification was completed in Roadmap 13. Basis: `reports/input-verification-2026-09-24.md`, `reports/check-inputs-main-2026-09-24.txt`, `reports/token-matching-check-2026-09-24.txt`.
   - `decisions/05-2-model-and-api-parameters.md:120`: "Status: … the main-sample inputs are verified with the same scripts before the first main-run call." Current fact and basis: as in the previous item.
   - `decisions/02-3-sampling-design.md:13`: "The random seed and sampling script for the main draw are not yet fixed and will be added when the sample is drawn (Roadmap 12)." Current fact: the seed and script were recorded. Basis: `decisions/02-3-sampling-design.md:15` (Revision note of 2026-09-24).
   - `decisions/06-analysis.md:104`: "For the future CI-policy check, …". Current fact: the CI-policy fixtures are implemented and passed. Basis: `decisions/06-analysis.md:79` (`tests/test_scorer_bootstrap.py`, passed on 2026-09-22, commit `df0963f`).

5. `scripts/scorer.py:8` (module docstring)
   - Current wording: "The report and the CLI are not implemented here yet."
   - Current fact: the report and the command-line entry point are implemented in `scripts/score_run.py`.
   - Basis: `scripts/score_run.py:1-24` (module docstring) and `scripts/score_run.py:260-273` (`main`). The code file is not modified by this clean-up.

## B. Editorial and terminology notes (no substantive inconsistency)

1. Names-only terminology. Terminology varies across documents (reference, diagnostic, condition, role); all refer to the same `names_only` condition, whose role is defined in 3.3. Locations:
   - "reference": `decisions/03-3-names-only-diagnostic.md:1`, `:5`, `:13`; `decisions/05-3-call-unit-and-api-request.md:52`; `decisions/05-4-repetition-and-label-aggregation.md:5`
   - "diagnostic": `DECISIONS.md:17`; `decisions/03-1-manual-component-definition.md:119`; `decisions/05-1-context-specification.md:21`; `decisions/05-2-model-and-api-parameters.md:42`, `:59`; the file name `decisions/03-3-names-only-diagnostic.md`
   - "condition": `decisions/02-3-sampling-design.md:11`
   - "role": `decisions/05-7-tool-validation.md:53`; `decisions/06-analysis.md:3`

2. `decisions/05-2-model-and-api-parameters.md` §5.2.1: the local `tiktoken` compatibility check of 2026-09-09 is described twice, in line 10 (requirement 1) and in lines 27–31.

3. `decisions/05-6-execution-order-and-run-records.md:19` and `:41`: the fixed number 1,800 is the number of (utterance, condition) pairs of the main experiment, 300 targets × 6 conditions.

4. Roadmap references inside decision documents denote the project's order of work and are not part of any rule: `decisions/02-3-sampling-design.md:13` (Roadmap 12); `decisions/04-2-repeated-call-reliability.md:23` (roadmap step 15); `decisions/05-3-call-unit-and-api-request.md:118` (roadmap 7); `decisions/05-4-repetition-and-label-aggregation.md:31` (roadmap 7), `:85` and `:87` (roadmap step 15); `decisions/05-6-execution-order-and-run-records.md:160` (roadmap 11); `decisions/05-7-tool-validation.md:1` (Roadmap 9), `:41` (Roadmap 9, Roadmap 10), `:55` and `:77` (Roadmap 10).

5. `decisions/03-1-manual-component-definition.md:124`: typographical error "diagnos" in "Names-only diagnos reference".

6. `DECISIONS.md` table of contents: sections 4.1, 4.3, 7 and 8 are listed but have no document file; the section heading of 4 and 5 also linked to overview files that do not exist. In this clean-up the links on the section headings of 4, 5, 7 and 8 were removed, so these headings have the same form as the heading of section 3.

7. Teacher names. Section 2.1.3(a) is a substitution rule for examples quoted in study documents. `reports/input-examples-2026-09-15.txt` is treated as a prompt-record artifact generated for input verification, so it was not redacted in this clean-up.

## C. Changes made in this clean-up

- `decisions/02-2-development-and-held-out-sets.md`: a Revision note was appended that points to the held-out omission decision; the text of 2.2.3 is unchanged.
- `DECISIONS.md`: table-of-contents clean-up (section-heading links to non-existent files removed, absolute URLs replaced by repository-relative links, one list marker unified).
- `reports/frame-summary-2026-09-14.txt`, `reports/frame-summary-2026-09-15.txt`, `reports/heldout-structure-check-2026-09-15.txt`, `reports/manual-inventory-check-2026-09-15.txt`: the local absolute path in one line of each file was replaced by `<local path>`, keeping the file name at the end of the path; numerical and verification content is unchanged.
- This errata document was written.

The sha256 of each changed or added file is recorded in `reports/protocol-freeze-record-2026-09-24.md`, section "Post-freeze documentation updates (no protocol change)".
