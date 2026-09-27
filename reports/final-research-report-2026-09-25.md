# Final research report: placeholder replacement of coding-manual components and LLM–human agreement (Roadmap 18-3, first draft)

Drafted 2026-09-25 at repository HEAD `e63cbe07487d125bbbaf510a120a8d8cbe50a744` ("Record post-scoring documentation errata (freeze record 02-3 entry, 02-3 script placeholder) and append freeze record entry", 2026-09-25 18:53:35 +0900). Status: first draft; not independently audited.

Every number describing an agreement result in this report is taken from `reports/main-scoring-record-2026-09-24.md` as displayed there (four decimal places for κ, Δκ and interval bounds; integer counts). Nothing was recomputed and the scorer was not rerun. Every quotation is verbatim from the cited file and line. Line citations refer to the files at the HEAD commit above.

Citation abbreviations. Decision documents under `decisions/`: `01` = `01-research-question.md`; `02-1` = `02-1-dataset-selection-and-scope.md`; `02-2` = `02-2-development-and-held-out-sets.md`; `02-3` = `02-3-sampling-design.md`; `03-1` = `03-1-manual-component-definition.md`; `03-2` = `03-2-placeholder-specification.md`; `03-3` = `03-3-names-only-diagnostic.md`; `04-2` = `04-2-repeated-call-reliability.md`; `05-1` = `05-1-context-specification.md`; `05-2` = `05-2-model-and-api-parameters.md`; `05-3` = `05-3-call-unit-and-api-request.md`; `05-4` = `05-4-repetition-and-label-aggregation.md`; `05-5` = `05-5-role-of-the-pilot.md`; `05-6` = `05-6-execution-order-and-run-records.md`; `05-7` = `05-7-tool-validation.md`; `06` = `06-analysis.md`. Records under `reports/`: `MSR` = `main-scoring-record-2026-09-24.md`; `HED` = `heldout-evaluation-decision-2026-09-24.md`; `PFR` = `protocol-freeze-record-2026-09-24.md`; `MRR` = `main-run-record-2026-09-24.md`; `CR` = `completeness-report-2026-09-24.md`; `IVR` = `input-verification-2026-09-24.md`; `PPR` = `procedural-pilot-record-2026-09-24.md`; `TVR` = `tool-validation-record-2026-09-23.md`; `ERR1` = `documentation-errata-2026-09-24.md`; `ERR2` = `documentation-errata-post-scoring-2026-09-25.md`; `MSM` = `main-sample-manifest-2026-09-24.json`; `TMC` = `token-matching-check-2026-09-24.txt`; `RMS` = `replacement-manifest-summary-2026-09-15.txt`; `BC` = `build-conditions-2026-09-15.txt`. A citation `03-1:137` means line 137 of that file.

## Summary

This summary restates the research question, the design as recorded in the decision documents, and the two prespecified result statements, each with the citation used in the sections below; it adds no statement beyond them.

Research question: "How does replacing specific components of a coding manual with placeholders change an LLM's agreement with human dialogue coding?" (01:5–7). The study evaluated 300 teacher utterances drawn by simple random sampling without replacement from the main-experiment sampling frame, "the eligible target population (2.1.2) minus the development targets D listed in 5.7.2" (02-3:11, :13), under five conditions, namely the baseline (unmodified manual), definition replacement, example replacement, exclusion-rule replacement and the negative control (03-1:102), together with the names-only reference, "a supplementary descriptive reference" that "is excluded from the primary baseline-referenced Δκ comparisons" (03-3:5). All calls used the model snapshot `gpt-5.5-2026-04-23` (05-2:24), three repeated calls per item-condition (05-4:15), and unweighted Cohen's κ against the human labels (02-3:11). The two prespecified result statements are:

- "C1. Under the implemented replacement procedure, agreement with the human labels was lower than the paired-set baseline in the example-replacement and exclusion-rule-replacement conditions: the baseline-referenced Δκ and its 95% interval were both below zero in each. The causal claim is restricted to the effect of the implemented manipulation on agreement." (MSR:339)
- "C2. For definition replacement and the negative control, the 95% interval for Δκ includes zero. No direction or magnitude is claimed, and this is not interpreted as evidence of no effect, maintained agreement, or equivalence between the baseline and replacement conditions. A small or uncertain negative-control Δκ does not establish general filler neutrality." (MSR:341)

The estimates behind these statements are in Section 11; the full set of interpretation boundaries is in Section 13.

## 1. Research question and scope of claims (R-1)

Source: 01:3–96.

### 1.1 Research question

The research question, settled 2026-08-29 (01:4), is: "How does replacing specific components of a coding manual with placeholders change an LLM's agreement with human dialogue coding?" (01:5–7).

The wording is the fourth version. The decision record documents why each earlier version was rejected (01:8–62). The first version, which asked which components "drive agreement", was rejected because "The wording presupposes that each component's contribution can be identified separately." (01:12–13) and because the manual's components "define themselves by reference to one another" (01:14–15). The second version spoke of "removal"; it was superseded because "Placeholder substitution had already been settled as the design on 2026-08-24: token length and position are preserved and only the information content is replaced." (01:28–30). In the current version, "Removing" was replaced by "replacing ... with placeholders", so that the RQ names the operation actually performed (01:57), and "Change" replaced "affect" (01:58), "change" having been "judged at the time to state the manipulation–outcome relation with less causal force" (01:59–60).

### 1.2 Level of causal claim

"The study belongs to the research-tool pathway (functional claims about an LLM's agreement with human coding), and additionally falls under the exception for experiments on the tool itself: it manipulates the prompt (placeholder replacement of manual components) and measures the resulting change in agreement (Δκ). Causal claims are therefore restricted to the effect of the implemented manipulation on agreement." (01:68–73)

Boundary: "No causal claim is made about anything not manipulated. The independent causal effect of a component, or a component's intrinsic importance, is outside the claim." (01:74–76)

Rationale as recorded: "The same utterances are evaluated under every condition, allowing within-item comparison. Placeholder replacement is designed to preserve token length and downstream position, while the remaining prompt architecture is held constant." (01:77)

### 1.3 No mechanism claims

"Agreement is a claim about outputs only. High κ is not taken as evidence that the LLM and human coders share a process, and Δκ is not taken as evidence about what the LLM understands or what human coders relied on." (01:81–84) The rationale is that "The data contain human labels and LLM labels. Neither the human coders' use of the manual nor the LLM's processing of it is observed, so neither can appear as the subject of a result statement." (01:85–88)

### 1.4 Position of the study

"This is a methodological pre-study for a later human–AI interaction study, examining whether LLM-assisted coding can be used there. It is not a pilot of that later study's research question." (01:92–95) Its boundary: "Results on TalkMoves do not generalize to the later study's coding manual. The transferable methodological premise is that a manual developed for human coders should not be assumed, without validation, to function equivalently when used as an LLM prompt." (01:96) TalkMoves was chosen "because it provides both a manual written for human coders and human-coded labels produced with that manual." (01:97–99)

## 2. Data: dataset, eligible target population, split (R-2)

Sources: 02-1 (2.1.1–2.1.3); 02-2; HED.

### 2.1 Dataset

"The TalkMoves corpus (SumnerLab/TalkMoves, GitHub; CC BY-NC-SA 4.0) is the dataset." (02-1:5–6) Rationale: "It provides both a coding manual written for human coders and labels produced by human coders using that manual, which is the pairing this study requires." (02-1:7–9) The corpus is not included in the repository; scripts read a local clone through the `TALKMOVES_DIR` environment variable (README.md:12–25).

### 2.2 Analysis population and eligible target population

"Analysis is restricted to teacher utterances (150,918 rows out of 203,601 in the development file)." (02-1:13–14) Student utterances are excluded because they "come from multiple unidentified speakers and make up roughly one third of the corpus; teacher utterances are attributable to a single speaker per transcript." (02-1:20–22)

Target eligibility rule [decided 2026-09-15]: "A teacher row whose `Sentence` is missing in the source file is ineligible as a target utterance for sampling. 274 rows are affected" (02-1:19). The rows remain in the frame and in the row order used for context windows; only sampling is restricted (02-1:19). The rationale is task feasibility: "the coding task presents an utterance to be coded; where no utterance text exists, there is no model input and therefore no human–LLM comparison unit for that row." (02-1:19) The resulting eligible target population is "150,644 (Not coded 101,201; Keeping Everyone Together 19,704; Getting Students to Relate 2,556; Restating 2,145; Revoicing 3,431; Pressing for Accuracy 19,848; Pressing for Reasoning 1,759)" (02-1:19). "Reporting item: the rule removes 160 of 2,305 Restating rows (6.9%); all other categories change by less than 0.2%." (02-1:19)

### 2.3 Tag mapping and integrity checks

The tag-to-category mapping was verified by inspecting utterances against the manual definitions, with Tags 3 and 4 additionally examined with the preceding student utterance (02-1:28). Verified mapping and counts in the development file (02-1:31–37):

| Tag | Category | Count |
| --- | --- | --- |
| 0 | Not coded | 101,309 |
| 1 | Keeping Everyone Together | 19,704 |
| 2 | Getting Students to Relate | 2,556 |
| 3 | Restating | 2,305 |
| 4 | Revoicing | 3,436 |
| 5 | Pressing for Accuracy | 19,849 |
| 6 | Pressing for Reasoning | 1,759 |

"The seven verified category counts sum to the prespecified development-set teacher-utterance population of 150,918." (02-1:41) A reproducibility check on 2026-09-14 recomputed the population and category counts and found "exact agreement with the recorded values" (02-1:43). The 0-based row position of the raw file is the canonical row order (`source_id`), because the ±7 context window is defined over adjacent rows; the provider ID is kept as `source_row_id` for traceability only (02-1:49).

