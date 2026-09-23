## 5.7 Tool validation (Roadmap 9)

This section fixes the rules of tool validation before any validation output is inspected; the execution results and any changes made afterwards are recorded separately in `reports/tool-validation-record-<date>.md`.

### 5.7.1 Purpose and scope

[decided 2026-09-23]

Tool validation checks that the assembled request presents the correct target utterance and the coding task, that the model output maps to the seven categories of `scripts/tags.py`, and that each condition implements its specified manipulation (3.1, 3.2, 3.3). The verification level is that of an output-level coding study: no claim about cognitive mechanism is made and no minimum κ is required. Low agreement alone is not a failure criterion.

Implementation of each manipulation is confirmed by static checks before any API call: `scripts/check_inputs.py`, `scripts/check_token_matching.py`, and human reading of the assembled prompts. κ, Δκ and output patterns from validation calls are diagnostic information that may prompt further inspection; they do not by themselves establish an implementation defect.

Basis: the research claim concerns agreement between LLM output and human codes under specified manual manipulations (1.2). What must be verified is that the instrument presents the intended input and that its output is interpretable, not that the model reaches a given level of agreement.

### 5.7.2 Development targets D

[decided 2026-09-23]

D consists of 2 utterances per Tag (0–6) drawn from the eligible rows of `data/frame.csv` joined with `data/scoring_labels.csv` on `source_id`, using `numpy.random.default_rng(20260923)`, Tags in ascending order, `source_id` sorted ascending within each Tag, and `rng.choice(size=2, replace=False)`; plus three prespecified boundary cases: `source_id` 0 (first row of a transcript), 7 (full ±7 context window on both sides) and 23541 (a row with empty utterance text inside the window). A row drawn in both steps is kept once with its boundary reason. Result: 17 targets, no overlap. Script: `scripts/build_dev_targets.py` (commit `fc5f61b`). List: `samples/dev_targets.csv` (columns `source_id` and `selection_reason` only; no label column). Selection report: `reports/dev-targets-2026-09-23.txt`.

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

The same D is used for tool validation (Roadmap 9) and for the procedural pilot (Roadmap 10). The pilot sends new API requests; validation responses are not reused.

D is excluded from target selection in the main experiment (2.3, revision of 2026-09-23). The original eligible population N = 150,644 (2.1.2) is preserved as a record; the inferential population and sampling frame of the main study are 150,644 − |D| = 150,627. The exclusion is at the target level only: D rows are not removed from the ±7 context window of any other utterance (5.1 unchanged).

Basis: any instrument change made after inspecting validation output was informed by these utterances. Excluding them from the main sample removes the possibility that the instrument was fitted to items it is later scored on.

### 5.7.3 Changes permitted and prohibited after inspecting validation output

[decided 2026-09-23]

Permitted, and only when a defect is confirmed by re-reading the raw responses, the prompts and the run records: task-instruction and output-instruction wording; serialisation format (`T:`/`S:` prefixes, the `Context:` header, section separation); the target marker format; the rendering of empty-text rows; response interpretation, parser and category-mapping code; record format.

Prohibited regardless of the results: component boundaries and replacement targets (3.1); the filler symbol and construction rule (3.2); the condition list and the negative-control background passage; the names-only role (3.3); the model snapshot and parameters (5.2); repetition, aggregation and tie rules (5.4); execution order and seeds (5.6); scorer and bootstrap rules (6); the sampling design (2.3).

The same lists govern the procedural pilot (Roadmap 10), where "result" means a procedural failure; changes there are limited to record format, response-interpretation code and the five operational settings (5.6.4).

Basis: the permitted items concern whether the intended input reaches the model and whether its output is read correctly. The prohibited items define the manipulation, the estimand and the analysis; changing them after seeing output would make the comparison depend on the observed responses.

### 5.7.4 Agreement computation in validation

[decided 2026-09-23]

`scripts/score_run.py` is applied to the validation run unchanged, for all six conditions. The values are recorded in the validation record with the statement that they are diagnostic and not a pass criterion, and are kept separate from the pilot records (5.5).

Anomalies that warrant inspection: a category never produced under any condition; systematic disagreement with the human labels; responses that appear to code a row other than the target; an excessive number of invalid responses. The level of κ, the direction of Δκ and the size of the negative-control effect are not anomalies.

With n ≤ 17, undefined κ and degenerate intervals are expected outcomes of the rules in 6.2, not defects.

Basis: on 17 items the analysis-set marginals are sparse, so κ is often undefined and intervals are withheld or degenerate under 6.2.2 and 6.2.3; running the scorer here checks that the scoring pipeline runs end to end on real records, not the size of any effect.

### 5.7.5 Run identifiers and provisional operational settings

[decided 2026-09-23]

`run_id` prefixes: `validation-`, `pilot-`, `main-`. A dry run and a real run use different `run_id`s (`validation-<date>-dryrun`, `validation-<date>`) because `scripts/run_experiment.py` refuses a re-run when `manifest_pass1.json` exists.

Provisional operational settings for validation: concurrency 4, timeout 60, backoff-initial 2, backoff-max 60, failure-threshold 10. Source: the usage example in `scripts/run_experiment.py`; these are not validated values. Only concurrency = 4 coincides with the pilot starting value in 5.6.4. The final values are fixed in the procedural pilot (Roadmap 10); the items marked [unresolved — pilot operational setting] in 5.6.4 remain open until then.

The input file for both the static checks and the validation run is `samples/dev_targets.csv`.

Basis: the runner has no defaults for these settings (5.6.4), so a validation run needs explicit values; taking them from the documented usage example keeps the provisional choice traceable without treating it as a decision about the main run.
