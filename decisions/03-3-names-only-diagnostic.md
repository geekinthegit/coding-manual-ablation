### 3.3 Names-only diagnostic

[proposed 2026-09-09]

- Purpose: A names-only diagnostic is used to estimate how much human–LLM agreement can be obtained when the model is given only the category names, without the substantive coding-manual information used in the main experiment.

- Procedure: The diagnostic is run on the same utterances used in the main experiment. Model, version, API parameters, context specification, call unit, repetition procedure, and label aggregation follow the specifications defined in Section 5 so that the diagnostic and experimental conditions are evaluated under the same computational environment.

- [unresolved] Label strings: The exact category-name strings used in the names-only prompt remain to be determined, including which positional or wording variants of the move names will be used (see note d in Section 3.1.3).

- Interpretation:
  - If a placeholder-replacement condition produces agreement close to the names-only diagnostic, category-label meaning remains a plausible explanation for the residual agreement.
  - If a placeholder-replacement condition produces agreement clearly above the names-only diagnostic, the observed agreement cannot be explained by category labels alone.
  - The names-only value serves as a reference point for interpreting the full-manual and placeholder-replacement conditions. It is not treated as an experimental condition and is not included in the primary Δκ comparisons.

- Boundary: High agreement in the names-only diagnostic does not establish why the model can reproduce the human label pattern. In particular, the model may already have encountered TalkMoves, its coding manual, related instructional materials, or similar category distinctions during training. Therefore, names-only performance cannot distinguish prior model knowledge from other sources of task-relevant information.

- Reporting rule: The names-only result will be described as agreement obtained under a prompt that provides only the category names, not as agreement obtained when the model used only the category names.