Known issues recorded in the decision document (02-1:51–55): (a) teacher real names remain in the transcripts (02-1:53); (b) "An open, unanswered issue in the corpus repository reports missing validation files. The development and held-out splits currently available may therefore differ from those used in the original dataset paper." (02-1:54); (c) 68 development-file rows marked as student speech carry a teacher tag; they are outside the `Speaker == "T"` population and no row is reassigned (02-1:55); (d) absent text is stored as the literal string `nan` in 1,019 rows (274 teacher, 745 student); the build scripts read with `keep_default_na=False` so that 12 genuine "None" utterances are retained (02-1:55).

### 2.4 Development and held-out sets

"The corpus's own split is used as provided: train_data_504.xlsx (503 transcripts) as the development set, test_data_63.xlsx (63 transcripts) as the held-out evaluation set. The split is at transcript level by construction." (02-2:12–15) Permitted use, settled 2026-08-29: "Development set: The main experiment runs here. The pilot sample is also drawn from here." and "Held-out evaluation set: Used once, for final evaluation, applying the rules developed on the development set without modification. Not touched before that point." (02-2:24–28)

The held-out file received one structural check on 2026-09-15 (23,250 teacher rows; no model calls or agreement calculations) (02-2:20). Held-out evaluation was later omitted by a post-freeze decision (02-2:32; HED:10); see Section 8. "The study's results refer to the development-set eligible target population defined in 2.1.2 and 2.3; no held-out result will be reported." (HED:19)

## 3. Sampling: main-experiment sampling frame, sample, seed (R-3)

Sources: 02-3:5–15, :25–39; 05-7:15–45; MSM; PFR:149–153.

### 3.1 Target population and primary estimand

"The inferential population is the eligible target population defined in 2.1.2 (decisions/02-1-dataset-selection-and-scope.md): the 150,644 development-set teacher utterances with utterance text present, out of the 150,918 teacher rows in the development file" (02-3:7). "The primary estimand is the change in overall human–LLM agreement, measured by Cohen's κ, when a specified coding-manual component is replaced with a placeholder. Agreement is therefore defined with respect to the natural category distribution of this population rather than to an artificially balanced evaluation distribution." (02-3:7)

### 3.2 Sampling design

"The main experimental sample will consist of 300 utterances selected by simple random sampling without replacement from the eligible target population (2.1.2). The same 300 utterances will be used in the baseline, all replacement conditions, and the names-only condition." (02-3:11) Agreement is measured by "ordinary (unweighted) Cohen's κ" because the categories are nominal (02-3:11).

Main-experiment sampling frame (revision of 2026-09-23): "The sampling frame for the main experiment is the eligible target population (2.1.2) minus the development targets D listed in 5.7.2 (`samples/dev_targets.csv`, 17 utterances): 150,644 − 17 = 150,627. D is excluded at the target level only." (02-3:13) The basis for excluding D: "any instrument change made after inspecting validation output was informed by these utterances. Excluding them from the main sample removes the possibility that the instrument was fitted to items it is later scored on." (05-7:45) D consists of 2 utterances per Tag drawn with `numpy.random.default_rng(20260923)` plus three prespecified boundary cases (`source_id` 0, 7 and 23541), 17 targets in total (05-7:19); the list is at 05-7:21–39. D rows are not removed from the ±7 context window of any other utterance (05-7:43).

Two stratified alternatives were considered and not adopted: disproportionate stratification without population weighting, because "the estimand becomes agreement in the constructed stratified sample rather than agreement in the prespecified eligible target population" (02-3:19), and disproportionate stratification with population standardization, which "introduces an additional estimation and validation layer that is not required for the present population-level question" (02-3:23).

### 3.3 Sample size

"The sample size of 300 is a prespecified, resource-constrained evaluation size rather than a statistically optimized quantity." (02-3:27) "The resulting sparsity of rare human-coded categories is therefore treated as a design limitation rather than as evidence that those categories are unaffected by the manipulation." (02-3:27)

Rare-category representation, as recorded: "the expected number of Pressing for Reasoning utterances in an SRS of 300 is approximately 3.5, and the probability of obtaining two or fewer is approximately 32%." (02-3:31) The same line states that "These quantities will be reproduced in a repository script using the corresponding hypergeometric calculation (`scripts/[filename].py`)." (02-3:31). Per ERR2, item 2, "the placeholder `scripts/[filename].py` was not replaced by an actual script file name. No repository script performing this hypergeometric calculation was created." (ERR2:14) The values at 02-3:31 are therefore reported here as recorded in the decision document, not as reproduced by a repository script. "Consequently, the study will not make inferential claims about category-specific effects." (02-3:31)

### 3.4 The main draw

"The main sample was drawn on 2026-09-24 with seed 20260924 by `scripts/build_main_sample.py` (numpy.random.Generator with PCG64; `choice(size=300, replace=False, shuffle=True)` over the reduced frame of 150,627 source_ids sorted ascending). Output: `samples/main_targets.csv` (300 source_ids, sha256 18ec7cd05b472fb26cbf64c983a9f84614a58dc26a7ec7f4f5b7329fd19553fe). Manifest: `reports/main-sample-manifest-2026-09-24.json`. Run commit eaa155d." (02-3:15)

The manifest records `eligible_count` 150644 and `frame_size` 150627 (MSM:8–9), seed 20260924 (MSM:11), and four checks all `true`: `len_drawn_equals_n`, `drawn_ids_unique`, `drawn_subset_of_eligible`, `drawn_disjoint_from_dev_targets` (MSM:31–36). The sampling script and its test were added after the protocol freeze to execute the frozen rule; the first draw at commit 095110b and the re-run at eaa155d produced byte-identical output (PFR:149–151). Overlap between the main sample and D was recomputed as 0 (IVR:106).

## 4. Conditions: components, placeholder, residual information, names-only (R-4)

Sources: 03-1:100–160; 03-2 (3.2.1–3.2.4); 03-3:1–13; 05-1:19–24.

### 4.1 Manual text and its segmentation

"The manual placed in the prompt is Chapter 1 of the TalkMoves Coding Manual (Teacher Talk Moves Coding Manual, sections 1.1–1.6). Chapter 2 (Student Talk Moves), the table of contents, the reference list, and page numbers are not placed in the prompt." (03-1:8) Components are segmented by four formatting units (paragraph, ➢ item, ■ item, section heading); sentence-level segmentation is not adopted (03-1:15–22). The inventory assigns all Chapter 1 text to nine component types a–i (03-1:32–44): a theoretical background sentences (3 sentences), b inclusion rule, c category scheme list, d move names, e definition paragraphs (6), f sub-clauses (16), g examples (61 example items), h exclusion rules (11), i section headings and numbers (03-1:34–42).

### 4.2 Relevance judgment and selection of replacement targets

"A component is task-relevant if its content bears on the assignment of an utterance to a move or to not-coded." (03-1:79) The judgment was made "by the author alone, from the manual text, before seeing any results." (03-1:86) Types a and i were judged not relevant, c was withheld, and b, d, e, f, g, h were judged relevant (03-1:88–98).

"Four types are selected. Relevant conditions: e (definitions), g (examples), h (exclusion rules). Negative control: a (background sentences). With the baseline (unmodified manual), the experiment has five conditions." (03-1:102) The three relevant types were chosen because each is cleanly separated by the formatting units, each spans the whole of Chapter 1, and "Each provides a distinct form of task-relevant information: definitions provide explicit assignment rules, examples provide demonstrations of qualifying utterances, and exclusion rules provide explicit criteria for withholding a move label. Related information remains elsewhere in the manual, and that residue is recorded separately in 3.1.7." (03-1:106–108)

Negative control: a is "the only one with substantive text" among the types judged not relevant (03-1:112). Its limitation is part of the condition definition: "the replaced content is far smaller than in the relevant conditions (3 sentences vs., e.g., 61 example items; measured 2026-09-15 with o200k_base on the assembled prompt for source_id 7: replaced spans total a 79 tokens, e 314, g 602, h 171, of a 2,202-token baseline prompt). The control therefore tests whether replacing irrelevant content changes agreement; it does not test whether replacing content at the volume of the relevant conditions changes agreement. No irrelevant text of comparable volume exists in Chapter 1." (03-1:113) The same token totals are in the replacement-manifest summary (RMS:6, :10–13).

Types not selected: b (its information "is nearly all duplicated in e and h"), c (relevance withheld), d (examined through the names-only reference rather than as a main condition), f (absent under Restating and Revoicing, so a manual-wide replacement would be asymmetric), and boundary statements (part of e) (03-1:117–121).

### 4.3 Residual-information record

"Each condition is defined by two lists: what is replaced, and what remains. The record of what remains is part of the condition definition and constrains how the estimated change in agreement can be interpreted for each condition." (03-1:130) The record (03-1:132–138):

| Condition | Replaced | What remains |
|---|---|---|
| Baseline | nothing | a–i, all of it |
| Definition replacement | e | Under four moves, sub-clauses and examples remain, so summaries of the definitions' content and utterance forms remain. Under Restating and Revoicing, only examples remain. Boundary statements are replaced along with e. The "coded as X" name strings go with e, so names remain only in the headings and the 1.2 list. |
| Example replacement | g | Definitions and sub-clauses remain, so descriptions of qualifying situations remain. The example-list heading, example utterances, `S:`/`T:` speaker-role markers, and parenthetical `(Restating)` / `(Revoicing)` labels are replaced. Inline examples inside 1.6 remain because they belong to h. The `■` item markers, the two-line layout of `S:`/`T:` items, and line breaks remain. Move names remain available elsewhere in the category list, move headings, and definition text. |
| Exclusion-rule replacement | h | The inclusion rule remains, so the definition of what is coded remains. The enumeration of what is not coded goes, and the inline examples inside 1.6 go with it. Least residue of the three relevant conditions. |
| Negative control | a | Everything bearing on assignment remains. |

"Move-name information remains available in every main condition through the category list, move headings, and definition text where applicable." (03-1:140)

