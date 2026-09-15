## 2.1 Dataset selection and scope

### 2.1.1 Dataset selection
- Status: settled (2026-08-24)
- Decision: The TalkMoves corpus (SumnerLab/TalkMoves, GitHub;
  CC BY-NC-SA 4.0) is the dataset.
- Rationale: It provides both a coding manual written for human
  coders and labels produced by human coders using that manual,
  which is the pairing this study requires.

### 2.1.2 Analysis population
- Status: settled (2026-08-24); target eligibility rule added 2026-09-15
- Decision: Analysis is restricted to teacher utterances
  (150,918 rows out of 203,601 in the development file).
- Inclusion criteria: Utterances attributed to the teacher.
- Exclusion criteria: Student utterances. No further exclusion is needed:
  the speaker–tag mismatch item recorded in August is closed by the
  population definition (see Known issues (c), resolved 2026-09-08).
- Target eligibility rule [decided 2026-09-15; proposed 2026-09-15]: A teacher row whose `Sentence` is missing in the source file is ineligible as a target utterance for sampling. 274 rows are affected (see 2.1.3 (d)). These rows are retained in `data/frame.csv` and in the row order used for context windows; only sampling is restricted, via the `eligible` flag written by `scripts/build_frame.py` and verified by `scripts/check_frame_outputs.py`. Rationale: the coding task presents an utterance to be coded; where no utterance text exists, there is no model input and therefore no human–LLM comparison unit for that row. Retaining such rows would introduce a different task (inferring an absent utterance from context). Expected model behaviour and the effect on κ were not used as grounds. The statement above that no further exclusion is needed concerned resolving count discrepancies by ad hoc removal; the absence of target text is a task-feasibility condition and falls outside that statement. Eligible target population: 150,644 (Not coded 101,201; Keeping Everyone Together 19,704; Getting Students to Relate 2,556; Restating 2,145; Revoicing 3,431; Pressing for Accuracy 19,848; Pressing for Reasoning 1,759). Reporting item: the rule removes 160 of 2,305 Restating rows (6.9%); all other categories change by less than 0.2%. Build summary: `reports/frame-summary-2026-09-15.txt`.
- Rationale: Student utterances come from multiple unidentified
  speakers and make up roughly one third of the corpus; teacher
  utterances are attributable to a single speaker per transcript.

### 2.1.3 Tag Mapping Verification

* Status: verified (2026-08; Tag 4 context check added 2026-08-31; category counts re-verified 2026-09-11; sampling-frame and label integrity re-verified 2026-09-14; missing-text source cells inspected 2026-09-15)

* Method: Tag mappings were checked by inspecting actual utterances against the coding-manual definitions using `scripts/check_tags.py`. Tags 3 and 4 were additionally examined together with the immediately preceding student utterance using `scripts/check_tag_context.py`, because Restating and Revoicing are defined by their relation to prior student speech and cannot be verified reliably from the teacher utterance alone.

* Verified mapping and counts:
  0 = Not coded (101,309)
  1 = Keeping Everyone Together (19,704)
  2 = Getting Students to Relate (2,556)
  3 = Restating (2,305)
  4 = Revoicing (3,436)
  5 = Pressing for Accuracy (19,849)
  6 = Pressing for Reasoning (1,759)

  The numeric tag order does not exactly follow the order in which the categories are presented in the manual: Tags 4 and 5 are reversed relative to that presentation order. Tag 3 was verified as verbatim repetition of the immediately preceding student utterance. Tag 4 was verified as repetition of the preceding student utterance with wording added, changed, or corrected.

* Category-count reconciliation: On 2026-09-11, all category counts were recomputed using a single `Speaker == "T"` mask. This showed that the previously recorded Tag 0 count of 101,357 had inadvertently included 48 rows marked as student speech. After correction, the Tag 0 count is 101,309. The seven verified category counts sum to the prespecified development-set teacher-utterance population of 150,918.

