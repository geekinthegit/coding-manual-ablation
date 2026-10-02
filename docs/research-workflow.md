
This project used the six-stage workflow in [Lin (2026), *A validity-guided workflow for robust large language model research in psychology*](https://doi.org/10.3758/s13428-026-03073-2) as its overall structure with adaptations for the study's specific design. This document links each stage to the relevant study records.
The decision documents cite the earlier arXiv version of this paper as Lin (2025). This document cites the published version.

## Stage 1. Define the research goal

### 1.1 Classification: LLM as a research tool

This study uses an LLM as a coding tool and tests how replacing coding-manual components with placeholders changes its agreement with human labels. Two notes in Table 1 applied.

- note 4: the reference is an existing standard—human coders' labels from TalkMoves
- note 6: the study experiments on the tool itself as in the paper's example of prompting strategies affecting classification accuracy.

The study does not assess psychological constructs in the model. Its findings provide no evidence about human cognition, human-like processes in the model, or the internal mechanisms of individual manual components.


### 1.2 Required validity evidence for a research tool

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

## Stage 3. Design Experiment

### 3.1. Operationalize the Manipulation and Outcome

In this study, the manipulated object was the coding instruction itself, not a psychological construct.

| Item | This study | Where documented |
|---|---|---|
| Independent variable | Manual condition, with six levels:<br>1. Full-manual baseline<br>2. Definitions replaced with placeholders<br>3. Examples replaced with placeholders<br>4. Exclusion rules replaced with placeholders<br>5. Negative control (Task-irrelevant background passage replaced with placeholders)<br>6. Names-only reference condition | 03-1; 03-3 |
| Dependent outcome | Agreement with fixed human labels, measured by unweighted Cohen's κ. Δκ was prespecified as the difference between each replacement condition and baseline; names-only was excluded from these comparisons | 06; 02-3 |
| Manipulation | In the four replacement conditions, specified manual passages were replaced in place with placeholders matched in token count. | 03-1; 03-2 |
| Resulting claim | How the implemented replacements changed agreement under the tested conditions, not psychological mechanisms or the independent contribution or intrinsic importance of individual manual components | main scoring record (claim boundary) |

### 3.2 Control Four Categories of Validity Threats
#### 3.2.1 Internal validity

Applies under Table 1, Note 6 because the experiment manipulated the coding tool itself.

##### 3.2.1.1 Prompt-level confounds

| Item | This study | Where documented |
|---|---|---|
| Control positional effects | Replacement conditions preserved token count and position relative to baseline. Positions were held fixed rather than randomized | 03-2; input verification |
| Control formatting artifacts | Output schema and label format were held constant across conditions. Label variations were not tested | 05-3 |
| Address scenario reconstruction | The same utterances and byte-identical context blocks were used across conditions. This controlled supplied context; model-inferred background assumptions were not directly tested | 05-1; input verification |
| Keep causal claims within the implemented manipulation | Placeholder neutrality was not established. Claims concern the specified replacements, not the independent contribution of individual manual components | 01; 03-2 |

##### 3.2.1.2 Technical confounds

| Item | This study | Where documented |
|---|---|---|
| Use and record a fixed model snapshot | The same dated OpenAI API model snapshot (gpt-5.5-2026-04-23) was requested across conditions. The returned model identifier was checked on every response | 05-2; main-run record |
| Hold API parameters constant | Temperature was set to 0, reasoning effort to none, and the same output schema was used across conditions | 05-2; 05-3; main-run record |
| Record collection dates | Collection dates were recorded | main-run record |
| Prevent context accumulation | Each call contained a single user message, with no conversation history or prior output passed into subsequent calls | 05-3 §5.3.10 |


#### 3.2.2 External validity

N/A in Table 1's research-tool pathway. Claims are limited to the eligible target population of the TalkMoves development set and to the tested model and settings.

#### 3.2.3 Construct validity

N/A in Table 1's research-tool pathway. The study manipulated coding instructions not a psychological construct. It makes no claims about psychological mechanisms or each component’s independent contribution.

#### 3.2.4 Statistical conclusion validity

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

### 3.3 Develop Pre-registration Plan

The study was not registered on a public registry. Instead, the protocol was frozen in the repository before sampling. Every later change was recorded with its date and reason.

| Item | This study | Where documented |
|---|---|---|
| Prompt variations | Six manual conditions and their replacement spans were fixed before the freeze | 03-1; 03-3; protocol freeze record |
| Technical parameters | Model snapshot, temperature, reasoning effort, and output schema were fixed before the freeze | 05-2; 05-3; protocol freeze record |
| Analysis plan | κ, paired Δκ, bootstrap procedure, and missing-label rules were adopted before main-experiment results | 06 |
| Robustness checks | Robustness analyses were outside the study's scope and were not performed. Findings are limited to the tested model snapshot, parameter settings, prompt format, and parsing rules | — |
| Boundary conditions | Population-level inference, no category-level conclusions, and no between-condition contrasts were set in advance | 02-3; 06 |
| Deviations after the freeze | The omission of held-out evaluation was recorded as a post-freeze deviation, after data collection and before scoring | held-out decision record; protocol freeze record |

## Stage 4 Execute and document the experiment

### 4.1 Specify and Document the Environment

The study used API access only; the web-interface requirements do not apply.

| Item | This study | Where documented |
|---|---|---|
| Model endpoint | Model snapshot `gpt-5.5-2026-04-23` | 05-2 §5.2.1 |
| Technical parameters | Temperature 0, reasoning_effort "none", `max_completion_tokens` 64, and a structured-output schema. `top_p` was not included in the request, so the API default applied | 05-2 §5.2.2; 05-3; run manifest `request_params` |
| Date and time of data collection | The first main-run call started at 2026-09-24T05:43:31Z; every attempt carries `started_at` and `completed_at` timestamps | main-run record §7; 05-6 §5.6.7 |
| Preprocessing and postprocessing | Inputs were serialized with the target utterance marked; responses were parsed into one of seven labels and combined into a final label by plurality | 05-1; 05-4 |
| API version and system specifications | Python 3.13.9, openai SDK 3.8.0, tiktoken 0.14.0 (`o200k_base`), NumPy 2.3.5, with upgrades prohibited until the analysis was complete | 05-2 §5.2.3 |
| Execution record | Each run manifest records the run ID, call list, request parameters, SDK and retry settings, input and prompt hashes, and the runner git commit | 05-6 §5.6.2; `runs/main-2026-09-24/manifest_pass1.json` |

### 4.2 Execute the Protocol with Transparency

| Item | This study | Where documented |
|---|---|---|
| Follow the frozen plan | A read-only audit by Codex at `d0bd38f` returned NOT READY with three omissions in the freeze record. They were corrected by an append-only commit, and a recheck at `beb3ef9` returned READY. The main run was executed at `beb3ef9` | main-run record §1–2 |
| Execution | 5,400 pass-1 calls all returned HTTP 200; pass 2 made one call to resolve the single remaining tie; pass 3 made no call. Total: 5,401 calls | main-run record §4–5 |
| No change during collection | No script, prompt template, condition file, decision document, sample, or operational setting was changed between the precheck and the completion of data collection | main-run record §7, §9 |
| Document and justify deviations | The one departure from the frozen plan, the omission of held-out evaluation, is recorded in a separate decision record. The original plan in 02-2 §2.2.3 is unchanged and carries a revision note. The reason is given in Stage 2 of this document | held-out decision record; protocol freeze record; 02-2 §2.2.3 |
| Report the original analysis alongside any revision | No analysis was revised. The held-out evaluation was omitted rather than replaced, so there is no revised analysis to report alongside it | held-out decision record |
| Documentation corrections | Errors found after the freeze are listed in two errata files with location, current wording, the correct fact, and its basis; no sentence in a frozen document was edited | documentation errata; errata post-scoring |

### 4.3 Ensure Data Preservation

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


## Stage 5. Analyze and Interpret Results

### 5.1 Perform Data Quality and Assumption Checks

| Item | This study | Where documented |
|---|---|---|
| Qualitative data evaluation | In tool validation, all 306 responses were inspected against four prespecified anomaly types: a category never produced, systematic disagreement with human labels, coding a row other than the target, and excessive invalid responses. None was found. The two utterances that disagreed with human labels were traced back to the source data and judged not to be tool defects | 05-7; tool-validation record §7 |
| | In the main run, every raw response was preserved and automatically classified against the invalid-response criteria (refusal, truncation, malformed JSON, schema mismatch, label outside the category set), with the reason recorded. All 5,400 pass-1 responses were valid. Six raw responses were compared with their parsed labels | 05-4 §5.4.5; 05-6 §5.6.7; main-run record §4 |
| | Output was restricted to one of seven category names, so nonsensical free text or hallucinations could not appear | 05-3 §5.3.4 |
| | Human inspection of response content was carried out in tool validation; the main run relied on automatic checks and a six-response sample comparison | — |
| Statistical assumption checks | No regression model was fitted, so residual-based checks do not apply | — |
| | For the analyses used (unweighted κ and paired percentile bootstrap), rules for undefined κ and degenerate intervals were set in advance; neither occurred in the main analysis | 06; main scoring record |
| | The bootstrap's premises (simple random sampling and independence at the utterance level) were set by design and were not tested against the data | 02-3; 06 |
| | Separately from assumption checks, the scorer was verified with synthetic-data tests, and point estimates were independently recomputed with no mismatches | 06; main scoring record |

### 5.2 Address Data Non-Independence

| Item | This study | Where documented |
|---|---|---|
| Within-model clustering | The three calls per utterance-condition were aggregated by plurality into one final label; repeated calls were not counted as observations | 05-4 §5.4.1–5.4.2; 06 §6.1.1 |
| Model-condition clustering | Each utterance's labels under all conditions were resampled together in an utterance-level paired bootstrap, and Δκ was computed on paired sets | 06 §6.2.1; 02-3 §2.3.7 |
| Item clustering | Utterances from the same transcript were not treated as a cluster, by design: the inferential population is the eligible target population, the sample was drawn at the utterance level, and no transcript-level superpopulation is posited | 02-3 §2.3.7; 06 §6.3 |
| Multilevel models, GEE, cluster-robust standard errors | Not used. Each comparison is a single paired Δκ, and no regression model is fitted | — |
| Number of clusters and intracluster correlation | The analysis unit was the utterance (300 clusters for the bootstrap); a single model was used. Intracluster correlation was not computed, including for utterances sharing a transcript | 02-3; 06 |

### 5.3 Conduct Robustness Analyses

| Item | This study | Where documented |
|---|---|---|
| Technical robustness | Technical robustness was not assessed. The study focused on estimating agreement changes under one fixed configuration, and its results are limited to that configuration. Testing whether these changes hold across other configurations was outside its scope | — |
| Conceptual robustness | Conceptual robustness was not assessed. The study varied instruction content within one coding task and one manual, and its results are limited to that task and manual. Testing whether these changes hold for other coding tasks or manuals was outside its scope | — |

### 5.4 Calibrate Interpretations of Effects

| Item | This study | Where documented |
|---|---|---|
| Low response variability | Repeated calls were aggregated into one label per utterance-condition, and uncertainty was estimated by resampling utterances, so the model's low variability across repeated calls did not add observations. Repeated-call diagnostics were reported per condition as descriptive statistics only | 05-4; 06; 04-2 §4.2.5 |
| Significance with large non-independent samples | No significance tests were used. κ, Δκ, and bootstrap intervals were reported and interpreted together. A small Δκ or an interval containing zero was prespecified not to be read as evidence of no effect or equivalence | 06; 03-1 §3.1.7; 02-3 §2.3.7 |
| Consistency across robustness checks | Robustness checks were not conducted (5.3), so consistency across them could not be assessed. Interpretation is limited to the observed decreases under the tested configuration, without ranking components or claiming mechanisms | main scoring record (claim boundary) |

## Stage 6 Report and Reconceptualize

### 6.1 Ensure Transparent and Accessible Reporting

| Item | This study | Where documented |
|---|---|---|
| Reporting guideline | No reporting guideline (TRIPOD-LLM, MI-CLEAR-LLM) was followed | — |
| Replication package | Data, code, prompts, raw responses, sealed analysis inputs, and execution and scoring records are in a public GitHub repository. No archival deposit (e.g., Zenodo) has been made | Stage 4 (4.3) |
| Model and environment | OpenAI `gpt-5.5-2026-04-23`; querying began on 2026-09-24. The model's training-data cutoff is not recorded | 05-2; main-run record §7 |
| Handling of stochasticity | Three calls per utterance-condition, aggregated by plurality, with up to two additional calls only to break ties; temperature 0, reasoning effort none | 05-4; 05-2 |
| Prompt documentation | The exact text of every prompt as sent, and the rules by which prompts were assembled | `runs/main-2026-09-24/prompts.jsonl`; 05-1 |
| Data contamination | TalkMoves is a public dataset, so prior model exposure to its transcripts or coding manual cannot be excluded for any condition, including the baseline and replacement conditions | 03-3; final report §15 |

### 6.2 Constrain Claims to Evidence

| Item | This study | Where documented |
|---|---|---|
| Frame conclusions within the study's boundaries | Claim boundaries were fixed before data collection, and results are reported for one model snapshot and one setting only | 01 §1.2; final report §15 |
| Avoid anthropomorphic language | The final report contains no affirmative use of verbs such as understand, know, reason, or believe with the model as subject | final report |
| Distinguish observed performance from inferred competence | Agreement is treated as a claim about outputs only; Δκ is not taken as evidence about what the model understands or what human coders relied on | 01 §1.2.2; final report §3 |

### 6.3 Use Findings to Reconceptualize and Refine

The study measured no psychological construct in the model, so construct reconceptualization does not apply. As a methodological pre-study for later human–AI interaction research, its results do not transfer to another coding manual. What transfers is the premise that a manual written for human coders should not be assumed to work equivalently as an LLM prompt without validation (01 §1.2.3; final report §14.4).

### 6.4 Address Limitations and Ethical Implications

Limitations, including generalization across model versions, are discussed in the final report (final report §15).

The study involved no human participants and used a public, licensed dataset. Its findings bear on research practice rather than public policy: they caution against treating LLM coding as a substitute for human coding without validation against human labels. The study did not propose replacing human coders; human labels served as the reference throughout.