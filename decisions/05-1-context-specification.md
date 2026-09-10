## 5.1 Context specification

[proposed 2026-09-10]

### 5.1.1 Context window

Each target utterance is presented with the seven preceding and seven subsequent utterances. Context size is counted in utterance rows (i.e., dataset rows), not conversational turns. Utterances from both students and teachers count toward the window.

Basis: in the original study using this dataset, a window of seven preceding and seven subsequent utterances produced the highest F1 score among the tested context windows (78.92; Suresh et al., 2022, Table 2), with performance declining from a window size of eight onward. The window-size definition in that study counts utterances regardless of speaker, and its preprocessing (30-token truncation per utterance, mean length about 7 tokens) confirms that the unit is the utterance row, not the turn. Human coders read full transcripts, so any fixed window is a partial reproduction of the human coding condition; within that limit, the empirically best-performing window from the original study is used.

### 5.1.2 Boundary handling

[proposed 2026-09-10] Near the beginning or end of a transcript, fewer than seven utterances may exist on one side. Only the available utterances are included; no empty-string padding is used. The original study prepended empty strings, but that choice served the fixed-input-shape requirement of an encoder model. An LLM prompt has no such requirement, and explicitly inserting empty utterances would show the model an artifact absent from the original situation. As a consequence, utterances near transcript boundaries receive less context than others; this is recorded here. This item moves to [decided] after prompt generation is checked during tool validation.

### 5.1.3 Difference from the original study

Utterances are included in full. The 30-token truncation in the original study served transformer input-length limits that do not apply here.

### 5.1.4 Prompt architecture

Each call's prompt consists of, in order: the task instruction; the manual (the baseline or one of the replacement versions, including the negative control, depending on condition; omitted in the names-only diagnostic); the context window with the target utterance marked; and the output instruction.

### 5.1.5 Output instruction

The model answers with a category name, not a tag number. The prompt does not expose the tag-number system; tag numbers are used only in parsing and scoring. The seven category-name strings are identical to the label set in `scripts/tags.py` (3.3, decided 2026-09-10). Variants appearing in the manual text are preserved as written, so canonical label strings and manual-internal wording variants may coexist in the prompt. The frequency of model answers outside the canonical label set is a pilot check item.

### 5.1.6 Unresolved wording

[unresolved] The exact wording of the task instruction and the output instruction, and the marking format for the target utterance within the context window, are fixed during tool validation.