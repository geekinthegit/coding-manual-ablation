
This project used the six-stage workflow in [Lin (2026), *A validity-guided workflow for robust large language model research in psychology*](https://doi.org/10.3758/s13428-026-03073-2) as its overall structure with adaptations for the study's specific design. This document links each stage to the relevant study records.
The decision documents cite the earlier arXiv version of this paper as Lin (2025). This document cites the published version.

## Stage 1. Define the research goal

**Classification: LLM as a research tool** (Lin, Table 1).

This study uses an LLM as a coding tool and tests how replacing coding-manual components with placeholders changes its agreement with human labels. Two notes in Table 1 applied.

- note 4: the reference is an existing standard—human coders' labels from TalkMoves
- note 6: the study experiments on the tool itself as in the paper's example of prompting strategies affecting classification accuracy.

The study does not assess psychological constructs in the model. Its findings provide no evidence about human cognition, human-like processes in the model, or the internal mechanisms of individual manual components.


### Required validity evidence for a research tool

| Validity evidence | Table 1 requirement (Research Tool) | Application to this study | Where documented |
|:---|:---|:---|:---|
| Content validity | Required | Applies. The coding categories and the manual come from the TalkMoves corpus (02-1 §2.1.1). The manual placed in the prompt is Chapter 1, sections 1.1–1.6 (03-1 §3.1.1); it was extracted with pdftotext, corrected by rule, and compared against the PDF token by token (manual inventory check). Every text unit in Chapter 1 is assigned to one of types a–i (03-1 §3.1.2–3.1.3, §3.1.8), which is the basis for separating definitions, examples, and exclusion rules. Input checks confirm the accuracy of the implementation; they are not presented as complete evidence of content validity. | [02-1](../decisions/02-1-dataset-selection-and-scope.md), [03-1](../decisions/03-1-manual-component-definition.md), [manual inventory check](../reports/manual-inventory-check-2026-09-15.txt) |
| Reliability (test-retest, parallel forms) | Note 1: required for tools intended for repeated use or scaled application | Applies to the extent of the claim. This study investigates Δκ for a fixed prompt and aggregation procedure: R = 3 independent calls per item-condition, plurality aggregation, and up to five repeats for ties (05-4 §5.4.1–5.4.3). Repeated-call indicators are reported per condition as descriptive statistics only (04-2 §4.2.1–4.2.5; observed values in the scoring record §10 and the pilot record §6). The bootstrap does not separately estimate variability from rerunning the API (06 §6.3), and a high-repeat auxiliary study was considered but not adopted (06 §6.4). Parallel-forms reliability (semantically equivalent prompt variants) was not performed. Three calls per item are not presented as completed reliability validation. | [05-4](../decisions/05-4-repetition-and-label-aggregation.md), [04-2](../decisions/04-2-repeated-call-reliability.md), [06-analysis](../decisions/06-analysis.md), [scoring record](../reports/main-scoring-record-2026-09-24.md), [pilot record](../reports/procedural-pilot-record-2026-09-24.md) |
| Internal consistency | Note 2: only for multi-item scales measuring one construct | Not applicable. The seven coding categories are not treated as scale items, and no Cronbach's α or similar statistic is computed. | |
| Internal structure | N/A | Not required. No factor analysis of a psychological structure of the model is added. | |
| Response process evidence | N/A | Not required. The study does not claim to show which process led the model to a label, and it makes no claim about internal mechanisms. | |
| Convergent / discriminant validation | Note 4: required when validating a tool against an existing standard | Relevant for the comparison with human labels. The human labels are the reference standard against which agreement is measured (01 §1.1); they come from the TalkMoves corpus, and the tag mapping was verified (02-1 §2.1.1, §2.1.3). κ is ordinary unweighted Cohen's κ against those labels (06 §6.1.1), and no minimum κ is required for the tool to pass validation (05-7 §5.7.1). Agreement is a claim about outputs only (01 §1.2.2); the study is a methodological pre-study (01 §1.2.3). Limits of the human labels themselves are recorded (tool-validation record §7; final report §15). A separate discriminant-validity study is not required by Table 1. | [01](../decisions/01-research-question.md), [02-1](../decisions/02-1-dataset-selection-and-scope.md), [05-7](../decisions/05-7-tool-validation.md), [06-analysis](../decisions/06-analysis.md), [tool-validation record](../reports/tool-validation-record-2026-09-23.md), [final report](../reports/final-research-report-2026-09-25.md) |
| Consequential evidence | Recommended | Not addressed in this repository. The consequences of misclassification and the limits of use in applications are not discussed in the decision documents or the final report. | |
| Internal validity | Note 6: applies when the experiment is on the tool itself | Applies. The same 300 utterances are used in every condition (02-3 §2.3.2); context blocks are byte-identical across conditions (05-1 §5.1.6); endpoint, schema, model, and settings are identical (05-3 §5.3.8; freeze record §3). Length and position are controlled by exact token matching with no tolerance (03-2 §3.2.1, §3.2.3), verified for 300 targets × 6 conditions (input verification §3–4). Call order is shuffled so that no condition runs in a distinct time period (05-3 §5.3.10); all 5,400 calls returned HTTP 200 and the parser is deterministic (main-run record §4, §6). Differences not controlled are stated: the placeholder is not shown to be behaviorally neutral (03-2); provider-side serialization is not observed (03-2); the names-only condition is not length-matched (03-3; input verification); the negative control differs in volume (03-1); prompt caching was observed at 79.01% and is reported as operational information only (main-run record §8). | [02-3](../decisions/02-3-sampling-design.md), [03-1](../decisions/03-1-manual-component-definition.md), [03-2](../decisions/03-2-placeholder-specification.md), [03-3](../decisions/03-3-names-only-diagnostic.md), [05-1](../decisions/05-1-context-specification.md), [05-3](../decisions/05-3-call-unit-and-api-request.md), [input verification](../reports/input-verification-2026-09-24.md), [freeze record](../reports/protocol-freeze-record-2026-09-24.md), [main-run record](../reports/main-run-record-2026-09-24.md) |
| External validity | N/A | No additional experiments on other models or corpora are required by Table 1. The results support only the prespecified population-level claim about the eligible target population (N = 150,644), within its category distribution (02-3 §2.3.8); the sample was drawn from the main-experiment sampling frame (N = 150,627). Results on TalkMoves do not generalize to the later study's coding manual (01 §1.2.3); single model and single setting are stated as limitations (final report §15). The held-out evaluation was omitted after data collection and before any κ, Δκ, or bootstrap result was computed; this is recorded as a post-freeze deviation (held-out decision record; freeze record; 02-2 §2.2.3 revision note). | [01](../decisions/01-research-question.md), [02-2](../decisions/02-2-development-and-held-out-sets.md), [02-3](../decisions/02-3-sampling-design.md), [held-out decision record](../reports/heldout-evaluation-decision-2026-09-24.md), [freeze record](../reports/protocol-freeze-record-2026-09-24.md), [final report](../reports/final-research-report-2026-09-25.md) |
| Construct validity of the manipulation | N/A | No validation that a psychological construct was manipulated is needed. Each condition is defined by two lists, what is replaced and what remains (03-1 §3.1.5–3.1.7); the placeholder form is fixed (03-2 §3.2.2). The independent causal effect or intrinsic importance of a component is outside the claim (01 §1.2.1); Δκ is not a pure estimate of the semantic contribution of the replaced component (03-2 §3.2.4), and a change is not evidence that the component is unnecessary (03-1). | [01](../decisions/01-research-question.md), [03-1](../decisions/03-1-manual-component-definition.md), [03-2](../decisions/03-2-placeholder-specification.md) |
| Statistical conclusion validity | Note 9: applies when the tool produces quantitative data for later statistical analysis | Applies. Repeated calls construct a label and are not additional sampled observations (06 §6.1.1); conditions are compared on paired sets, with no imputation of missing final labels (06 §6.1.2; 02-3 §2.3.7). Ties and insufficient valid repeats are handled by rule (05-4 §5.4.2–5.4.3, §5.4.8). Intervals are percentile bootstrap intervals from 10,000 replicates with seed 20260919, individual-statistic rather than simultaneous coverage; undefined κ and degenerate intervals are handled by rule (06 §6.2.1–6.2.3). The sample size is a prespecified, resource-constrained evaluation size (02-3 §2.3.5–2.3.6, §2.3.8). The bootstrap approximates sampling uncertainty only (06 §6.3). Executed values are in the scoring record (§3, §8–9). | [02-3](../decisions/02-3-sampling-design.md), [05-4](../decisions/05-4-repetition-and-label-aggregation.md), [06-analysis](../decisions/06-analysis.md), [scoring record](../reports/main-scoring-record-2026-09-24.md) |

## Stage 2. Develop and Validate the Computational Instrument

**Pathway A: Research tool—classification and coding**

Lin (2026) treats a classification tool's central claim as functional: the LLM can stand in for human coders. This study did not make that claim. Its target was the change in agreement with human labels under specified manual replacements, not the performance of an optimized prompt on new data. The study therefore did not perform iterative performance-based prompt refinement or held-out predictive validation. Validation was scoped to whether the procedure ran as designed:

| Item | This study | Where documented |
|:---|:---|:---|
| Measurement standard | Human coder labels in TalkMoves fixed as the reference | [02-1](../decisions/02-1-dataset-selection-and-scope.md) |
| Agreement metric | Unweighted κ, paired Δκ, bootstrap intervals prespecified | [06](../decisions/06-analysis.md); [02-3](../decisions/02-3-sampling-design.md) |
| Prompt | Manual text used unchanged; prompt fixed before validation and not changed afterwards | [05-1 §5.1.4](../decisions/05-1-context-specification.md#514-prompt-architecture), [§5.1.6](../decisions/05-1-context-specification.md#516-serialisation-target-marking-and-instruction-wording); [protocol freeze record](../reports/protocol-freeze-record-2026-09-24.md) |
| Development subset | 17 development utterances, all six conditions; no invalid responses or defects; κ reported as diagnostic only, no refinement | [05-7](../decisions/05-7-tool-validation.md); [tool-validation record](../reports/tool-validation-record-2026-09-23.md) |
| Input verification | All 300 main-sample inputs checked for target utterance, context, and replacement sites | [input verification report](../reports/input-verification-2026-09-24.md) |
| Output format | Structured output restricted to the seven category names | [05-3](../decisions/05-3-call-unit-and-api-request.md); [main-run record](../reports/main-run-record-2026-09-24.md) |

## Stage 3: Design Experiment

### 1. Operationalize the Manipulation and Outcome

In this study, the manipulated object was the coding instruction itself, not a psychological construct.

| Item | This study | Where documented |
|---|---|---|
| Independent variable | Manual condition, with six levels:<br>1. Full-manual baseline<br>2. Definitions replaced with placeholders<br>3. Examples replaced with placeholders<br>4. Exclusion rules replaced with placeholders<br>5. Negative control (Task-irrelevant background passage replaced with placeholders)<br>6. Names-only reference condition | 03-1; 03-3 |
| Dependent outcome | Agreement with fixed human labels, measured by unweighted Cohen's κ. Δκ was prespecified as the difference between each replacement condition and baseline; names-only was excluded from these comparisons | 06; 02-3 |
| Manipulation | In the four replacement conditions, specified manual passages were replaced in place with placeholders matched in token count. | 03-1; 03-2 |
| Resulting claim | How the implemented replacements changed agreement under the tested conditions, not psychological mechanisms or the independent contribution or intrinsic importance of individual manual components | main scoring record (claim boundary) |

### 2. Control Four Categories of Validity Threats
#### 2.1 Internal validity

Applies under Table 1, Note 6 because the experiment manipulated the coding tool itself.

##### 2.1.1 Prompt-level confounds

| Item | This study | Where documented |
|---|---|---|
| Control positional effects | Replacement conditions preserved token count and position relative to baseline. Positions were held fixed rather than randomized | 03-2; input verification |
| Control formatting artifacts | Output schema and label format were held constant across conditions. Label variations were not tested | 05-3 |
| Address scenario reconstruction | The same utterances and byte-identical context blocks were used across conditions. This controlled supplied context; model-inferred background assumptions were not directly tested | 05-1; input verification |
| Keep causal claims within the implemented manipulation | Placeholder neutrality was not established. Claims concern the specified replacements, not the independent contribution of individual manual components | 01; 03-2 |

##### 2.1.2 Technical confounds

| Item | This study | Where documented |
|---|---|---|
| Use and record a fixed model snapshot | The same dated OpenAI API model snapshot (gpt-5.5-2026-04-23) was requested across conditions. The returned model identifier was checked on every response | 05-2; main-run record |
| Hold API parameters constant | Temperature was set to 0, reasoning effort to none, and the same output schema was used across conditions | 05-2; 05-3; main-run record |
| Record collection dates | Collection dates were recorded | main-run record |
| Prevent context accumulation | Each call contained a single user message, with no conversation history or prior output passed into subsequent calls | 05-3 §5.3.10 |


#### 2.2 External validity

N/A in Table 1's research-tool pathway. Claims are limited to the eligible target population of the TalkMoves development set and to the tested model and settings.

#### 2.3 Construct validity

N/A in Table 1's research-tool pathway. The study manipulated coding instructions not a psychological construct. It makes no claims about psychological mechanisms or each component’s independent contribution.

#### 2.3 Statistical conclusion validity

| Item | This study | Where documented |
|---|---|---|
| Do not count repeated responses as independent observations | Repeated calls were used to form the final label and were not counted as additional samples | 05-4 |
| Account for dependence in the data | Condition results for the same utterance were compared as paired sets and resampled with an utterance-level paired bootstrap | 06 |
| Keep inference within what the analysis supports | Missing final labels were not imputed; prespecified comparison rules were applied | 06 |
| | Rules for ties and insufficient valid repeats were set in advance | 05-4 |
| | κ, Δκ, and bootstrap confidence intervals were reported | 06; main scoring record |
| | Intervals were stated to be per-statistic, not simultaneous | 06; main scoring record |
| | Rules were set for undefined κ and degenerate intervals | 06 |
| | The sample of 300 was stated as a prespecified evaluation size set under resource constraints | 02-3 |
| | The bootstrap was stated to approximate sampling uncertainty only | 06; main scoring record |
| Do not overstate results because of low variability | Magnitudes and intervals of κ and Δκ were reported and interpreted together | 06; main scoring record |

### 3. Develop Pre-registration Plan

The study was not registered on a public registry. Instead, the protocol was frozen in the repository before sampling. Every later change was recorded with its date and reason.

| Item | This study | Where documented |
|---|---|---|
| Prompt variations | Six manual conditions and their replacement spans were fixed before the freeze | 03-1; 03-3; protocol freeze record |
| Technical parameters | Model snapshot, temperature, reasoning effort, and output schema were fixed before the freeze | 05-2; 05-3; protocol freeze record |
| Analysis plan | κ, paired Δκ, bootstrap procedure, and missing-label rules were adopted before main-experiment results | 06 |
| Robustness checks | Robustness analyses were outside the study's scope and were not performed. Findings are limited to the tested model snapshot, parameter settings, prompt format, and parsing rules | — |
| Boundary conditions | Population-level inference, no category-level conclusions, and no between-condition contrasts were set in advance | 02-3; 06 |
| Deviations after the freeze | The omission of held-out evaluation was recorded as a post-freeze deviation, after data collection and before scoring | held-out decision record; protocol freeze record |

## Stage 4. Execute and document the experiment

### 1. Specify and Document the Environment

The study used API access only; the web-interface requirements do not apply.

| Item | This study | Where documented |
|---|---|---|
| Model endpoint | Model snapshot `gpt-5.5-2026-04-23` | 05-2 §5.2.1 |
| Technical parameters | Temperature 0, reasoning_effort "none", `max_completion_tokens` 64, and a structured-output schema. `top_p` was not included in the request, so the API default applied | 05-2 §5.2.2; 05-3; run manifest `request_params` |
| Date and time of data collection | The first main-run call started at 2026-09-24T05:43:31Z; every attempt carries `started_at` and `completed_at` timestamps | main-run record §7; 05-6 §5.6.7 |
| Preprocessing and postprocessing | Inputs were serialized with the target utterance marked; responses were parsed into one of seven labels and combined into a final label by plurality | 05-1; 05-4 |
| API version and system specifications | Python 3.13.9, openai SDK 3.8.0, tiktoken 0.14.0 (`o200k_base`), NumPy 2.3.5, with upgrades prohibited until the analysis was complete | 05-2 §5.2.3 |
| Execution record | Each run manifest records the run ID, call list, request parameters, SDK and retry settings, input and prompt hashes, and the runner git commit | 05-6 §5.6.2; `runs/main-2026-09-24/manifest_pass1.json` |

### 2. Execute the Protocol with Transparency

| Item | This study | Where documented |
|---|---|---|
| Follow the frozen plan | A read-only audit by Codex at `d0bd38f` returned NOT READY with three omissions in the freeze record. They were corrected by an append-only commit, and a recheck at `beb3ef9` returned READY. The main run was executed at `beb3ef9` | main-run record §1–2 |
| Execution | 5,400 pass-1 calls all returned HTTP 200; pass 2 made one call to resolve the single remaining tie; pass 3 made no call. Total: 5,401 calls | main-run record §4–5 |
| No change during collection | No script, prompt template, condition file, decision document, sample, or operational setting was changed between the precheck and the completion of data collection | main-run record §7, §9 |
| Document and justify deviations | The one departure from the frozen plan, the omission of held-out evaluation, is recorded in a separate decision record. The original plan in 02-2 §2.2.3 is unchanged and carries a revision note. The reason is given in Stage 2 of this document | held-out decision record; protocol freeze record; 02-2 §2.2.3 |
| Report the original analysis alongside any revision | No analysis was revised. The held-out evaluation was omitted rather than replaced, so there is no revised analysis to report alongside it | held-out decision record |
| Documentation corrections | Errors found after the freeze are listed in two errata files with location, current wording, the correct fact, and its basis; no sentence in a frozen document was edited | documentation errata; errata post-scoring |

### 3. Ensure Data Preservation

| Item | This study | Where documented |
|---|---|---|
| Full prompts as sent | Every prompt exactly as sent is stored in `prompts.jsonl`; each attempt also records its `prompt_sha256` and `request_params` | 05-6 §5.6.7; `runs/main-2026-09-24/` |
| Raw outputs before parsing | Each attempt stores `raw_response`, the HTTP response body as a string before any parsing | 05-6 §5.6.7 |
| Metadata | Each attempt records `started_at`, `completed_at`, `http_status`, `openai_request_id`, `finish_reason`, and token counts including `cached_tokens` | 05-6 §5.6.7 |
| Pre- and post-processing code | Input construction, parsing, and scoring code is committed under `scripts/` | `scripts/` |
| Standardized format | JSONL and CSV | `runs/main-2026-09-24/` |
| Sealed analysis inputs | The label files used for scoring are snapshotted with their hashes registered in the freeze record | `analysis-inputs/`; protocol freeze record |
| Public deposit | The data, code, manual texts, and documentation are in a public GitHub repository under CC BY-NC-SA 4.0, the licence of the source dataset. No archival deposit (e.g., Zenodo) has been made | `LICENSE-DATA` |
| Files not committed | `score_report.txt` and `score_summary.json` contain local absolute paths and are not committed; their hashes are sealed and their content is reproduced in the scoring record | main scoring record |


## Stage 5. Analyze and interpret results

The paper requires data-quality and assumption checks before analysis, explicit handling of the non-independence of LLM outputs (aggregation, multilevel or GEE models, cluster bootstrap, cluster-robust standard errors), robustness analyses across technical settings and task logic, and interpretation that weighs consistency across checks over any single p-value or effect size.

### Data quality and assumption checks

- **Structured output.** Responses were returned under a strict JSON schema with a single `category` field and a seven-name enum, so a value outside the category set could not be returned (05-3 §5.3.4). The parser normalises the value and applies the valid-label criterion, separating invalid responses from Not coded (05-4 §5.4.2). In the main run, all 5,400 pass-1 calls returned HTTP 200 with outcome `success`; no invalid response and no refusal occurred (main-run record §4).
- **Raw-response checks.** In tool validation, five raw responses were compared with the parsed labels (tool-validation record §5); in the main run, six raw responses spread across the call order were compared (main-run record §6); before scoring, the `category` in every `raw_response` was compared with `labels.csv` for all 5,401 calls with 0 mismatches (completeness report §5).
- **Completeness before scoring.** The completeness report ran 17 pass/fail checks (coverage, raw attempts → labels → final labels, an independent recomputation, and status), all PASS; all six conditions have 300 resolved final labels and no other status (completeness report §4–7). The scorer refuses to run unless every call in every pass is terminated and the final labels re-derived from the attempts files match the file on disk (06 §6.1.1; `scripts/scorer.py` `require_run_complete`).
- **Model assumptions.** No regression model is fitted, so residual-based assumption checks do not apply. The conditions under which κ is undefined, and the distinction between an undefined statistic and a degenerate interval such as [0, 0], are handled by rule (06 §6.2.2–6.2.3).

### Non-independence

- **Aggregation.** The three calls per item-condition are aggregated by plurality into one final label, and repeated calls are not counted as observations: "Repeated calls construct a label; they are not additional sampled observations" (06 §6.1.1; 05-4 §5.4.1–5.4.2).
- **Utterance-level paired bootstrap.** Resampling is at the utterance level, with each utterance carrying its labels under all conditions, so the pairing across conditions is preserved in every replicate (06 §6.2.1; 02-3 §2.3.7). This is the paper's cluster-bootstrap strategy with the utterance as the cluster.
- **Not used.** Multilevel models, GEE, and cluster-robust standard errors were not used. The comparison is a single paired Δκ per condition, and no regression model is involved.
- **Transcript-level clustering.** Utterances from the same lesson transcript were not treated as a cluster. This was a design decision, not an oversight: the inferential population is the prespecified eligible target population, the sample is drawn at the utterance level, and the study does not posit a transcript-level superpopulation (02-3 §2.3.7; 06 §6.3). The final report's limitations section (§15) does not discuss this choice separately.

### Robustness

- **Technical robustness.** Not performed. Temperature was fixed at 0, `top_p` was left at the API default, and prompt formatting was identical across conditions (Stages 2–4). A high-repeat auxiliary study was considered and not adopted (06 §6.4).
- **Conceptual robustness.** Two reference conditions serve this role within their stated limits: the negative control shows whether replacing task-irrelevant content by the same procedure changes agreement, and the names-only reference shows agreement when no substantive manual text is supplied. Neither is subtracted from, used to adjust, or used as a threshold for the substantive estimates, and no names-only contrast is created (03-1 §3.1.7; 03-3; 06 §6.5).
- **Computational verification.** The point estimates were recomputed independently without importing the scorer (Roadmap 16-3), and the scoring record was audited independently (Roadmap 16-7). These verify the implementation, not the statistical robustness of the result.

### Calibration of interpretation

- **What is reported.** Per-condition κ, Δκ against the baseline for each replacement condition, and percentile bootstrap intervals from 10,000 replicates with seed 20260919. The intervals are individual-statistic intervals, not simultaneous coverage across the substantive contrasts (06 §6.2.1). No direct contrast between substantive conditions is performed, and no multiplicity adjustment is specified (06 §6.1.2; scoring record §12).
- **Prespecified boundaries.** A small Δκ, an interval containing zero, or a failure to detect a clear difference is not interpreted as evidence of no effect, maintained agreement, or equivalence; no equivalence or noninferiority claim is made (03-1 §3.1.7; 02-3 §2.3.7). A [0, 0] interval is not read as population-level equality (02-3 §2.3.7; 06 §6.2.3). The R = 3 procedure is a label-construction rule and does not establish label stability or optimality (05-4 §5.4.1). The bootstrap approximates sampling uncertainty only and does not estimate variability from rerunning the API (06 §6.3).
- **Repeated-call diagnostics.** Reported per condition as descriptive statistics only; no inferential test, interval, or between-condition contrast is computed on them (04-2; §4.2.5).


### Where this study differs from the workflow

- No technical robustness analysis across parameter settings or prompt formats.
- No multilevel, GEE, or cluster-robust analysis; the design uses aggregation and utterance-level paired resampling only.
- Transcript-level clustering is not modelled, by design; the final report does not list this as a limitation.
- Conceptual robustness is limited to the two reference conditions.

Records: [02-3](../decisions/02-3-sampling-design.md), [03-1](../decisions/03-1-manual-component-definition.md), [03-3](../decisions/03-3-names-only-diagnostic.md), [04-2](../decisions/04-2-repeated-call-reliability.md), [05-3](../decisions/05-3-call-unit-and-api-request.md), [05-4](../decisions/05-4-repetition-and-label-aggregation.md), [06-analysis](../decisions/06-analysis.md), [tool-validation record](../reports/tool-validation-record-2026-09-23.md), [main-run record](../reports/main-run-record-2026-09-24.md), [completeness report](../reports/completeness-report-2026-09-24.md), [scoring record](../reports/main-scoring-record-2026-09-24.md)

## Stage 6. Report and reconceptualize

The paper requires transparent reporting that follows an AI reporting guideline (TRIPOD-LLM or MI-CLEAR-LLM) and a public replication package covering the model and environment, the handling of stochasticity, the prompts and their use, and a statement on data contamination; claims constrained to the evidence, without anthropomorphic language and with observed performance distinguished from inferred competence; use of the findings to refine tools or constructs; and a limitations section that addresses generalization across model versions and the ethical implications.

### Reporting

- **Replication package.** The elements the paper lists are in this repository: model and environment (05-2; run manifests), stochasticity handling (three calls per item-condition, plurality aggregation, tie resolution; 05-4, 06), the prompts exactly as sent and how they were assembled (`runs/main-2026-09-24/prompts.jsonl`; 05-1), the code (`scripts/`), the sealed analysis inputs (`analysis-inputs/`), and the execution, scoring, and verification records (`reports/`). Raw responses and the manual text are published under the source dataset's licence (Stage 4).
- **Final report.** `reports/final-research-report-2026-09-25.md`, headed "Status: first draft; not independently audited" (Roadmap 18-3, corrected in 18-4). No audit of the report has been committed since.
- **Data exposure.** The only statement on prior model exposure is the interpretation boundary of the names-only reference: "Prior model exposure to TalkMoves or related material remains possible" (03-3; cited in the final report §4.5, §13.3, §15). There is no contamination statement covering the baseline and replacement conditions, and the training-data cutoff of `gpt-5.5-2026-04-23` is not recorded anywhere in the repository.
- **Not done.** No reporting guideline (TRIPOD-LLM, MI-CLEAR-LLM) was followed. The reproducibility checklist named in the Roadmap 18 title was planned (18-1) but no checklist file was produced; `docs/reproduction.md` is the intended location. No external deposit (Stage 4).

### Claims constrained to evidence

- The claim boundaries were fixed before data collection (01 §1.2) and the interpretation statements in the report were checked against the frozen documents (Roadmap 16-5). What is reported is agreement with the human labels under one prompt, one model snapshot, and one setting; Δκ "is not taken as evidence about what the LLM understands or what human coders relied on" (01, cited in the final report §3). Agreement is a claim about outputs only (01 §1.2.2).
- A search of the final report for anthropomorphic verbs with the model as subject (understand, know, reason, believe, think, intend, decide) found no affirmative use; the single occurrence is the negated boundary sentence above.
- Results are reported for the configuration used only: "All calls used one dated snapshot, `gpt-5.5-2026-04-23`, with temperature 0 and reasoning effort none; results are reported for this configuration only" (final report §15, Single model, single setting). The reason for fixing the snapshot is stated in 05-2 §5.2.1: provider-side model updates can alter behaviour and threaten replicability.

### Use of the findings

- This study measures no psychological construct in the model, so the paper's reconceptualization step, replacing a human-centric construct that fails validation with a computationally grounded one, has no object here.
- What the paper says for a tool-development goal is that the findings inform more robust instruments. In this study that role is limited and stated in advance: the study is "a methodological pre-study for a later human–AI interaction study, examining whether LLM-assisted coding can be used there" (01 §1.2.3). The results on TalkMoves do not transfer to the later study's coding manual; what transfers is the methodological premise that a manual developed for human coders should not be assumed, without validation, to function equivalently as an LLM prompt (01 §1.2.3; final report §14.4). Further directions are listed as questions for new designs, not as findings (final report §14.2).

### Limitations and ethical implications

- **Limitations.** The final report §15 lists thirteen items: rare categories and scope of inference, negative-control volume, placeholder neutrality, scope of token verification, uncertainty scope, label construction, context condition, single model and single setting, reference standard, names-only reference, held-out evaluation, generalization, and documentation.
- **Generalization across model versions.** Addressed by fixing one dated snapshot and reporting for that configuration only (final report §15; 05-2 §5.2.1). No statement generalizes the result to other versions of the model.
- **Ethical implications.** Not addressed. Neither the decision documents nor the final report discusses the consequences of misclassification or the risks of applying the tool (see the Consequential evidence row in Stage 1). The data are publicly licensed classroom transcripts from the TalkMoves corpus; no new human-participant data were collected.

### Where this study differs from the workflow

- No reporting guideline followed; no reproducibility checklist file; no external deposit.
- The final report is a first draft that has not been independently audited.
- No contamination statement for the substantive conditions and no training-data cutoff recorded.
- Ethical and social implications not discussed.
- No reconceptualization step, because no construct in the model is measured.

Records: [01](../decisions/01-research-question.md), [03-3](../decisions/03-3-names-only-diagnostic.md), [05-1](../decisions/05-1-context-specification.md), [05-2](../decisions/05-2-model-and-api-parameters.md), [05-4](../decisions/05-4-repetition-and-label-aggregation.md), [06-analysis](../decisions/06-analysis.md), [final report](../reports/final-research-report-2026-09-25.md), [scoring record](../reports/main-scoring-record-2026-09-24.md), [run files](../runs/main-2026-09-24/), [analysis inputs](../analysis-inputs/)