## 6. Analysis

[decided 2026-09-19] The analysis rules below were adopted before main-experiment results. They retain the sampling and estimand decisions in [2.3](02-3-sampling-design.md), the replacement and negative-control roles in [3.1.7](03-1-manual-component-definition.md), and the names-only role in [3.3](03-3-names-only-diagnostic.md). They do not promote the proposed repetition or execution specifications to decided status.

### 6.1 Estimation of condition-specific κ

#### 6.1.1 Input and scoring unit

Use the final labels constructed under [5.4](05-4-repetition-and-label-aggregation.md), with the final parsing and run-completion requirements of [5.6.8](05-6-execution-order-and-run-records.md). Analysis uses `final_labels.csv` only after the last required pass has terminated and the parser has been rerun. Check coverage against the original sample and condition list; an absent row or `tie_pending` is an incomplete execution/record state, not a terminal missing label to exclude silently.

Before any statistic is computed, the scorer verifies from the attempt records that every call in every pass present in the run directory is terminated (as defined in 5.6, Terms), using `run_experiment.require_pass_terminated`. If any call is unterminated, the scorer stops without computing statistics. This check is needed because `final_labels.csv` alone cannot show an unterminated call: a (condition, utterance) pair whose remaining repeats are still open can already appear as `resolved` or `insufficient_valid_repeats`. The scorer also re-derives the final labels from the attempts files with the `parse_attempts.py` functions and stops if they differ from `final_labels.csv` on disk, so that a file left over from an earlier, partial parse (5.6.8) is not analysed.

Revision note (2026-09-21): A document–code comparison on 2026-09-21 found that the incomplete states named in this section (an absent row or `tie_pending`) do not cover calls that are still open, and that nothing prevents analysis of a `final_labels.csv` that was not regenerated after the last pass (5.6.8). The termination check and the stale-file check were added. No other rule in this section was changed.

Join the human label and all six condition records by utterance identity, preserving the original 300 sampled utterances and each condition's status. Do not change `final_labels.csv` semantics: it remains one row per utterance-condition. Repeated calls construct a label; they are not additional sampled observations. Category mapping is exactly `scripts/tags.py`, including `Not coded` as a substantive category.

For each condition, report ordinary unweighted Cohen's κ against human labels on the utterances with a resolved final label in that condition, together with that analysis n. With contingency-table proportions, κ = (P_o − P_e) / (1 − P_e), where P_o is observed agreement and P_e is the sum of products of human and predicted marginal proportions across the seven canonical categories. Numeric tag values do not define distances or weights.

#### 6.1.2 Comparison-specific missing-label handling

For each of the three substantive replacements and the negative control, define its paired set as the utterances with resolved final labels in both baseline and that condition. Recompute both κ values on that same set; Δκ = κ_replacement − κ_baseline. Distinguish this paired-set baseline κ from the standalone baseline κ in 6.1.1. Names-only has its own descriptive κ and uncertainty interval under 3.3, not a baseline-referenced inferential contrast.

Do not impute missing final labels or convert them to `Not coded`. Do not require complete labels across all six conditions: a failure in another condition, including names-only, does not remove an otherwise eligible pair from a comparison.

For each comparison, report the original sample n, actual paired n, counts with both labels, baseline only, replacement only, and neither, and the terminal missing-status counts (`unresolved_tie`, `insufficient_valid_repeats`) for each side. Report the actual number of condition-discordant final labels on the paired set. Retain all missing records in the completeness report.

When missing labels remain, the intended complete 300-item primary analysis is incomplete. The prespecified paired complete-case result preserves pairing but does not recover the original finite-population estimand without additional missingness assumptions. Report it as the agreement difference on the observed paired set, with that limitation; do not silently redefine the population in 2.3.1. Different comparison-specific paired sets do not authorize a new contrast between Δκ estimates.

### 6.2 Estimation and uncertainty of Δκ

#### 6.2.1 Bootstrap specification

Use paired utterance-level bootstrap with two-sided 95% pointwise percentile intervals (2.5th and 97.5th percentiles), 10,000 replicates, and bootstrap seed 20260919. These are individual-statistic intervals, not simultaneous coverage across the three substantive contrasts.

