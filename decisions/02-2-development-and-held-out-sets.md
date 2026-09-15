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