A note recorded for the results discussion: "The examples in g have the functional form of demonstrations within the prompt and are therefore analogous to few-shot examples. The example-replacement condition removes these demonstrations while retaining the rest of the coding manual. It is therefore not treated as a standard few-shot-versus-zero-shot comparison, and no specific in-context-learning mechanism is inferred from the result." (03-1:167)

### 4.4 Placeholder specification

Purpose. "A placeholder is a string inserted in place of a manual-component instance and designed not to provide information relevant to the coding decision. Target components are replaced rather than deleted for two reasons." (03-2:4) First, to control prompt length in tokens: "each replaced component instance is matched locally with a placeholder containing the same number of tokens. Local matching also preserves the total input token count across conditions." (03-2:6) Second, to preserve the token positions of manual content after each replaced instance (03-2:8). "These controls are structural. Matching token count and downstream positions does not establish that the placeholder itself is behaviorally or computationally neutral." (03-2:10) "Placeholder replacement also does not reveal whether the model reads a given manual component or how it uses the information that remains when producing a label. Such response-process claims are outside the scope of the manipulation." (03-2:12)

Requirements. The filler must contain no coding-relevant lexical content, no explicit omission cue, no retained target content, no character that occurs in the manual text, and no unrelated natural-language filler; structural formatting is preserved; and the symbol is selected by procedural criteria independent of performance (03-2:26–34). "The placeholder is not assumed to be behaviorally or computationally neutral." (03-2:49) "Any observed change in agreement is interpreted as the effect of the implemented replacement condition, not as the effect of creating a completely neutral or empty region in the prompt." (03-2:51)

Selected form [decided 2026-09-15]: "Symbol `%`, space-separated repetition (rule B)." (03-2:68) "Construction rule: for a replacement site whose original text plus its line-ending newline occupies k tokens in the assembled prompt, the site text is replaced by k occurrences of `%` joined by single spaces. On marker lines the marker and one following space are preserved and the filler starts after that space (`■ % % %`, `➢ % % %`); on lines without a marker the filler starts at the first character (`% % %`). Line breaks, `■`/`➢` markers, and paragraph boundaries are unchanged." (03-2:70) Eleven candidate symbols were probed under two construction rules with tiktoken 0.14.0 / o200k_base (03-2:74). Contiguous repetition (rule A) was rejected because o200k_base merges long runs of one symbol into single tokens (03-2:76); under rule B "for all eleven candidates, `' ' + symbol` is one token for every repetition length tested (1–40) and every site of every condition matched exactly" (03-2:78). Symbols occurring in Chapter 1 (`.`, `:`, `?`, `;`) and symbols with markup meaning were rejected (03-2:80). "`%` retained: absent from Chapter 1, no Markdown or markup meaning, exact match at all 90 sites in one iteration. The selection was made without reference to any agreement result." (03-2:82) The condition files were generated with symbol `%`, rule B, converging in one iteration for every condition (BC:5–10).

Token-count matching procedure. Matching is performed per replaced instance with the tokenizer of the experimental model (03-2:95), because "Matching only the total token count of a condition could preserve overall prompt length while shifting the positions of content located between replacement spans." (03-2:99) After replacement the whole constructed text is re-tokenized to verify "1. the token count of each replacement instance against its baseline counterpart; 2. the token index, within the researcher-constructed text input, of the first unchanged content following each replacement; 3. the total token count of the researcher-constructed text input against the baseline." (03-2:105–107) "No token-count tolerance is defined." (03-2:101) Scope: "These checks establish condition-to-condition matching within the text content controlled by the study. They do not claim direct observation or reconstruction of the provider's complete internal API serialization or the absolute token positions of all request-structure tokens." (03-2:109)

Interpretation rules fixed in advance (03-2:126–129): "1. Results are interpreted as effects of the implemented replacement condition, not as pure estimates of the semantic contribution of the replaced component. 2. Token matching controls input length and downstream token positions, but does not establish that the placeholder is behaviorally or computationally neutral. 3. A small or uncertain estimated Δκ in the negative control does not establish placeholder neutrality. The negative-control result applies only to the amount and location of filler used in that condition and is reported with its uncertainty. 4. No claims are made about whether or how the model internally processes the placeholder."

Replacement sites per target: negative_control 1, definition_replacement 6, example_replacement 72, exclusion_rule_replacement 11, i.e. 90 site checks per target (IVR:42).

### 4.5 Names-only reference

"The names-only reference reports human–LLM agreement when the category names are provided without substantive coding-manual text. It is a supplementary descriptive reference and is excluded from the primary baseline-referenced Δκ comparisons." (03-3:5) "It is evaluated on the same sampled utterances and under the same model, API, repetition, aggregation, and output-handling specifications as the experimental conditions. No filler is added to match token count, information position, category-name repetition, or prompt structure." (03-3:7) "Report the unweighted Cohen's κ and its uncertainty interval for the names-only prompt. No inferential contrast with the experimental conditions is made. Differences in κ are not interpreted as identifying the contribution of category-name semantics or which information the model used. No "close to names-only" or "clearly above names-only" rules are used." (03-3:11) "The reference is not a chance baseline or a lower bound. Prior model exposure to TalkMoves or related material remains possible. Report it as "agreement obtained under the names-only reference prompt, with no substantive manual text supplied in the request," not as agreement produced using only category names." (03-3:13)

### 4.6 Condition identifiers

"Condition identifiers used in code follow 3.1.7 and 3.3: `baseline`, `definition_replacement`, `example_replacement`, `exclusion_rule_replacement`, `negative_control`, `names_only`." (05-1:24) The prompt order is "the task instruction; the manual (the baseline or one of the replacement versions, including the negative control, depending on condition; omitted in the names-only diagnostic); the context window with the target utterance marked; and the output instruction." (05-1:21)

## 5. Prompt and API request settings (R-5)

Sources: 05-1; 05-2:3–62; 05-3:7–63, :110–118.

### 5.1 Context window and prompt

"Each target utterance is presented with the seven preceding and seven subsequent utterances. Context size is counted in utterance rows (i.e., dataset rows), not conversational turns. Utterances from both students and teachers count toward the window." (05-1:7) The decision record gives as its basis the original study using this dataset, in which "a window of seven preceding and seven subsequent utterances produced the highest F1 score among the tested context windows (78.92; Suresh et al., 2022, Table 2)" (05-1:9); that source is cited here as recorded in the decision document. "Human coders read full transcripts, so any fixed window is a partial reproduction of the human coding condition; within that limit, the empirically best-performing window from the original study is used." (05-1:9) Near transcript boundaries "Only the available utterances are included; no empty-string padding is used." (05-1:13) Utterances are included in full, without the 30-token truncation of the original study (05-1:17).

"The context window and the target row contain only the speaker marker and the utterance text. No human label enters the prompt in any form: not the tag number, not the category name attached to a row, and not any field derived from `Tag` or `StudentTag`. Category names appear only in the output instruction (5.1.5) and, where present, inside the manual text." (05-1:22) "The model answers with a category name, not a tag number. The prompt does not expose the tag-number system; tag numbers are used only in parsing and scoring." (05-1:28)

Serialisation and marking (05-1:34–38): the target row is prefixed with `[TARGET] `; rows are written as `T: <text>` or `S: <text>` under a `Context:` header; the manual section is introduced by `Coding manual:`; a context row with missing text is rendered as the speaker marker alone.

Task instruction (05-1:42): "You are coding teacher talk in a mathematics classroom transcript. The Context block below shows consecutive lines from one transcript; T: marks the teacher and S: marks a student. Exactly one line is marked [TARGET]. Assign that target line to exactly one of the categories listed in the Output section. Use the other lines only as context and do not code them."

Output instruction (05-1:46): "Output: respond with a JSON object with a single key "category" whose value is exactly one of the following strings: "Not coded", "Keeping Everyone Together", "Getting Students to Relate", "Restating", "Revoicing", "Pressing for Accuracy", "Pressing for Reasoning". Do not include anything else."

### 5.2 Model and generation parameters

The model must allow local token-level verification of the constructed text with a compatible tokenizer and must be a fixed version throughout data collection (05-2:9–13). The selected model is the snapshot `gpt-5.5-2026-04-23` with tokenizer encoding `o200k_base` (05-2:22–25). "The same snapshot is used for all study-related API calls, including tool validation, the pilot, the main experiment, and the names-only diagnostic." (05-2:42) "Temperature is fixed at `0` for all experimental conditions." (05-2:48) `reasoning_effort = "none"` "is used because the task is constrained classification rather than open-ended reasoning." (05-2:57)

Environment record (05-2:85–95): Provider OpenAI; model snapshot `gpt-5.5-2026-04-23`; tokenizer `o200k_base`; tiktoken 0.14.0; temperature 0; reasoning effort none; Python 3.13.9; openai SDK 3.8.0; NumPy 2.3.5. Package versions were frozen until data collection and analysis were complete (05-2:98).

### 5.3 API request structure

"The endpoint is Chat Completions." (05-3:9) "The complete experimental prompt is sent as one `user` message. No `developer` or `system` message contains the coding manual or other experimental instructions." (05-3:17) Structured output with "a single required field, `category`, restricted to exactly one of the seven canonical category names defined in `scripts/tags.py`" (05-3:38), with `additionalProperties: false` and `strict: true` (05-3:50), and the identical schema in all six conditions (05-3:52). Output-token limit `max_completion_tokens` = 64 for all conditions (05-3:63). A technical verification call on synthetic input passed all eleven checks in 5.3.6, including `reasoning_tokens = 0` with structured output enabled (05-3:99–106).

"One utterance per call. Each API call codes exactly one target utterance." (05-3:114) "Independent requests. Every call is a new request with no conversation history, no prior output, and no continuation state." (05-3:116) "The execution order of utterance × condition × repetition is shuffled with a recorded seed so that no condition is systematically executed in a distinct time period." (05-3:118)