Each replicate draws 300 utterance indices with replacement from the complete original 300-record table. Carry the human label, all condition final labels, and all missingness states together, including repeated occurrences of a sampled index. Use the same draw for every condition. Within each replicate, apply 6.1.1 for standalone κ and 6.1.2 for each paired κ/Δκ; paired n can vary across replicates. Do not independently resample conditions, prefilter the shared table to six-condition complete cases, or bootstrap calls as independent observations.

Reproducibility of the draws. The replicate indices are generated once per scorer run, before any statistic is computed, as a 10,000 × n integer array `numpy.random.Generator(numpy.random.PCG64(20260919)).integers(0, n, size=(10000, n))`, where n is the number of records in the original table (300 in the main run). Row r is replicate r, and every condition and every statistic (standalone κ, paired κ, Δκ) uses the same array. The table rows are ordered by `utterance_id` ascending, and a drawn index i (0-based) refers to the i-th row of that table, so the row order is part of the reproducibility conditions. Percentiles are computed with `numpy.percentile(values, [2.5, 97.5], method="linear")`. The bit generator is named explicitly rather than taken from `default_rng`, whose default may change. NumPy still does not guarantee that `Generator.integers` yields the same values across NumPy versions, so the seed reproduces the intervals only together with the NumPy version: the scorer records `numpy.__version__` in its report header, and the version is fixed in 5.2.3.

Revision note (2026-09-21): The generator, the order in which the draws are produced, the percentile method and the NumPy version record were not specified in this section. They were added before any scorer code for the bootstrap was written and before any data were collected. No other rule in this section was changed.

Revision note (2026-09-21, row order): The order of the table rows that the drawn indices refer to was not specified. It was added after `make_table` fixed that order in the point-estimate code (commit `4e61b58`) and before any bootstrap code was written. No other rule in this section was changed.

Revision note (2026-09-21, bit generator): `default_rng(20260919)` was replaced by an explicit `Generator(PCG64(20260919))` so that the specification does not depend on NumPy's current default. Under NumPy 2.3.5 the two produce the same stream. No bootstrap code had been written.

#### 6.2.2 Undefined statistics

κ is undefined when the analysis set is empty or P_e = 1. If an original-set κ is undefined, report that κ and any Δκ depending on it as `not estimable`; retain available descriptive information (n, raw agreement, marginals, confusion matrix). For an empty set, raw agreement is also not estimable. Do not replace undefined values with zero.

Evaluate the prespecified 10,000 replicates and record undefined values separately for each relevant κ and Δκ. A Δκ replicate is undefined if either of its paired-set κ values is undefined. Do not silently drop, replace, or redraw undefined replicates to obtain 10,000 defined values. Report each statistic's undefined count and proportion out of 10,000.

For this study, withhold the affected statistic's percentile CI if at least one replicate is undefined; also withhold a CI for an original-set statistic that is not estimable. Do not suppress CIs for unaffected statistics. This is a prespecified conservative reporting policy, not a claim of uniquely optimal statistical coverage.

#### 6.2.3 Defined but degenerate intervals

Distinguish an undefined statistic from a defined but degenerate interval, such as [0, 0]. Where 6.2.2 permits an interval, report a degenerate interval with its diagnostic context, including paired n and the actual condition-discordant count. Do not infer zero discordant labels from degeneracy alone. Apply the no-equivalence and limited-resolution interpretation in 2.3.7 and 3.1.7; if no discordant labels were observed, state the actual paired n rather than automatically saying 300.

### 6.3 Non-independence and uncertainty interpretation

Retain paired utterance-level resampling and the decision against transcript cluster resampling in 2.3.7. The target remains the fixed eligible finite population, not a transcript superpopulation.

The bootstrap approximates sampling uncertainty for κ and Δκ from the observed utterance/final-label records under the stipulated sampling and execution assumptions. Those records include realized stochastic outputs, but this procedure does not separately estimate variability from rerunning the API on the same 300 utterances. It is not evidence that the same final labels or Δκ would reproduce under a complete rerun.

### 6.4 Robustness checks and alternatives

High-repeat auxiliary study: considered but not adopted for this study. It addresses an additional measurement/reliability question and is not required for the current agreement-change research question. Its omission does not establish the stability of the proposed R = 3 procedure.

