# 2. Data

## 2.1 Dataset selection and scope

### 2.1.1 Dataset selection
- Status: settled (2026-08-24)
- Decision: The TalkMoves corpus (SumnerLab/TalkMoves, GitHub;
  CC BY-NC-SA 4.0) is the dataset.
- Rationale: It provides both a coding manual written for human
  coders and labels produced by human coders using that manual,
  which is the pairing this study requires.

### 2.1.2 Analysis population
- Status: settled (2026-08-24); one exclusion item pending
- Decision: Analysis is restricted to teacher utterances
  (150,918 rows out of 203,601 in the development file).
- Inclusion criteria: Utterances attributed to the teacher.
- Exclusion criteria: Student utterances. No further exclusion is needed:
  the speaker–tag mismatch item recorded in August is closed by the
  population definition (see Known issues (c), resolved 2026-09-08).
- Rationale: Student utterances come from multiple unidentified
  speakers and make up roughly one third of the corpus; teacher
  utterances are attributable to a single speaker per transcript.

### 2.1.3 Tag mapping verification

- Status: verified (2026-08; Tag 4 context check added 2026-08-31; category counts re-verified 2026-09-11)
- Method: Inspection of actual sentences against manual definitions (scripts/check_tags.py). Tags 3 and 4 additionally checked with preceding context (scripts/check_tag_context.py), because Restating and Revoicing are defined by relation to the preceding student utterance and cannot be verified from the teacher utterance alone.
- Result: 0 Not coded (101,309) / 1 Keeping Everyone Together (19,704) / 2 Getting Students to Relate (2,556) / 3 Restating (2,305) / 4 Revoicing (3,436) / 5 Pressing for Accuracy (19,849) / 6 Pressing for Reasoning (1,759). The numeric order does not follow the manual's order of presentation: tags 4 and 5 are swapped relative to it. Tag 3 is verbatim repetition of the immediately preceding student utterance (checked 2026-08). Tag 4 is repetition of the preceding student utterance with wording added or changed, including corrections (checked 2026-08-31). Category counts were re-computed under a single `Speaker == T` mask on 2026-09-11; the previous Tag 0 count of 101,357 included 48 student rows and was corrected to 101,309. The seven category counts now sum to the verified analysis population of 150,918.
- Known issues: (a) Teacher real names remain in transcripts (702 "Ms + name" matches). Names are substituted when examples are quoted in documents. (b) An open, unanswered issue on the corpus repository notes missing validation files. The splits available may differ from those used in the original dataset paper. (c) Speaker–tag mismatch, re-examined 2026-09-08 and count reconciliation completed 2026-09-11: In the development file, 68 rows are marked as student speech (`Speaker == S`) but contain a value in the teacher `Tag` column: 48 have `Tag = 0` and 20 have `Tag = 1–6`. One additional `Tag = 1–6` case appears in the held-out file. Because the analysis population is defined as `Speaker == T`, these rows are not included in the analysis and no separate exclusion rule is needed. On 2026-09-11, category counts were recomputed using a single `Speaker == T` mask, confirming that the previous Tag 0 count had inadvertently included the 48 `Speaker == S, Tag == 0` rows. The 20 rows with substantive teacher tags may be speaker-labeling errors, but the original `Speaker` values are retained and no rows are reassigned.



## 2.2 Development and held-out evaluation sets

### 2.2.1 Purpose of the split
- Status: settled (2026-08-24)
- Decision: Two-step validation: develop on one set, then evaluate
  on data not used in development.
- Rationale: Follows the two-step validation structure of the
  validity workflow.

### 2.2.2 Split as provided by the corpus
- Status: settled (2026-08-24)
- Decision: The corpus's own split is used as provided:
  train_data_504.xlsx (503 transcripts) as the development set,
  test_data_63.xlsx (63 transcripts) as the held-out evaluation
  set. The split is at transcript level by construction.
- Rationale: Using the corpus-provided split avoids introducing a
  split decision of this study's own.
- Known issue: See 2.1.3 (b); the provided split may differ from
  the original paper's.

### 2.2.3 Permitted use of each set
- Status: settled (2026-08-29)
- Development set: The main experiment runs here. The pilot
  sample is also drawn from here.
- Held-out evaluation set: Used once, for final evaluation,
  applying the rules developed on the development set without
  modification. Not touched before that point.
- Boundary: The pilot is a separate stage and is not the
  development run.

  
## 2.3 Sampling design

[decided 2026-09-10]

### 2.3.1 Target Population and Primary Estimand