In the main run, the manifest records `model` `gpt-5.5-2026-04-23`, `temperature: 0`, `reasoning_effort: none`, `max_completion_tokens: 64` and the json_schema response format (MRR:62), and `response_model` was `gpt-5.5-2026-04-23` in all 5,400 pass 1 attempts (MRR:73).

## 6. Repetition, aggregation, response handling (R-6)

Sources: 05-4:13–87; 05-6:116–133; 04-2:1–31.

"R = 3 independent calls per item-condition." (05-4:15) "The planned number of calls, excluding retries and tie-break calls, is 300 utterances × 6 conditions × 3 repeats = 5,400." (05-4:17) The record states that this "is a prespecified, resource-constrained label-construction rule, not an increase in sample size" and that "This rationale does not establish final-label stability or optimality; plurality is not claimed to eliminate stochastic noise or recover a true/stable model label." (05-4:17)

"The final label of an item-condition is the plurality label, i.e., the label with the largest count among valid repeats." (05-4:21) "If two or more labels share the largest count among valid repeats, one additional independent call is made and plurality is re-evaluated over all valid repeats, including the added one. This step is repeated at most twice, so an item-condition receives at most 5 repeats in total. If a tie remains after the second additional call, the item-condition receives no final label and is recorded with reason `unresolved tie`." (05-4:27)

Parser and validity. The parser "requires a case-sensitive exact match against one of the seven canonical category names" with no other transformation (05-4:37). A response is invalid when `finish_reason` is not `stop`, a `refusal` field is present, the content is not JSON, the `category` field is missing or extra fields are present, or the value is outside the enum (05-4:45–49). "`Not coded` is a valid substantive label and is never merged with, or used as a fallback for, an invalid response." (05-4:51) Retryable errors are retried within the same repeat with exponential backoff (05-4:57); "Each repeat is allowed at most 3 attempts." (05-4:74) Aggregation is performed over valid repeats only and only with at least 2 valid repeats; otherwise the item-condition is recorded as `insufficient valid repeats` (05-4:80–83). "An item-condition without a final label is never converted to `Not coded` and is never silently dropped from analysis." (05-4:85)

Parsing outputs (05-6:124–125): `labels.csv` has one row per completed attempt; `final_labels.csv` has one row per (utterance, condition) with `status` ∈ {`resolved`, `tie_pending`, `unresolved_tie`, `insufficient_valid_repeats`}. The parser re-derives outcome and category from the raw response and refuses to write if they differ from the recorded values (05-6:120).

Repeated-call indicators (04-2): unanimity rate (04-2:11), mean agreement with the final label (04-2:15), ties and additional calls (04-2:19), items without a final label (04-2:23), and initial-pattern counts 3/3, 2/1, 1/1/1 (04-2:29). "All indicators are reported per condition as descriptive statistics only. No inferential test, interval, or between-condition contrast is computed on them, and they are not part of the primary estimand (Δκ)." (04-2:5)

## 7. Validation, pilot, freeze, execution (R-7)

Sources: 05-5; 05-7; TVR; PPR; PFR:1–143; IVR; MRR.

### 7.1 Tool validation (Roadmap 9)

"Tool validation checks that the assembled request presents the correct target utterance and the coding task, that the model output maps to the seven categories of `scripts/tags.py`, and that each condition implements its specified manipulation (3.1, 3.2, 3.3). The verification level is that of an output-level coding study: no claim about cognitive mechanism is made and no minimum κ is required. Low agreement alone is not a failure criterion." (05-7:9) Changes permitted after inspecting validation output are limited to instruction wording, serialisation, target marker, empty-text rendering, response interpretation and record format, "and only when a defect is confirmed by re-reading the raw responses, the prompts and the run records" (05-7:51); component boundaries, filler, condition list, model, repetition rules, execution order, scorer rules and sampling design are prohibited from change "regardless of the results" (05-7:53).

Executed on the 17 development targets D: `check_inputs.py` passed all 102 target × condition checks (TVR:74); `check_token_matching.py` ran 1,530 site checks with 0 mismatches, and the total token count of every replacement condition equalled the baseline total for every target (TVR:76); the test suite passed (160 tests) (TVR:98); the full prompts of two targets under all six conditions were read by the user (TVR:100). The validation run made 306 calls, all HTTP 200, `finish_reason` `stop`, 0 invalid, 0 retries (TVR:117–132). The scorer was applied as a diagnostic: "The values below are diagnostic information for further inspection (5.7.1, 5.7.4). They are not a pass criterion, and they are kept separate from the procedural pilot (5.5)." (TVR:148) Anomaly inspection found no category never produced, no inverted mapping, no evidence of coding a non-target row, and 0 invalid responses (TVR:263–266); two inspected disagreements were coding judgements in the gold labels, not tool defects (TVR:280, :290). "None. No change within the permitted list of 5.7.3 (instruction wording, serialisation, target marker, empty-text rendering, response interpretation, parser, mapping, record format) was made, and no change outside it was proposed." (TVR:307)

### 7.2 Procedural pilot (Roadmap 10)

"The pilot is used only to verify procedural execution. Human–LLM agreement statistics, including Cohen's κ, are not calculated or reported during the pilot." (05-5:3) The pilot run (`pilot-2026-09-24`, 306 calls on D) recorded 306 `attempt_completed` records, all HTTP 200 and `success`, 0 HTTP 429, 0 timeouts, 0 retries, maximum concurrency 4 (PPR:51–58, :76–84). The operational settings were fixed from these metrics: concurrency 4; timeout 60 s; backoff_initial 2 s; backoff_max 60 s; consecutive-failure threshold 10 (PPR:87; 05-6:47, :58). "No procedural failure occurred, so no change under the conditions of 5.7.3 was made" (PPR:118).

### 7.3 Protocol freeze (Roadmap 11)

The freeze commit is `ed13ec2`, 2026-09-24 (PFR:13). "No research decision was changed: every edit either promoted an existing [proposed] tag to [decided 2026-09-24] or rewrote a sentence that referred to tool validation or the procedural pilot as future work" (PFR:21); 18 tags were promoted and 7 forward-looking sentences synchronised (PFR:23, :38). The frozen values (PFR:61–77) include the model snapshot, tokenizer, endpoint, generation parameters, structured-output schema, operational settings, call-order seeds (pass 1 = 20260918; pass 2 = 20260919; pass 3 = 20260920), the six condition identifiers, R = 3 with plurality, tie rules, attempt limits, D, the sampling rule and the scorer and bootstrap rules. The sha256 of every frozen tracked file at `ed13ec2` and of the git-ignored derived files is recorded (PFR:83–133). "Roadmaps 12–14 execute the frozen protocol rather than reopen design choices; any exception requires the change procedure in §5.7.3." (PFR:139)

### 7.4 Input verification on the main sample (Roadmap 13)

At commit `6673383` (IVR:11), `check_inputs.py` on the 300 targets ended with "All checks passed for 300 target(s) x 6 conditions." (IVR:34; `reports/check-inputs-main-2026-09-24.txt:302`), and `check_token_matching.py` reported "RESULT: 0 failing condition/source_id pairs; 27000 site checks run" (IVR:42; TMC:1208), with 1,200 `PASS` lines (300 targets × 4 replacement conditions) and 0 `FAIL` (IVR:42). A dry run wrote `prompts.jsonl` with 1,800 rows and `prompts_sha256` `4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140` (IVR:69–71); the planned call list was reproduced from the seed (IVR:73). Checks on `prompts.jsonl` found no gold-leak pattern and no category name in the task instruction or Context block, and no `Coding manual` section in any names_only row (IVR:87–90). "None. No script, prompt template, condition file, decision document or sample was changed during Roadmap 13." (IVR:110)

### 7.5 Main run (Roadmap 14)

Execution commit `beb3ef984f1b8bd0ec73f7c9f96171f80cddf1eb`; input `samples/main_targets.csv`; planned calls 5,400 (MRR:12–14). A read-only integrity audit before execution found no mismatch between protocol, sample, inputs and code; three omissions in the freeze record were completed by an append-only entry, after which the re-check concluded "READY FOR MAIN-RUN EXECUTION (re-check at beb3ef9)" (MRR:20–24). A precheck dry run reproduced the expected `prompts_sha256`, `n_calls` and `input_file.sha256` (MRR:44–48).

Pass 1: 5,400 calls; 5,400 `attempt_completed` records; HTTP 200 × 5,400; `outcome` `success` × 5,400; `response_model` `gpt-5.5-2026-04-23` × 5,400; `finish_reason` `stop` × 5,400; 0 refusals; 0 invalid responses; 0 attempts numbered ≥ 2; 0 HTTP 429; 0 timeouts (MRR:66–81). After pass 1, one pair was `tie_pending`: (54297, names_only), with repeats 1 / 2 / 3 labelled Pressing for Reasoning / Pressing for Accuracy / Not coded (MRR:85). Pass 2 made one call (repeat 4, label Not coded), after which `tie_pending` was 0 (MRR:104); pass 3 reported "pass 3 not needed: no tie_pending rows in final_labels.csv" and made no API call (MRR:112). "Total API calls: 5,401 (pass 1: 5,400; pass 2: 1)." (MRR:114)

Processing: `labels.csv` 5,401 rows, all `valid`; `final_labels.csv` 1,800 rows, all `resolved` (MRR:122–125). Elapsed time of pass 1 was 1,392.794 s with median latency 0.970 s and maximum concurrency 4 (MRR:145–148); `reasoning_tokens` sum 0 (MRR:153). Prompt caching was observed (79.01% of prompt tokens in pass 1) and "recorded as descriptive operational information only" (MRR:159). "None. No script, prompt template, condition file, decision document, sample or operational setting was changed between the precheck dry run and the completion of data collection." (MRR:163)

## 8. Protocol deviations and post-freeze records (R-8)

Sources: PFR:145–195; HED:1–19; ERR1; ERR2.

### 8.1 Post-freeze implementation artifacts (no protocol change)

