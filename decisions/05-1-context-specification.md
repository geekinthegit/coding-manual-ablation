## 5.1 Context specification

[proposed 2026-09-10]

### 5.1.1 Context window

Each target utterance is presented with the seven preceding and seven subsequent utterances. Context size is counted in utterance rows (i.e., dataset rows), not conversational turns. Utterances from both students and teachers count toward the window.

Basis: in the original study using this dataset, a window of seven preceding and seven subsequent utterances produced the highest F1 score among the tested context windows (78.92; Suresh et al., 2022, Table 2), with performance declining from a window size of eight onward. The window-size definition in that study counts utterances regardless of speaker, and its preprocessing (30-token truncation per utterance, mean length about 7 tokens) confirms that the unit is the utterance row, not the turn. Human coders read full transcripts, so any fixed window is a partial reproduction of the human coding condition; within that limit, the empirically best-performing window from the original study is used. Human coders read each transcript in order and assigned a label to every teacher utterance; the utterance under judgment was therefore given to them, not searched for. This study likewise specifies the target utterance explicitly (5.1.4). What differs from the human condition is the amount of surrounding transcript available (±7 rows rather than the whole transcript), not whether the target is identified. Context rows are taken from the full source row order (teacher and student rows together, position = `source_id`, see `scripts/build_frame.py`), not from the teacher-only frame; the teacher filter applies to target selection only.

### 5.1.2 Boundary handling

[decided 2026-09-23; proposed 2026-09-10] Near the beginning or end of a transcript, fewer than seven utterances may exist on one side. Only the available utterances are included; no empty-string padding is used. The original study prepended empty strings, but that choice served the fixed-input-shape requirement of an encoder model. An LLM prompt has no such requirement, and explicitly inserting empty utterances would show the model an artifact absent from the original situation. As a consequence, utterances near transcript boundaries receive less context than others; this is recorded here. Confirmed during tool validation on source_id 0 (first row of a transcript) and 23541 (empty-text row inside the window); see reports/tool-validation-record-2026-09-23.md §4 and §9.

### 5.1.3 Difference from the original study

Utterances are included in full. The 30-token truncation in the original study served transformer input-length limits that do not apply here.

### 5.1.4 Prompt architecture

Each call's prompt consists of, in order: the task instruction; the manual (the baseline or one of the replacement versions, including the negative control, depending on condition; omitted in the names-only diagnostic); the context window with the target utterance marked; and the output instruction.
The context window and the target row contain only the speaker marker and the utterance text. No human label enters the prompt in any form: not the tag number, not the category name attached to a row, and not any field derived from `Tag` or `StudentTag`. Category names appear only in the output instruction (5.1.5) and, where present, inside the manual text.

Condition identifiers used in code follow 3.1.7 and 3.3: `baseline`, `definition_replacement`, `example_replacement`, `exclusion_rule_replacement`, `negative_control`, `names_only`.

### 5.1.5 Output instruction

The model answers with a category name, not a tag number. The prompt does not expose the tag-number system; tag numbers are used only in parsing and scoring. The seven category-name strings are identical to the label set in `scripts/tags.py` (3.3, decided 2026-09-10). Variants appearing in the manual text are preserved as written, so canonical label strings and manual-internal wording variants may coexist in the prompt. The frequency of model answers outside the canonical label set is a pilot check item.

### 5.1.6 Serialisation, target marking, and instruction wording

[decided 2026-09-23; proposed 2026-09-15] The following four items were previously [unresolved]. They are implemented in `scripts/build_inputs.py` and checked by `scripts/check_inputs.py`. Confirmed during tool validation without change to any of the four items; see reports/tool-validation-record-2026-09-23.md §4 and §9.

(a) Target marker. The target row is prefixed with the string `[TARGET] ` (marker, space), e.g. `[TARGET] T: Okay`. This format was accepted in the technical test of the API request (5.3.9).

(b) Serialisation. Each row is written as `T: <text>` for a teacher row or `S: <text>` for a student row. Rows are separated by a single newline. The block is preceded by one header line, `Context:`. Prompt sections (task instruction, manual, context block, output instruction) are separated by one blank line; the manual section is introduced by the line `Coding manual:`.

(c) Empty text in context rows. A context row whose `Sentence` is missing in the source file is rendered as the speaker marker alone (`S:` or `T:`). The row is not skipped, so the ±7 count of 5.1.1 is unchanged, and no stand-in such as `nan` or `[MISSING]` is inserted. Basis: the source file has no text for that row (2.1.3(d)), and no inference is drawn about the materials used by the human coders, and inserting a marker would show the model an artefact absent from the original situation, the same reasoning as 5.1.2. A target row with missing `Sentence` cannot occur because such rows are ineligible (2.1.2).

(d) Instruction wording, draft. Task instruction:

> You are coding teacher talk in a mathematics classroom transcript. The Context block below shows consecutive lines from one transcript; T: marks the teacher and S: marks a student. Exactly one line is marked [TARGET]. Assign that target line to exactly one of the categories listed in the Output section. Use the other lines only as context and do not code them.

Output instruction:

> Output: respond with a JSON object with a single key "category" whose value is exactly one of the following strings: "Not coded", "Keeping Everyone Together", "Getting Students to Relate", "Restating", "Revoicing", "Pressing for Accuracy", "Pressing for Reasoning". Do not include anything else.

The same seven strings are the enum of the structured-output schema (5.3). The wording was read on assembled prompts during tool validation and kept unchanged.

Implementation record. The context is built from `data/rows_all.csv` (all source rows, no label columns; written by `build_frame.py`) and target candidates from `data/frame.csv`. `check_inputs.py` verifies, for given `source_id`s and all six conditions: no label column in either input file; exactly one `[TARGET]` line, a teacher line, at the expected position; window size equal to min(7, rows available before) + 1 + min(7, rows available after), computed independently; every line carrying a speaker marker; no `Tag`, tag-number pattern, category name, or empty-text stand-in in the task instruction or context block; each category name exactly once in the output instruction; byte-identical context blocks across conditions. Example prompts for `source_id` 0 (transcript start, no rows before), 7 (full window on both sides), and 23541 (window containing a row with missing text) are in `reports/input-examples-2026-09-15.txt`; all checks passed. These three `source_id`s are development targets (5.7.2) and are excluded from main-experiment target selection (2.3, revision of 2026-09-23).

Observation recorded at this step: `rows_all.csv` contains 503 contiguous `Transcript` blocks, equal to the number of distinct `Transcript` values, so the boundary rule of 5.1.2 operates on adjacent rows.

Revision note (2026-09-23): 5.1.2 and 5.1.6 (a)–(d) were moved from [proposed] to [decided] after the prompts generated for tool validation were checked (reports/tool-validation-record-2026-09-23.md §4 and §9). The basis sentence of 5.1.6 (c) was narrowed to what 2.1.3(d) supports, namely that the source file has no text for the row, without an inference about the materials used by the human coders (independent audit, non-blocking item 4.3). No prompt wording was changed.