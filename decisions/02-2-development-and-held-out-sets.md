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
  - Structure check (2026-09-15): `scripts/check_population_counts.py --file heldout` was run on `test_data_63.xlsx` with the same read rule as the development file (`keep_default_na=False`; only the string `nan` treated as missing). Results: 30,401 rows in total; 23,250 teacher rows (`Speaker == "T"`); tag counts Not coded 15,648, Keeping Everyone Together 3,072, Getting Students to Relate 306, Restating 306, Revoicing 562, Pressing for Accuracy 3,076, Pressing for Reasoning 280, summing to 23,250; all 63 transcripts contain teacher rows; no missing or duplicate source IDs and no missing or unmapped labels. The three source-file characteristics documented for the development file in 2.1.3 are also present here: the provider ID is increasing but not contiguous (9 absent values; first gap at row position 4946); absent text is stored as the literal string `nan`; and 42 teacher rows (Not coded 30, Restating 11, Keeping Everyone Together 1) and 157 student rows have no utterance text. No genuine "None" utterance occurs in this file. Four `Speaker == "S"` rows carry a teacher `Tag` value (three with Tag 0, one with Tag 3); the Tag 3 row is the single held-out `Tag = 1–6` case recorded in 2.1.3 (c), and the three Tag 0 rows were not previously recorded. Under the target eligibility rule in 2.1.2, the held-out eligible target population would be 23,208 teacher utterances (Restating 295 of 306). This is a structural check only; no model calls or agreement calculations were made. Output retained in `reports/heldout-structure-check-2026-09-15.txt`.

### 2.2.3 Permitted use of each set
- Status: settled (2026-08-29)
- Development set: The main experiment runs here. The pilot
  sample is also drawn from here.
- Held-out evaluation set: Used once, for final evaluation,
  applying the rules developed on the development set without
  modification. Not touched before that point.
- Boundary: The pilot is a separate stage and is not the
  development run.

Revision note (2026-09-24): Held-out evaluation, planned in 2.2.3 above as a single final evaluation, was omitted by a post-freeze decision recorded after main-run data collection and before any main-study agreement result was computed or examined. See `reports/heldout-evaluation-decision-2026-09-24.md` and the section "Post-freeze deviation: held-out evaluation omitted" of `reports/protocol-freeze-record-2026-09-24.md`. The text of 2.2.3 above is unchanged.

### 2.2.4 Prior model exposure and direction of bias
- Status: added 2026-10-10, after main-study scoring (post-scoring
  documentation addition; no protocol change). This section was
  written after the results in
  `reports/main-scoring-record-2026-09-24.md` had been computed and
  examined. It restates boundaries fixed before scoring in 3.3
  (Boundary) and reported in that record (Section 12) and in
  `reports/final-research-report-2026-09-25.md` (Sections 13 and 15);
  it adds no new claim, analysis, or protocol change. The text of
  2.2.1–2.2.3 and the Revision note above is unchanged.
- Exposure: TalkMoves is a public dataset, so prior model exposure
  to its transcripts or coding manual cannot be excluded for any
  condition, including the baseline and replacement conditions
  (3.3, Boundary; final report, Section 15).
- Effect on κ: If such exposure occurred, it acted in common on all
  six conditions, which use the same model (5.2) and the same 300
  sampled utterances (2.3.2). It may therefore affect the absolute
  level of the condition-specific κ values.
- Direction: The direction in which such exposure would move Δκ
  depends on the content and extent of the exposure, which the
  design of this study cannot determine. This study therefore
  assumes no direction of bias.
- Consequence for claims: This study makes no claim about the
  absolute level of κ and no generalization to other datasets or
  coding manuals. Its claims are limited to comparisons between
  conditions evaluated on the same 300 sampled utterances, with
  the scope of inference stated in 2.3.1, and within the claim
  boundaries of the scoring record (Section 12) and the final
  report (Sections 13 and 15).
- Record: This section is the record corresponding to the item
  planned as "7.2 Direction of development-set bias" in the
  `DECISIONS.md` outline of 2026-08-31, which was not written
  before scoring.