Entries appended to the freeze record document artifacts added after `ed13ec2` "to execute the frozen sampling rule (02-3). No frozen specification was changed, so none of these entries is a change under §5.7.3." (PFR:147) They are the sampling script and test (PFR:149), the main draw and its manifest (PFR:151), the 02-3 revision note (PFR:153), the `paths.py` constant, the sampling test file and the three Roadmap 13 reports (PFR:155–161), and the completeness report with the two archival snapshots (PFR:173–176).

### 8.2 Held-out evaluation omitted

"Held-out evaluation will be omitted." (HED:10) Timing: "Main-run data collection (`run_id` `main-2026-09-24`, execution commit beb3ef984f1b8bd0ec73f7c9f96171f80cddf1eb) was complete when this decision was recorded: pass 1 and pass 2 finished, and the runner reported that pass 3 was not needed. No scorer had been run on the main run." (HED:13)

Nature of the decision, verbatim: "This decision departs from the plan in 02-2 §2.2.3 (line 26), which stated that the held-out set would be used once for final evaluation. The frozen decision documents do not state held-out evaluation as optional. Section 5.7.3 does not specify a procedure for changes to Section 2.2. This decision is therefore recorded separately as a post-freeze deviation from the held-out evaluation plan. The decision was made after completion of main-run data collection and before any main-study κ, Δκ or bootstrap result was computed or examined; it was not based on main-study agreement results. The held-out set has had one structural check (2026-09-15) and no model calls or agreement calculations." (HED:16)

Consequence: "The study's results refer to the development-set eligible target population defined in 2.1.2 and 2.3; no held-out result will be reported." (HED:19) The freeze record carries the same deviation as a separate appended section (PFR:163–167), and 02-2 carries a revision note pointing to the decision without altering the text of 2.2.3 (02-2:32).

### 8.3 Documentation-only updates and errata

Before scoring, documentation-only changes were made and hashed: the 02-2 revision note, a `DECISIONS.md` table-of-contents clean-up, path redaction in four report files, and the first errata document (PFR:180–189). ERR1 records stale wording that was not edited before scoring, including: 05-4:31 says tie-break placement is "pass 2" whereas repeat 5 is recorded as pass 3 (ERR1:7–10); 05-6:41 and 05-6:90 describe the prompts file and the dry-run sequence in wording that differs from the implemented behaviour (ERR1:12–20); several sentences were "written before the step they describe was completed" (ERR1:22–26); and `scripts/scorer.py:8` has a stale docstring (ERR1:28–31). The 02-3:13 sentence about the seed "not yet fixed" is superseded by the revision note at 02-3:15 (ERR1:25).

After scoring, ERR2 records two further items: the freeze-record entry for 02-3 lacks the commit ID and file size of the change (ERR2:7–10), and "the placeholder `scripts/[filename].py` was not replaced by an actual script file name. No repository script performing this hypergeometric calculation was created." (ERR2:12–15). The post-scoring errata file is itself registered in the freeze record (PFR:191–195).

### 8.4 Changes after inspecting output

At each stage the record states that no change was made after inspecting output: tool validation (TVR:307), procedural pilot (PPR:118), input verification (IVR:110) and the main run (MRR:163). One reporting restriction was added after results were seen; it is listed as P1 in Section 13 with that marking (MSR:361–363).

## 9. Completeness (R-9)

Source: CR §4–§8.

Coverage: 5,400 manifest calls unique by (utterance_id, condition, repeat); the manifest utterance set equals the 300 `source_id`s of the sample file; the observed condition set equals the six prespecified identifiers; 1,800 calls per repeat; the calls form the full 300 × 6 × 3 cross product with 0 missing and 0 extra (CR:34–38). "All coverage checks: PASS." (CR:40)

Raw attempts to labels: 5,401 manifest calls, 5,401 `attempt_completed` records, exactly one `success` per call; `labels.csv` 5,401 rows, all `valid`; the `category` in every `labels.csv` row equals the `category` in the matching raw response, 0 mismatches; `final_labels.csv` holds the 1,800 pairs with one row each (CR:46–55). Final label and status were recomputed for every pair from `labels.csv` by code that follows only 05-4 lines 21, 27 and 80–83 and does not import the repository parser or scorer: "1,800 pairs compared with `final_labels.csv`, 0 mismatches in `final_label` or `status`. PASS." (CR:63)

Final-label status by condition (CR:71–78): every condition has 300 `resolved`, 0 `tie_pending`, 0 `unresolved_tie`, 0 `insufficient_valid_repeats`.

"No missing final labels remain; the planned complete 300-item analysis set is available to the scorer." (CR:82) The conditional rule for an incomplete analysis set (06:27) therefore did not apply. The human-label file was checked only for size and sha256 at this stage; "The human labels are read for the first time by the scorer in Roadmap 16." (CR:95)

## 10. Analysis methods (R-10)

Source: 06:5–75.

"[decided 2026-09-19] The analysis rules below were adopted before main-experiment results." (06:3)

Input and scoring unit. Analysis uses `final_labels.csv` after the last pass has terminated and the parser has been rerun (06:9). Before any statistic, the scorer verifies from the attempt records that every call is terminated and re-derives the final labels from the attempts files, stopping if they differ from the file on disk (06:11). "Repeated calls construct a label; they are not additional sampled observations. Category mapping is exactly `scripts/tags.py`, including `Not coded` as a substantive category." (06:15)

Condition-specific κ. "For each condition, report ordinary unweighted Cohen's κ against human labels on the utterances with a resolved final label in that condition, together with that analysis n. With contingency-table proportions, κ = (P_o − P_e) / (1 − P_e), where P_o is observed agreement and P_e is the sum of products of human and predicted marginal proportions across the seven canonical categories. Numeric tag values do not define distances or weights." (06:17)

Paired Δκ. "For each of the three substantive replacements and the negative control, define its paired set as the utterances with resolved final labels in both baseline and that condition. Recompute both κ values on that same set; Δκ = κ_replacement − κ_baseline. Distinguish this paired-set baseline κ from the standalone baseline κ in 6.1.1. Names-only has its own descriptive κ and uncertainty interval under 3.3, not a baseline-referenced inferential contrast." (06:21) "Do not impute missing final labels or convert them to `Not coded`." (06:23) For each comparison the original n, paired n, the both/baseline-only/condition-only/neither counts, the terminal missing-status counts and "the actual number of condition-discordant final labels on the paired set" are reported (06:25).

Uncertainty. "Use paired utterance-level bootstrap with two-sided 95% pointwise percentile intervals (2.5th and 97.5th percentiles), 10,000 replicates, and bootstrap seed 20260919. These are individual-statistic intervals, not simultaneous coverage across the three substantive contrasts." (06:33) "Each replicate draws 300 utterance indices with replacement from the complete original 300-record table. Carry the human label, all condition final labels, and all missingness states together, including repeated occurrences of a sampled index. Use the same draw for every condition." (06:35) The generator is `numpy.random.Generator(numpy.random.PCG64(20260919))`, the table rows are ordered by `utterance_id` ascending, and percentiles use `numpy.percentile(values, [2.5, 97.5], method="linear")`; the NumPy version is recorded because the draws are reproducible only together with it (06:37).

Undefined and degenerate statistics. κ is undefined when the analysis set is empty or P_e = 1; undefined values are reported as `not estimable`, never replaced by zero (06:49). Undefined replicates are counted and a percentile CI is withheld "if at least one replicate is undefined" (06:51–53). A defined but degenerate interval such as [0, 0] is reported with paired n and the discordant count and is not read as equivalence (06:57; 02-3:35).

Non-independence. "Retain paired utterance-level resampling and the decision against transcript cluster resampling in 2.3.7. The target remains the fixed eligible finite population, not a transcript superpopulation." (06:61) "The bootstrap approximates sampling uncertainty for κ and Δκ from the observed utterance/final-label records under the stipulated sampling and execution assumptions. Those records include realized stochastic outputs, but this procedure does not separately estimate variability from rerunning the API on the same 300 utterances. It is not evidence that the same final labels or Δκ would reproduce under a complete rerun." (06:63)

Robustness. A high-repeat auxiliary study was "considered but not adopted"; "Its omission does not establish the stability of the R = 3 procedure." (06:67) Single-repeat sensitivity analysis is "optional and unresolved, not adopted by this specification. No repeat-specific κ/Δκ analysis is silently added." (06:69)

Descriptive reporting. Raw agreement, marginal distributions and confusion matrices are reported on the corresponding analysis sets and "create no new inferential contrast or rare-category inference (2.3.6)." (06:73) "Retain three substantive baseline-referenced Δκ estimates, condition-specific κ and uncertainty; negative-control contextual κ/Δκ and uncertainty with all 3.1.7 boundaries; and names-only descriptive κ and uncertainty with all 3.3 boundaries. Do not subtract the control, use it as a pass/fail threshold, or create a names-only contrast." (06:75)

Scorer validation. Synthetic, hand-checkable point-estimate fixtures are implemented in `tests/test_scorer_kappa.py` (passed 2026-09-21, commit `bdfac6a`) and CI-policy fixtures in `tests/test_scorer_bootstrap.py` (passed 2026-09-22, commit `df0963f`) (06:79).

## 11. Results: standalone κ, paired Δκ, uncertainty (R-11)

Source: MSR §8–§9 (MSR:98–150). Scoring was executed once on 2026-09-24 with `python scripts/score_run.py --run-id main-2026-09-24`, exit code 0, at commit `c56ed33` (MSR:19, :38–47, :49), under Python 3.13.9 and NumPy 2.3.5 (MSR:27), with 10,000 bootstrap replicates and seed 20260919 (MSR:31). Integrity checks on the output recorded 245 metadata/structure/report–JSON checks with mismatch count 0, and an independent standard-library recomputation of the 18 point estimates and 10 n fields with mismatch count 0 and maximum absolute difference 3.5344990823027445e-17 (MSR:87–88). "Values are rounded for display only; calculations use the unrounded values in score_summary.json." (MSR:7)