Single-repeat sensitivity analysis: optional and unresolved, not adopted by this specification. No repeat-specific κ/Δκ analysis is silently added. Any later adoption must be explicit and respect the existing prohibition on new primary/auxiliary inferential contrasts. No new sensitivity method is specified here.

### 6.5 Descriptive reporting and condition roles

Retain [4.2](04-2-repeated-call-reliability.md), including its descriptive-only boundary and the additions in 4.2.5. Report raw agreement, human/predicted marginal label distributions, and descriptive confusion matrices on the corresponding analysis sets, identifying their n. These diagnostics create no new inferential contrast or rare-category inference (2.3.6).

Retain three substantive baseline-referenced Δκ estimates, condition-specific κ and uncertainty; negative-control contextual κ/Δκ and uncertainty with all 3.1.7 boundaries; and names-only descriptive κ and uncertainty with all 3.3 boundaries. Do not subtract the control, use it as a pass/fail threshold, or create a names-only contrast.

### 6.6 Scorer validation specification

The following are synthetic, hand-checkable examples, not research observations. The point-estimate checks below are implemented in `tests/test_scorer_kappa.py` and passed on 2026-09-21 (commit `bdfac6a`). The CI-policy fixtures in the last paragraph of this section are not implemented yet; they belong to the bootstrap checks.

Revision note (2026-09-21): The previous text stated that scorer implementation and execution of these checks remained pending. The expected values in this section were not changed.

First verify all canonical mappings against `scripts/tags.py`: 0 = Not coded; 1 = Keeping Everyone Together; 2 = Getting Students to Relate; 3 = Restating; 4 = Revoicing; 5 = Pressing for Accuracy; 6 = Pressing for Reasoning. In the examples, A = Not coded (0), B = Keeping Everyone Together (1); all unused categories have zero counts. A dash represents an empty final label with the stated status, never category A.

| Synthetic item | Human | Baseline | Replacement | Missing status |
| --- | --- | --- | --- | --- |
| 1 | A | A | A | none |
| 2 | A | B | A | none |
| 3 | B | B | A | none |
| 4 | B | A | B | none |
| 5 | A | A | — | replacement: unresolved_tie |
| 6 | B | — | B | baseline: insufficient_valid_repeats |

Expected paired set: items 1–4; paired n = 4; both = 4, baseline only = 1, replacement only = 1, neither = 0. With human categories as rows (A, B) and predicted categories as columns (A, B), baseline counts are [[1, 1], [1, 1]] and replacement counts are [[2, 0], [1, 1]]. Thus baseline P_o = P_e = 1/2 and κ = 0; replacement P_o = 3/4, P_e = 1/2 and κ = 1/2; Δκ = +1/2. Actual condition-discordant count = 3.

Standalone baseline uses items 1–5: P_o = 3/5, P_e = 13/25, κ = 1/6. This is not the baseline κ used in the paired contrast. Standalone replacement uses items 1–4 and 6: P_o = 4/5, P_e = 12/25, κ = 8/13. Mark names-only missing for item 1: the paired set and Δκ above must remain unchanged. Items 5 and 6 must not enter the pair through `Not coded` imputation.

Undefined case: human [A, A], baseline [A, A], replacement [B, B]. Baseline P_o = P_e = 1, so baseline κ and Δκ are not estimable; replacement κ = 0 remains defined. An empty paired set is also not estimable. These cases must retain their descriptive information and must not return an artificial zero Δκ.

Identical-label case: human, baseline and replacement all [A, A, B, B]. Both κ values equal 1 and Δκ = 0, with zero discordant labels. This checks the point estimate, not a guarantee of a reportable bootstrap CI: an all-A or all-B resample has undefined κ and follows 6.2.2.

For the future CI-policy check, a synthetic replicate-result fixture with one undefined value among 10,000 must yield undefined count 1, proportion 0.0001, and no CI for that statistic; an unaffected statistic with 10,000 defined values retains its CI. A fully defined all-zero Δκ fixture has interval [0, 0], not an undefined status. These fixtures test reporting rules without API calls or claims about actual bootstrap results.