* Reproducibility check (2026-09-14): `scripts/check_population_counts.py` recomputed the Speaker == "T" population size and all seven category counts from the development file and confirmed exact agreement with the recorded values: 150,918 teacher utterances in total and the seven category counts reported above. The source-ID field contained no missing or duplicate values and was monotonically increasing. All 150,918 teacher rows had non-missing labels that mapped successfully through TAG_TO_CATEGORY, with no unmapped tag values, and the seven numeric tags mapped to seven unique coding categories.

  The development file contains 503 transcripts in total, of which 502 contain at least one row satisfying the prespecified teacher mask. The remaining transcript, `Video Mosaic Grade 4 Building large models 3.xlsx`, contains no teacher rows and therefore contributes no utterances to the teacher-utterance analysis population. This is a consequence of the existing `Speaker == "T"` population definition and does not constitute an additional exclusion rule.

  The verification output is retained in `reports/sampling-frame-and-label-check-2026-09-14.txt`.

* Canonical row order and source identifiers (2026-09-14): The provider-assigned ID field (`Unnamed: 0`) is increasing and has no duplicates, but it is not contiguous. In the current development file, 49 values are absent (203,601 rows; maximum ID 203,649), and the first gap occurs at row position 2286. Because the +/-7 context window is defined over adjacent rows of the file as read, the 0-based row position of the raw DataFrame is used as the canonical row order and is carried as `source_id`; the provider ID is retained as `source_row_id` for traceability only and is not used to define adjacency. Both identifiers are written to the derived files `data/frame.csv` (API-input fields only) and `data/scoring_labels.csv` (gold labels), produced by `scripts/build_frame.py` and checked by `scripts/check_frame_outputs.py`. These derived files are git-ignored; the build summary is retained in `reports/frame-summary-2026-09-14.txt`.

* Known issues:

  * (a) Teacher real names remain in the transcripts, including 702 matches of the form “Ms + name.” Names are substituted when examples are quoted in study documents.
  * (b) An open, unanswered issue in the corpus repository reports missing validation files. The development and held-out splits currently available may therefore differ from those used in the original dataset paper.
  * (c) Speaker–tag mismatch, re-examined 2026-09-08 and reconciled on 2026-09-11: in the development file, 68 rows are marked as student speech (`Speaker == "S"`) but contain a value in the teacher `Tag` column. Of these, 48 have `Tag = 0` and 20 have `Tag = 1–6`. In the held-out file, four such rows occur: three with `Tag = 0` and one with `Tag = 3` (the single held-out `Tag = 1–6` case recorded earlier; all four confirmed by the structure check of 2026-09-15, see 2.2.2). Because the analysis population is defined by `Speaker == "T"`, these rows are not included in the analysis and no separate exclusion rule is applied. The 20 development-set rows with substantive teacher tags may reflect speaker-labeling errors, but the original `Speaker` values are retained and no rows are reassigned.
  * (d) Missing utterance text, identified 2026-09-14: the provider file stores absent text as the literal string `nan` in the `Sentence` column. 1,019 rows are affected (274 teacher rows, 745 student rows); these rows carry labels but no text. Among the 274 teacher rows, 160 are coded Restating (6.9% of all Restating rows), 108 Not coded, 5 Revoicing, and 1 Pressing for Accuracy. Direct inspection of the source cells with openpyxl (2026-09-15) confirmed that the cells contain the literal string `nan`; the text is absent in the source file and was not lost in reading. In the inspected cases the missing teacher row is the first row of its turn, the immediately preceding student row is also missing text, and the following rows of the same teacher turn contain text. No inference is drawn from this about the materials used by the human coders. Separately, pandas' default missing-value list treats the string `None` as missing; in the first build on 2026-09-14 this erased 12 genuine utterances (6 teacher, 6 student) in which "None" is the answer to a how-many or what-questions prompt. `scripts/build_frame.py` and `scripts/check_frame_outputs.py` therefore read with `keep_default_na=False` and treat only `nan` as missing in `Sentence`, `Tag`, and `StudentTag`; the regenerated `data/frame.csv` retains the 12 utterances and leaves 274 teacher rows with empty text. The handling of these 274 rows is set by the target eligibility rule in 2.1.2 [decided 2026-09-15].