### 11.1 Standalone κ per condition

"Ordinary unweighted Cohen's κ; all intervals are 95% pointwise percentile intervals." (MSR:100) Table reproduced from MSR:102–109:

| Condition | Analysis n | κ | 95% CI | Undefined / replicates | Undefined proportion | Degenerate |
| --- | --- | --- | --- | --- | --- | --- |
| baseline | 300 | 0.6085 | [0.5266, 0.6846] | 0 / 10000 | 0.0000 | false |
| definition_replacement | 300 | 0.6067 | [0.5252, 0.6824] | 0 / 10000 | 0.0000 | false |
| example_replacement | 300 | 0.5473 | [0.4658, 0.6239] | 0 / 10000 | 0.0000 | false |
| exclusion_rule_replacement | 300 | 0.5023 | [0.4244, 0.5767] | 0 / 10000 | 0.0000 | false |
| negative_control | 300 | 0.5852 | [0.5060, 0.6605] | 0 / 10000 | 0.0000 | false |
| names_only | 300 | 0.2727 | [0.1971, 0.3475] | 0 / 10000 | 0.0000 | false |

The names_only row is a standalone descriptive κ reported under the wording of R2 (Section 13); it enters no contrast.

### 11.2 Paired Δκ per condition, referenced to the paired-set baseline

"The paired-set baseline κ is computed on the same paired set as its condition κ; it is distinct in definition from the standalone baseline κ in Section 8. Δκ = κ_replacement − κ_baseline. Negative control is included alongside the substantive contrasts as context." (MSR:115) Each row below is an individual baseline-referenced estimate with its own interval; no contrast between the substantive conditions is made (R3, Section 13).

Paired-set composition, reproduced from MSR:117–122:

| Condition vs baseline | Original n | Paired n | Both | Baseline only | Condition only | Neither | Discordant final labels |
| --- | --- | --- | --- | --- | --- | --- | --- |
| definition_replacement | 300 | 300 | 300 | 0 | 0 | 0 | 16 |
| example_replacement | 300 | 300 | 300 | 0 | 0 | 0 | 24 |
| exclusion_rule_replacement | 300 | 300 | 300 | 0 | 0 | 0 | 39 |
| negative_control | 300 | 300 | 300 | 0 | 0 | 0 | 16 |

Terminal missing-status counts (`unresolved_tie`, `insufficient_valid_repeats`) are 0 on both sides of every comparison (MSR:124–129).

Estimates, reproduced from MSR:131–144:

| Comparison condition | Statistic | Estimate | 95% CI | Undefined / replicates | Undefined proportion | Degenerate |
| --- | --- | --- | --- | --- | --- | --- |
| definition_replacement | paired-set baseline κ | 0.6085 | [0.5266, 0.6846] | 0 / 10000 | 0.0000 | false |
| definition_replacement | paired-set condition κ | 0.6067 | [0.5252, 0.6824] | 0 / 10000 | 0.0000 | false |
| definition_replacement | Δκ | -0.0018 | [-0.0384, 0.0360] | 0 / 10000 | 0.0000 | false |
| example_replacement | paired-set baseline κ | 0.6085 | [0.5266, 0.6846] | 0 / 10000 | 0.0000 | false |
| example_replacement | paired-set condition κ | 0.5473 | [0.4658, 0.6239] | 0 / 10000 | 0.0000 | false |
| example_replacement | Δκ | -0.0611 | [-0.1047, -0.0191] | 0 / 10000 | 0.0000 | false |
| exclusion_rule_replacement | paired-set baseline κ | 0.6085 | [0.5266, 0.6846] | 0 / 10000 | 0.0000 | false |
| exclusion_rule_replacement | paired-set condition κ | 0.5023 | [0.4244, 0.5767] | 0 / 10000 | 0.0000 | false |
| exclusion_rule_replacement | Δκ | -0.1062 | [-0.1576, -0.0556] | 0 / 10000 | 0.0000 | false |
| negative_control | paired-set baseline κ | 0.6085 | [0.5266, 0.6846] | 0 / 10000 | 0.0000 | false |
| negative_control | paired-set condition κ | 0.5852 | [0.5060, 0.6605] | 0 / 10000 | 0.0000 | false |
| negative_control | Δκ | -0.0232 | [-0.0581, 0.0118] | 0 / 10000 | 0.0000 | false |

Read individually against the prespecified rules:

- Definition replacement: Δκ −0.0018, interval [−0.0384, 0.0360]; the interval includes zero (C2, MSR:341).
- Example replacement: Δκ −0.0611, interval [−0.1047, −0.0191]; the estimate and both interval bounds are below zero (C1, MSR:339).
- Exclusion-rule replacement: Δκ −0.1062, interval [−0.1576, −0.0556]; the estimate and both interval bounds are below zero (C1, MSR:339).
- Negative control: Δκ −0.0232, interval [−0.0581, 0.0118]; the interval includes zero (C2, MSR:341). It is reported as context and is not subtracted from, used to adjust, or used as a pass/fail criterion for the substantive estimates (R6, MSR:353).

### 11.3 Conditional reporting

"Conditional reporting: observed-paired-set limitation due to missing final labels — not applicable (0 cases); undefined original κ/Δκ requiring `not estimable` — not applicable (0 cases); CI withholding — not applicable (0 cases); degenerate intervals, including [0, 0] — not applicable (0 cases). Undefined counts and proportions for all 18 bootstrap statistics are explicitly reported in Sections 8–9." (MSR:148) "Zero-discordance cases: not applicable (0 cases)." (MSR:150) Discordant counts are shown for all four contrasts above; no numerical cutoff for "very small" discordant counts is defined in 02-3:35, and none is introduced here (MSR:150).

Post-result reporting restriction: "Δκ is not interpreted as a percentage-point change in accuracy." (P1, MSR:363; added at Roadmap 16-4, after results were seen.)

## 12. Descriptive and repeated-call diagnostics (R-12)

Source: MSR §10–§11 (MSR:152–331). All values in this section are descriptive only (U6, R4; Section 13).

### 12.1 Repeated-call diagnostics

Definitions and denominators follow 04-2 (MSR:154). Tables reproduced from MSR:156–172:

| Condition | n_items | initial_valid_denominator | items_lacking_all_initial_valid | pattern_3_3 | pattern_3_3_share | pattern_2_1 | pattern_2_1_share | pattern_1_1_1 | pattern_1_1_1_share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 300 | 300 | 0 | 282 | 0.9400 | 18 | 0.0600 | 0 | 0.0000 |
| definition_replacement | 300 | 300 | 0 | 285 | 0.9500 | 15 | 0.0500 | 0 | 0.0000 |
| example_replacement | 300 | 300 | 0 | 289 | 0.9633 | 11 | 0.0367 | 0 | 0.0000 |
| exclusion_rule_replacement | 300 | 300 | 0 | 283 | 0.9433 | 17 | 0.0567 | 0 | 0.0000 |
| negative_control | 300 | 300 | 0 | 287 | 0.9567 | 13 | 0.0433 | 0 | 0.0000 |
| names_only | 300 | 300 | 0 | 271 | 0.9033 | 28 | 0.0933 | 1 | 0.0033 |

| Condition | unanimity_rate | items_with_final_label | mean_agreement_with_final | items_with_tie | additional_calls_total | calls_repeat_4 | calls_repeat_5 | unresolved_tie | insufficient_valid_repeats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.9400 | 300 | 0.9800 | 0 | 0 | 0 | 0 | 0 | 0 |
| definition_replacement | 0.9500 | 300 | 0.9833 | 0 | 0 | 0 | 0 | 0 | 0 |
| example_replacement | 0.9633 | 300 | 0.9878 | 0 | 0 | 0 | 0 | 0 | 0 |
| exclusion_rule_replacement | 0.9433 | 300 | 0.9811 | 0 | 0 | 0 | 0 | 0 | 0 |
| negative_control | 0.9567 | 300 | 0.9856 | 0 | 0 | 0 | 0 | 0 | 0 |
| names_only | 0.9033 | 300 | 0.9672 | 1 | 1 | 1 | 0 | 0 | 0 |

"Denominator-zero reporting (`unavailable`): not applicable (0 cases). Calls in the tables are logical calls (repeats), not attempts." (MSR:174)

### 12.2 Raw agreement and expected agreement

Reproduced from MSR:180–187:

| Condition | Analysis n | Exact agreement count | P_o | P_e |
| --- | --- | --- | --- | --- |
| baseline | 300 | 236 | 0.7867 | 0.4551 |
| definition_replacement | 300 | 235 | 0.7833 | 0.4492 |
| example_replacement | 300 | 223 | 0.7433 | 0.4330 |
| exclusion_rule_replacement | 300 | 209 | 0.6967 | 0.3906 |
| negative_control | 300 | 230 | 0.7667 | 0.4374 |
| names_only | 300 | 167 | 0.5567 | 0.3904 |

### 12.3 Marginal distributions and confusion matrices

The human and predicted marginal counts and the 7 × 7 confusion matrix for each of the six conditions are recorded in MSR:189–331 (baseline MSR:189–211; definition_replacement MSR:213–235; example_replacement MSR:237–259; exclusion_rule_replacement MSR:261–283; negative_control MSR:285–307; names_only MSR:309–331). They are not reproduced here. The human marginal counts of the 300-utterance sample are the same in every condition: Not coded 207, Keeping Everyone Together 41, Getting Students to Relate 1, Restating 2, Revoicing 4, Pressing for Accuracy 42, Pressing for Reasoning 3 (MSR:193–199). "Marginal distributions are reported as stored category counts with the analysis n; no additional proportions or statistics were calculated." (MSR:178)

## 13. Interpretation boundaries (R-13)

Sources: MSR §12 (MSR:333–363); 01:66–96; 03-1:142–156; 03-2:122–129; 03-3:11–13. The twelve sentences below are the claim-boundary set of the scoring record, reproduced verbatim. The wording of that set was supplied by Jiwon at Roadmap 16-6 (MSR:335); the scoring record states that "C1/C2 were checked against the unrounded JSON delta values and interval bounds." (MSR:335)

