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