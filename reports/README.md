# reports/

This folder holds the records produced while the study was carried out. Files are kept in a flat layout with the date of creation in each name, because several records refer to one another by path. The grouping below is a reading guide only. The rules that these records follow are indexed in [`DECISIONS.md`](../DECISIONS.md).

## Final report

- `final-research-report-2026-09-25.md`: the study report with the research question, design, results and limitations. First draft, not independently audited.

## Execution and analysis records

- `protocol-freeze-record-2026-09-24.md`: the files frozen before the main sample was drawn, with their hashes, and every later change registered after the freeze.
- `main-sample-manifest-2026-09-24.json`: the record of the main-experiment sampling, with the frame and development-target hashes, the sampling rule, the seed and generator, the commit it ran on, the hash of `samples/main_targets.csv` and the checks on the drawn sample.
- `procedural-pilot-record-2026-09-24.md`: the procedural pilot used to fix the operational settings of the runner.
- `main-run-record-2026-09-24.md`: the main data collection run, its passes and its execution environment.
- `completeness-report-2026-09-24.md`: the check that every planned call terminated and every item has a final label before scoring.
- `main-scoring-record-2026-09-24.md`: the scoring run, its inputs and its outputs.

## Validation of the data

- `population-count-check-2026-09-14.txt`: counts of teacher rows and categories in the source data.
- `sampling-frame-and-label-check-2026-09-14.txt`: the check of the sampling frame and of the tag-to-category mapping.
- `frame-summary-2026-09-14.txt`: the first summary of the built frame.
- `frame-summary-2026-09-15.txt`: the summary after the eligibility column and the eligible counts were added.
- `heldout-structure-check-2026-09-15.txt`: the structure check of the held-out file.
- `dev-targets-2026-09-23.txt`: the development targets used for tool validation and the pilot.

## Validation of the inputs

- `manual-inventory-check-2026-09-15.txt`: the coding-manual transcription checked against the component inventory.
- `replacement-manifest-summary-2026-09-15.txt`: the replacement sites for each condition.
- `symbol-probe-2026-09-15.txt`: the comparison of candidate placeholder symbols.
- `build-conditions-2026-09-15.txt`: the build of the condition manuals, including the selected placeholder symbol.
- `token-matching-check-2026-09-15.txt`, `token-matching-check-2026-09-23.txt` and `token-matching-check-2026-09-24.txt`: the token-count and token-position checks of the placeholders, repeated as the target set grew.
- `input-examples-2026-09-15.txt`: prompt structure for selected utterances, with the manual position left as a placeholder.
- `input-examples-2026-09-23.txt`: fully assembled prompts for selected utterances using the condition manuals.
- `api-request-test-2026-09-15.txt`: the technical test of the API request specification.
- `tool-validation-record-2026-09-23.md`: the tool validation run on the development targets.
- `check-inputs-main-2026-09-24.txt`: the automated checks of the main-experiment prompts.
- `input-verification-2026-09-24.md`: the full verification of the main-experiment inputs before the main run.

## Changes, deviations and errata

- `heldout-evaluation-decision-2026-09-24.md`: the decision to omit the held-out evaluation, recorded as a deviation from the original plan after main-run data collection and before any main-study result was computed or examined.
- `documentation-errata-2026-09-24.md`: stale wording and terminology differences found before scoring.
- `documentation-errata-post-scoring-2026-09-25.md`: documentation corrections recorded after scoring.