### 13.1 Prespecified boundaries (MSR:337–359)

- C1. Under the implemented replacement procedure, agreement with the human labels was lower than the paired-set baseline in the example-replacement and exclusion-rule-replacement conditions: the baseline-referenced Δκ and its 95% interval were both below zero in each. The causal claim is restricted to the effect of the implemented manipulation on agreement. (01-research-question.md:73; 03-1:144, :146) (MSR:339)
- C2. For definition replacement and the negative control, the 95% interval for Δκ includes zero. No direction or magnitude is claimed, and this is not interpreted as evidence of no effect, maintained agreement, or equivalence between the baseline and replacement conditions. A small or uncertain negative-control Δκ does not establish general filler neutrality. (03-1:146, :150) (MSR:341)
- R1. All prespecified estimates and intervals are reported (Sections 8–11). (MSR:343)
- R2. Names-only is reported with its standalone descriptive κ, its 95% interval, and the per-condition descriptive diagnostics; no baseline-referenced Δκ and no inferential contrast with the experimental conditions is made. It is reported as agreement obtained under the names-only reference prompt, with no substantive manual text supplied in the request, not as agreement produced using only category names. It is not a chance baseline or a lower bound, and prior model exposure to TalkMoves or related material remains possible. No "close to names-only" or "clearly above names-only" rules are used. (06:21, :75; 03-3:5, :11, :13) (MSR:345)
- R3. No direct contrast between substantive conditions was performed. Each interval is an individual-statistic interval referenced to the paired-set baseline, not simultaneous coverage across contrasts. No multiplicity adjustment is specified in decisions/06-analysis.md. (06:27, :33, :69) (MSR:347)
- R4. Confusion matrices, marginals, and raw agreement are descriptive only. No inferential claim is made about category-specific effects, and no baseline-to-replacement transition analysis is added. (02-3:31; 06:73) (MSR:349)
- R5. No claim is made about mechanisms, which information the model used, what the human coders relied on, a component's independent contribution or intrinsic importance, whether a replaced component is necessary, equivalence, or noninferiority. (01-research-question.md:74–88; 03-1:148, :152, :154) (MSR:351)
- R6. The negative control replaces background text judged task-irrelevant and is much smaller in volume than the substantive replacements. Its κ, Δκ, and interval are reported alongside the substantive Δκ estimates as context. It is not subtracted from those estimates, not used to adjust them, and not used as a pass/fail criterion. Its interpretation is limited to the specific passage replaced, the amount and location of filler, and the execution conditions used. A change in agreement in the control does not by itself invalidate the substantive replacement results. (03-1:150, :152; 06:75) (MSR:353)
- R7. Each condition's estimated change in agreement is interpreted in light of the residual manual information recorded for that condition under 3.1.7, including label semantics, redundancy among manual components, and other possible routes to agreement. (03-1:130, :148) (MSR:355)
- U6. Repeated-call indicators are reported per condition as descriptive statistics only; no inferential test, interval, or between-condition contrast is computed on them, and they are not part of the primary estimand. An invalid response is not a substantive disagreement category. Logical calls are repeats, not attempts. (04-2:5, :29, :31) (MSR:357)
- U11. The main sample was drawn from the main-experiment sampling frame of 150,627 utterances, which is the eligible target population of 150,644 utterances minus the 17 development targets D, excluded at the target level only. (02-3:13) "The study's results refer to the development-set eligible target population defined in 2.1.2 and 2.3; no held-out result will be reported." (reports/heldout-evaluation-decision-2026-09-24.md:19) (MSR:359)

"(Sections 8–11)" in R1 refers to the sections of the scoring record, which correspond to Sections 11 and 12 of this report.

### 13.2 Post-result reporting restriction (MSR:361–363)

- P1. Post-result reporting restriction added at 16-4: Δκ is not interpreted as a percentage-point change in accuracy. (MSR:363)

P1 was added after the results were seen; it restricts reporting and adds no claim.

### 13.3 Boundaries stated in the decision documents and the held-out decision

The following sentences are part of the interpretation boundary of this report in addition to 13.1–13.2:

- "Results on TalkMoves do not generalize to the later study's coding manual." (01:96)
- "It is not evidence that the same final labels or Δκ would reproduce under a complete rerun." (06:63)
- "The reference is not a chance baseline or a lower bound. Prior model exposure to TalkMoves or related material remains possible." (03-3:13)
- "Consequently, the study will not make inferential claims about category-specific effects." (02-3:31)
- "An overall null or small Δκ therefore cannot be interpreted as evidence that every category is unaffected by manual-component replacement." (02-3:39)
- "3. A small or uncertain estimated Δκ in the negative control does not establish placeholder neutrality." (03-2:128)
- "Such results will also not be interpreted as evidence that the replaced component is unnecessary." (03-1:148)
- "These are individual-statistic intervals, not simultaneous coverage across the three substantive contrasts." (06:33)
- "The study's results refer to the development-set eligible target population defined in 2.1.2 and 2.3; no held-out result will be reported." (HED:19)

### 13.4 Application to the negative control

The negative control was executed under the same verification as the substantive conditions: its replacement site (one site check per target, IVR:42) was covered by the token-matching check on the 300 targets, whose result line reads `RESULT: 0 failing condition/source_id pairs; 27000 site checks run` with 1,200 `PASS` lines and 0 `FAIL` lines (IVR:42; TMC:1208), the condition's 300 prompts were among the 1,800 rows checked for gold leaks (IVR:83–89), all 300 of its item-conditions are `resolved` (CR:78), and no input or setting was changed during data collection (MRR:163). With execution documented in this way, the interpretation of its estimate (Δκ −0.0232, interval [−0.0581, 0.0118]; MSR:144) is limited exactly as the prespecified rule states: "The negative-control Δκ and its uncertainty will be reported alongside the substantive Δκ estimates as context. The control will not be subtracted from those estimates, used to adjust them, or used as a pass/fail criterion. A change in agreement in a validly executed control does not by itself invalidate the substantive replacement results. Control results do not establish model-internal mechanisms or which information the model actually used." (03-1:152) and by C2 (MSR:341). No numerical criterion for the size of a control change is defined in the decision documents, and none is introduced here.

### 13.5 Application to descriptive diagnostics

Under R4, the discordant final-label counts in Section 11.2 and the marginals and confusion matrices referenced in Section 12.3 are descriptive. No baseline-to-replacement transition analysis was performed on the discordant items, and no error-pattern exploration was conducted; these are listed as future work in Section 14.

## 14. Discussion and future work (R-14)

This section stays within Section 13. It adds no analysis, no numerical criterion and no claim beyond the sentences cited there.

### 14.1 What the results support

The two result statements are C1 and C2 (Section 13.1). Under R3 no contrast between the substantive conditions was performed, so this report does not order the conditions or compare the sizes of their Δκ estimates; each Δκ is read on its own against the paired-set baseline (Section 11.2). Under P1, Δκ is not restated as a change in accuracy.

Under R7, each estimate is read with the residual-information record of its condition (Section 4.3). For definition replacement, the record states that under four moves "sub-clauses and examples remain, so summaries of the definitions' content and utterance forms remain" (03-1:135). For example replacement, "Definitions and sub-clauses remain, so descriptions of qualifying situations remain." (03-1:136), and the condition "is therefore not treated as a standard few-shot-versus-zero-shot comparison, and no specific in-context-learning mechanism is inferred from the result." (03-1:167). For exclusion-rule replacement, "The inclusion rule remains, so the definition of what is coded remains. The enumeration of what is not coded goes, and the inline examples inside 1.6 go with it. Least residue of the three relevant conditions." (03-1:137). These sentences describe what each prompt contained. They are conditions on interpretation, not explanations of the observed estimates: under R5, no claim is made about which information the model used, and the causal claim is "restricted to the effect of the implemented manipulation on agreement" (01:73). Interpretation also does not separate the effect of removing the component's information from the effect of the inserted filler: "Any observed change in agreement is interpreted as the effect of the implemented replacement condition, not as the effect of creating a completely neutral or empty region in the prompt." (03-2:51)

For the names-only reference, R2 applies in full: its κ is "agreement obtained under the names-only reference prompt, with no substantive manual text supplied in the request" (03-3:13), and no contrast with any other condition is drawn.

### 14.2 Candidate directions for follow-up, starting from the exclusion-rule-replacement result

The decrease recorded in C1 for the exclusion-rule-replacement condition is the observation from which the following directions for a subsequent study are formulated. They are questions for new designs, not findings of this study. They are not mutually exclusive, none of them was tested here, and none is offered as a mechanism, as evidence of which information the model used, or as evidence of the component's independent contribution or intrinsic importance (R5; 03-2:126–129; 01:74–76).

- Category-boundary information. Type h "Contains the explicit exclusion rules specifying which utterances are not coded." (03-1:97). A subsequent design could ask whether agreement changes when other manual text that draws boundaries between categories is replaced, for example the boundary statements that this study did not isolate because "there are three instances in the whole manual" (03-1:24).
- Negative or contrastive formulation. The exclusion rules are the ➢ items of section 1.6 (03-1:41), the section headed "1.6 What is not coded" (`reports/manual-inventory-check-2026-09-15.txt:109`). Whether the form of a rule (stated as what is not coded versus as what is coded) matters for agreement would require a rewriting manipulation, which is a different operation from placeholder replacement and is outside the present design.
- False-positive suppression and class-distribution effects. The predicted marginal counts in the scoring record are descriptive (R4) and no category-specific inference is drawn from them (02-3:31); a subsequent study could prespecify descriptive transition tables from baseline to replacement final labels, which this study did not add (R4).
- Implementation characteristics of the filler and its position. The negative-control interpretation is limited to "the specific passage replaced, the amount and location of filler, and the execution conditions used" (03-1:150), and token matching "does not establish that the placeholder is behaviorally or computationally neutral" (03-2:127). A subsequent design could vary the filler form, using the candidate forms rejected here for this study's purpose (03-2:57–64) as alternatives under a new specification, or the location of replaced text, to examine whether agreement changes with these implementation characteristics independently of the component replaced.

