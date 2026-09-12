### 3.3 Names-only reference

[decided 2026-09-11; originally proposed 2026-09-10]

- Purpose: The names-only reference reports human–LLM agreement when the category names are provided without substantive coding-manual text. It is a supplementary descriptive reference and is excluded from the primary baseline-referenced Δκ comparisons.

- Procedure: It is evaluated on the same sampled utterances and under the same model, API, repetition, aggregation, and output-handling specifications as the experimental conditions. No filler is added to match token count, information position, category-name repetition, or prompt structure.

- Label strings: The six move names use the manual's Section 1.2 forms, with "Not coded" as the seventh canonical output label.

- Reporting and interpretation: Report the unweighted Cohen's κ and its uncertainty interval for the names-only prompt. No inferential contrast with the experimental conditions is made. Differences in κ are not interpreted as identifying the contribution of category-name semantics or which information the model used. No "close to names-only" or "clearly above names-only" rules are used.

- Boundary: The reference is not a chance baseline or a lower bound. Prior model exposure to TalkMoves or related material remains possible. Report it as "agreement obtained under the names-only reference prompt, with no substantive manual text supplied in the request," not as agreement produced using only category names.