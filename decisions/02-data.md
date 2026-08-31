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
- Exclusion criteria: Student utterances. Rows with a speaker–tag
  mismatch (about 48), to be inspected and excluded before
  sampling. Pending.
- Rationale: Student utterances come from multiple unidentified
  speakers and make up roughly one third of the corpus; teacher
  utterances are attributable to a single speaker per transcript.

### 2.1.3 Tag mapping verification
- Status: verified (2026-08)
- Method: Inspection of actual sentences against manual
  definitions (scripts/check_tags.py). Tag 3 additionally checked
  through context inspection (scripts/check_tag3_context.py).
- Result: 0 Not coded (101,357) / 1 Keeping Everyone Together
  (19,704) / 2 Getting Students to Relate (2,556) / 3 Restating
  (2,305) / 4 Revoicing (3,436) / 5 Pressing for Accuracy (19,849)
  / 6 Pressing for Reasoning (1,759). The numeric order does not
  follow the manual's order of presentation: tags 4 and 5 are
  swapped relative to it. Tag 3 is verbatim repetition of the
  immediately preceding student utterance.
- Known issues:
  (a) Teacher real names remain in transcripts (702 "Ms + name"
  matches). Names are substituted when examples are quoted in
  documents.
  (b) An open, unanswered issue on the corpus repository notes
  missing validation files. The splits available may differ from
  those used in the original dataset paper.

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