### 14.3 Analyses not performed in this study

- Baseline-to-replacement transition analysis and error-pattern exploration. Discordant final-label counts per comparison are reported (Section 11.2), but the items were not decomposed by human category or by the direction of the label change, and no error patterns were examined (R4). A future study could prespecify such tables as descriptive output.
- Repeat-level analyses. No repeat-specific κ/Δκ analysis was added (06:69), and no high-repeat auxiliary study was run; "Its omission does not establish the stability of the R = 3 procedure." (06:67)
- Rerun variability. The bootstrap "does not separately estimate variability from rerunning the API on the same 300 utterances" (06:63); estimating that variability would require a separate, prespecified rerun design.
- Held-out evaluation. It was omitted (HED:10) and "no held-out result will be reported" (HED:19). An evaluation on data not used in development remains open for a separate study with its plan fixed before any result is seen.
- Length-matched names-only reference. In this study "No filler is added to match token count, information position, category-name repetition, or prompt structure." (03-3:7) for the names-only prompt; a subsequent design could specify a length-matched reference if a contrast with that reference were to be part of its estimand.

### 14.4 Methodological premise

The study's position is that of "a methodological pre-study for a later human–AI interaction study" (01:92–93). "Results on TalkMoves do not generalize to the later study's coding manual. The transferable methodological premise is that a manual developed for human coders should not be assumed, without validation, to function equivalently when used as an LLM prompt." (01:96)

## 15. Limitations (R-15)

Sources: 02-3:29–31, :37–39; 03-1:113; 03-2:10, :127–129; 06:63; 01:96; and the repository records cited per item.

- Rare categories and scope of inference. "The main limitation of this sampling decision is reduced sensitivity to effects concentrated in rare coding categories. An overall null or small Δκ therefore cannot be interpreted as evidence that every category is unaffected by manual-component replacement. The result supports only the prespecified population-level claim about overall agreement, within the category distribution represented by the eligible target population of TalkMoves development-set teacher utterances (2.1.2)." (02-3:39) In the drawn sample the human marginal counts are Getting Students to Relate 1, Restating 2, Revoicing 4 and Pressing for Reasoning 3 (MSR:193–199), and "the study will not make inferential claims about category-specific effects." (02-3:31) The sample size is "a prespecified, resource-constrained evaluation size rather than a statistically optimized quantity." (02-3:27)
- Negative-control volume. "The control therefore tests whether replacing irrelevant content changes agreement; it does not test whether replacing content at the volume of the relevant conditions changes agreement. No irrelevant text of comparable volume exists in Chapter 1." (03-1:113; the full sentence, with the token totals, is quoted in Section 4.2)
- Placeholder neutrality. "Matching token count and downstream positions does not establish that the placeholder itself is behaviorally or computationally neutral." (03-2:10) "3. A small or uncertain estimated Δκ in the negative control does not establish placeholder neutrality. The negative-control result applies only to the amount and location of filler used in that condition and is reported with its uncertainty. 4. No claims are made about whether or how the model internally processes the placeholder." (03-2:128–129)
- Scope of token verification. The token checks "do not claim direct observation or reconstruction of the provider's complete internal API serialization or the absolute token positions of all request-structure tokens." (03-2:109)
- Uncertainty scope. "It is not evidence that the same final labels or Δκ would reproduce under a complete rerun." (06:63) The intervals are individual-statistic intervals, "not simultaneous coverage across the three substantive contrasts" (06:33), and "No multiplicity adjustment is specified in decisions/06-analysis.md." (R3, MSR:347)
- Label construction. The R = 3 plurality rule "does not establish final-label stability or optimality" (05-4:17); the repeated-call indicators in Section 12.1 are descriptive only (04-2:5).
- Context condition. "Human coders read full transcripts, so any fixed window is a partial reproduction of the human coding condition" (05-1:9); utterances near transcript boundaries receive less context (05-1:13).
- Single model, single setting. All calls used one dated snapshot, `gpt-5.5-2026-04-23`, with temperature 0 and reasoning effort none (05-2:24, :52–53); results are reported for this configuration only.
- Reference standard. The human labels are the corpus labels used as the reference standard (01:49); the decision record notes that the development and held-out splits currently available "may therefore differ from those used in the original dataset paper" (02-1:54) and that, for the two disagreements inspected during tool validation, the record concludes for source_id 9340 that "The disagreement is a coding judgement recorded in the dataset's gold label for a one-word utterance, not a tool defect." and "As a single case it is not generalised into the Known issues of 2.1.3." (TVR:280), and for source_id 191127 that "This is a borderline coding judgement, not a rendering or alignment defect." (TVR:290).
- Names-only reference. "The reference is not a chance baseline or a lower bound. Prior model exposure to TalkMoves or related material remains possible." (03-3:13)
- Held-out evaluation. Omitted by a post-freeze decision (HED:10, :16); "no held-out result will be reported." (HED:19)
- Generalization. "Results on TalkMoves do not generalize to the later study's coding manual." (01:96)
- Documentation. The hypergeometric quantities at 02-3:31 were not reproduced by a repository script (ERR2:14); other stale sentences are listed in ERR1 and ERR2 and were left unedited in the frozen documents.

## 16. AI/tool use (R-16)

Sources: MSR §13 (MSR:365–378); TVR §10 (TVR:313–321); the tool-use items of the other records where present.

| Stage | Tool / party | Role as recorded | Source |
| --- | --- | --- | --- |
| Tool validation (Roadmap 9) | Codex (OpenAI) | "Read-only audit at `a058391` and API-specification comparison (section 2). No code was modified." | TVR:317 |
| Tool validation (Roadmap 9) | Claude Code (Claude Fable 5.1) | "Implementation of `scripts/build_dev_targets.py` and its tests; drafts of `decisions/05-7-tool-validation.md` and of the 2.3 and 6.2.1 revisions; execution of the static checks, the dry run, the parser and the scorer; this record." | TVR:318 |
| Tool validation (Roadmap 9) | Claude (Fable 5.1, decision session) | "Consolidation of decisions and drafting of the task prompts." | TVR:319 |
| Tool validation (Roadmap 9) | User | "All decisions, reading of the assembled prompts, execution of the real API run, all commits." | TVR:320 |
| Procedural pilot (Roadmap 10) | User | The pilot run command "was run by the user in a local terminal, consistent with the validation run." | PPR:43 |
| Procedural pilot (Roadmap 10) | — | No tool-use item in the record beyond the line above. | — |
| Protocol freeze (Roadmap 11) | — | No tool-use item in the record. | — |
| Input verification (Roadmap 13) | — | No tool-use item in the record. | — |
| Main run (Roadmap 14) | Codex | "An independent read-only audit (Codex) was run at HEAD `d0bd38f`." The audit modified no file; its reports "were delivered to the user in the conversation and are not stored in the repository." | MRR:18, :28 |
| Main run (Roadmap 14) | User | The pass 1 command "was run by the user in a local terminal, consistent with the validation and pilot runs." | MRR:60 |
| Main run (Roadmap 14) | Assistant session (unnamed in the record) | The parser was first run "in an assistant session that was interrupted by a usage limit before its report was completed; the parser was then re-run in a new session and the outputs were byte-identical." | MRR:133 |
| Completeness (Roadmap 15) | — | No tool-use item in the record. | — |
| Held-out decision | — | No tool-use item in the record. | — |
| Scoring (Roadmap 16) | Codex | "16-0 preflight; 16-1 execution; 16-2 integrity check; 16-3 independent recomputation; 16-4 result report" and "16-6 record drafting" | MSR:371, :375 |
| Scoring (Roadmap 16) | Jiwon | "16-4 interpretation decisions"; "16-8 commit" — "Jiwon (assigned; not performed in 16-6)"; the Section 12 boundary wording "supplied by Jiwon in the Roadmap 16-6 request, Section 8" | MSR:372, :376, :335 |
| Scoring (Roadmap 16) | Claude Code | "16-5a, 16-5b boundary checks and source check"; Roadmap 16-7 independent audit of the record draft, result "READY TO COMMIT" | MSR:373, :378 |
| Scoring (Roadmap 16) | Claude (claude.ai project chat) | "Cross-review of prompts and reports" | MSR:374 |
| Final report (Roadmap 18) | Claude Code | Roadmap 18-1 planning report; this draft (18-3), written from the repository files cited in it; the 18-4 corrections. No scorer rerun, no recomputation, no API call. | this document |
| Final report (Roadmap 18) | Jiwon | Decisions on format, language, section structure, boundary handling and reference policy; the 18-4 list of corrections. | this document |
| Final report (Roadmap 18) | Claude (claude.ai project chat) | Cross-review of the plan and of this draft. | this document |

Rows marked "No tool-use item in the record" are left without content because the cited record contains no such item; nothing is inferred for them.

The scoring record additionally notes that the Claude Code boundary-check and source-check reports of Roadmap 16-5 are uncommitted and that their conclusions are attributed to the supplied Roadmap 16-6 request rather than to independently opened copies (MSR:94–96).

## References and sources

This report cites the repository's decision documents and records by path and line. External works referenced by those documents (the placeholder-design literature at 03-2:14–18 and 03-2:84–91, the lecture sources at 03-2:18 and 03-2:120, the context-window basis at 05-1:9, and the sources at 05-2:123–126) are cited here only as recorded in the decision documents; their original texts were not accessed during the drafting of this report, and no specific claim in this report rests on them beyond what the decision documents state. The corpus is identified as recorded in README.md:12–14 and 02-1:5–6: SumnerLab/TalkMoves (GitHub), CC BY-NC-SA 4.0.