The inferential population is the prespecified development-set teacher-utterance population of 150,918 utterances. The primary estimand is the change in overall human–LLM agreement, measured by Cohen’s κ, when a specified coding-manual component is replaced with a placeholder. Agreement is therefore defined with respect to the natural category distribution of this population rather than to an artificially balanced evaluation distribution.

### 2.3.2 Sampling Design and Agreement Metric

The main experimental sample will consist of 300 utterances selected by simple random sampling without replacement from the analysis population. The same 300 utterances will be used in the baseline, all replacement conditions, and the names-only condition. The random seed and sampling script will be retained in the repository. Because the coding categories are nominal, agreement will be measured using ordinary (unweighted) Cohen’s κ; subsequent references to κ in the analysis will use “unweighted Cohen’s κ” to distinguish it from design weighting or ordinal weighted κ.

### 2.3.3 Alternative Considered: Disproportionate Stratification Without Population Weighting

Disproportionate stratified sampling without population weighting was considered and rejected. Such a design would increase representation of rare human-coded categories and therefore provide more opportunities to observe category-specific changes. However, Cohen’s κ depends on the marginal category distributions. If rare categories are deliberately oversampled and the resulting sample is analyzed using ordinary unweighted κ, the estimand becomes agreement in the constructed stratified sample rather than agreement in the prespecified TalkMoves teacher-utterance population. Using the same utterances across conditions preserves the paired comparison but does not restore the population distribution on which κ and Δκ are defined. Because the primary claim concerns the overall change in agreement in the prespecified population, rather than category-balanced performance, this alternative was not adopted.

### 2.3.4 Alternative Considered: Disproportionate Stratification With Population Standardization

Disproportionate stratified sampling combined with population standardization was also considered. This design could, in principle, increase rare-category coverage while retaining a population-relevant estimand by reconstructing population-weighted joint classification proportions before computing κ. However, it would require explicit design weights, a population-standardized κ estimator, and an uncertainty procedure that preserves both the paired condition structure and the stratified sampling design. This is a statistically valid alternative rather than an invalid design, but it introduces an additional estimation and validation layer that is not required for the present population-level question. It was therefore not adopted for this study.

### 2.3.5 Sample Size Rationale

The sample size of 300 is a prespecified, resource-constrained evaluation size rather than a statistically optimized quantity. Precision-based planning for Δκ would require credible information about the paired joint classification structure across the baseline and replacement conditions, which was not available before the main evaluation. The resulting sparsity of rare human-coded categories is therefore treated as a design limitation rather than as evidence that those categories are unaffected by the manipulation.

### 2.3.6 Rare-Category Representation and Scope of Inference

Under the verified category counts of the analysis population reported in 02-data, the expected number of Pressing for Reasoning utterances in an SRS of 300 is approximately 3.5, and the probability of obtaining two or fewer is approximately 32%. These quantities will be reproduced in a repository script using the corresponding hypergeometric calculation (`scripts/[filename].py`). Similar sparsity is expected for several other minority categories. Consequently, the study will not make inferential claims about category-specific effects. Category-level results may be reported descriptively through counts and confusion matrices, while the primary inferential analysis remains the overall κ and condition-specific Δκ.

### 2.3.7 Paired Resampling for Uncertainty Estimation

Uncertainty for Δκ will be estimated using paired utterance-level resampling. Each sampled utterance will be resampled together with its human label and all corresponding LLM outputs across experimental conditions, thereby preserving the within-item pairing. Because the inferential population is the prespecified development-set teacher-utterance population and the sample itself is drawn at the utterance level, transcript-level cluster resampling is not adopted. Transcripts are not the sampling units in the prespecified design, and the study does not posit a transcript-level superpopulation model. This choice is consistent with treating item-level pairing as part of the analysis while keeping the uncertainty procedure aligned with the actual sampling design. If the baseline and a replacement condition produce identical final labels for all 300 sampled utterances, the paired bootstrap distribution of Δκ may be degenerate at zero. This case will be flagged separately. A `[0, 0]` bootstrap interval will not be interpreted as evidence of population-level equality or equivalence. Instead, the result will be described as no condition-discordant labels having been observed among the 300 sampled utterances.

### 2.3.8 Limitation of the Sampling Design

The main limitation of this sampling decision is reduced sensitivity to effects concentrated in rare coding categories. An overall null or small Δκ therefore cannot be interpreted as evidence that every category is unaffected by manual-component replacement. The result supports only the prespecified population-level claim about overall agreement, within the category distribution represented by the TalkMoves development-set teacher-utterance population.