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
- Status: verified (2026-08; Tag 4 context check added 2026-08-31)
- Method: Inspection of actual sentences against manual
  definitions (scripts/check_tags.py). Tags 3 and 4 additionally
  checked with preceding context (scripts/check_tag_context.py),
  because Restating and Revoicing are defined by relation to the
  preceding student utterance and cannot be verified from the
  teacher utterance alone.
- Result: 0 Not coded (101,357) / 1 Keeping Everyone Together
  (19,704) / 2 Getting Students to Relate (2,556) / 3 Restating
  (2,305) / 4 Revoicing (3,436) / 5 Pressing for Accuracy (19,849)
  / 6 Pressing for Reasoning (1,759). The numeric order does not
  follow the manual's order of presentation: tags 4 and 5 are
  swapped relative to it. Tag 3 is verbatim repetition of the
  immediately preceding student utterance (checked 2026-08).
  Tag 4 is repetition of the preceding student utterance with
  wording added or changed, including corrections (checked
  2026-08-31).
- Known issues:
  (a) Teacher real names remain in transcripts (702 "Ms + name"
  matches). Names are substituted when examples are quoted in
  documents.
  (b) An open, unanswered issue on the corpus repository notes
  missing validation files. The splits available may differ from
  those used in the original dataset paper.
  (c) Speaker–tag mismatch, re-examined 2026-09-08: In the development file, 68 rows are marked as student speech (`Speaker == S`) but contain a value in the teacher `Tag` column: 48 have `Tag = 0` and 20 have `Tag = 1–6`. One additional `Tag = 1–6` case appears in the held-out file. Because the analysis population is defined as `Speaker == T`, these rows are not included in the analysis and no separate exclusion rule is needed. The 20 rows with substantive teacher tags may be speaker-labeling errors, but the original `Speaker` values are retained and no rows are reassigned.

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