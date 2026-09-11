## 3.2 Placeholder specification
### 3.2.1 Purpose and scope of placeholder replacement

[proposed 2026-09-07] A placeholder is a string inserted in place of a manual-component instance and designed not to provide information relevant to the coding decision. Target components are replaced rather than deleted for two reasons.

First, placeholder replacement is used to control prompt length across conditions. In this study, prompt length is measured by the number of input tokens because LLMs process inputs as tokens and context length is defined in token units (Park, 2026). Changes in input length can affect model performance (Levy, Jacoby, & Goldberg, 2024). Deleting a manual-component instance would therefore change both its information content and the length of the prompt. To avoid this confound, each replaced component instance is matched locally with a placeholder containing the same number of tokens. Local matching also preserves the total input token count across conditions.

Second, placeholder replacement is used to preserve the token positions of manual content that occurs after each replaced instance. Information position can affect LLM performance. Liu et al. (2024) found that performance varies depending on where relevant information appears in the input, with stronger performance near the beginning and end and weaker performance in the middle. Deleting an instance would shift the manual content that follows it to earlier positions in the token sequence. Locally token-matched replacement is therefore used to keep intervening and subsequent manual content at the same token positions as in the baseline prompt.

These controls are structural. Matching token count and downstream positions does not establish that the placeholder itself is behaviorally or computationally neutral. Placeholder form and its remaining limitations are specified separately in Sections 3.2.2–3.2.4.

Placeholder replacement also does not reveal whether the model reads a given manual component or how it uses the information that remains when producing a label. Such response-process claims are outside the scope of the manipulation.

Sources:

- Levy, M., Jacoby, A., & Goldberg, Y. (2024). *Same Task, More Tokens: The Impact of Input Length on the Reasoning Performance of Large Language Models*. Proceedings of ACL 2024, 15339–15353.
- Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). *Lost in the Middle: How Language Models Use Long Contexts*. Transactions of the Association for Computational Linguistics, 12, 157–173.
- Park, W. (2026). *Prompt Engineering Part 1: Historically Important Techniques (2022–2024).* Lecture slides, SNU KDT, June 2026.

### 3.2.2 Placeholder form

[decided 2026-09-08; originally proposed 2026-09-07] The placeholder uses a deterministic non-lexical symbol filler. The purpose of the filler is to remove the lexical information carried by the replaced component without introducing new natural-language content. The exact symbol is not yet fixed; it will be selected using the procedural criteria below before data collection.

#### Placeholder requirements

| Requirement | Rule | Rationale |
|---|---|---|
| No coding-relevant lexical content | The filler must not contain words or phrases that describe the coding categories, assignment rules, examples, exclusions, or the type of component replaced. | Such content would reintroduce information relevant to the coding decision. |
| No explicit omission cue | Forms such as `[definition omitted]`, `[example removed]`, or `[redacted]` are not used. | They identify the nature of the missing content and may invite the model to infer or reconstruct it. |
| No retained target content | No part of the replaced component is repeated or retained as filler. | The manipulated information would remain partially available. |
| No unrelated natural-language filler | Lorem ipsum, random word sequences, grammatical task-irrelevant sentences, and coherent unrelated passages are not used. | They introduce additional lexical or semantic content and may function as distractor context. |
| Structural formatting preserved | Paragraph boundaries, line breaks, item markers, dialogue markers, and other structural delimiters that are not themselves part of the target component remain unchanged. | This minimizes formatting differences between the baseline and replacement conditions. |
| Selection independent of performance | The exact symbol is selected using tokenizer compatibility, exact token-match feasibility, stable serialization, preservation of surrounding formatting, and pipeline compatibility. | The placeholder form must be fixed independently of agreement results rather than selected according to which form produces a preferred performance pattern. |

Original rule (superseded 2026-09-08):

Structural preservation follows the component assignments established in Section 3.1. For example replacement, `➢ Examples:`, `■`, `S:`, and `T:` remain in place because they define the structure of the example block rather than its lexical coding information. Move-name strings assigned to component d, including parenthetical labels such as `(Restating)` and `(Revoicing)`, also remain. Only the lexical content assigned to component g is replaced.

Revised rule (2026-09-08; current):

The `➢ Examples:` heading is replaced together with the example content. Although it marks the beginning of the example block, the word `Examples` explicitly identifies the type of information removed and therefore provides component-specific information. The heading was already assigned to type g in Section 3.1.8, so replacing it keeps the manipulation consistent with the existing component assignment.

Within example items, `S:`, `T:`, and parenthetical move labels such as `(Restating)` and `(Revoicing)` are also replaced because they carry information about speaker roles or the move instantiated by the example. Generic layout features such as item boundaries and line breaks are retained.

The revision was made after examining the informational function of these markers in the actual example items, before observing experimental results.


The placeholder is not assumed to be behaviorally or computationally neutral. Research on filler tokens has produced different results across models and experimental settings. Lanham et al. (2023) found that replacing chain-of-thought content with filler did not recover performance in the models they tested, whereas Pfau et al. (2024) showed that repeated filler tokens could support computation under specific training conditions. Brauer et al. (2026) provide evidence that some recent models can perform computation across content-free filler positions. These findings do not establish what will occur in the present prompt setting, but they rule out treating filler tokens as guaranteed computationally inert.

The purpose of the filler is therefore narrower: it provides a minimally lexical replacement that permits token count and downstream token positions to be controlled. Any observed change in agreement is interpreted as the effect of the implemented replacement condition, not as the effect of creating a completely neutral or empty region in the prompt.

Prompt formatting is also treated as a potential source of variation. Sclar et al. (2024) showed that seemingly superficial prompt-formatting choices can affect model performance. The existing structural shell of the manual is therefore preserved wherever it is not part of the manipulated component.

#### Candidate forms considered

| Candidate | Decision | Reason | Source / basis |
|---|---|---|---|
| Repetition of a non-lexical symbol | Retained | Introduces minimal lexical information and can potentially be constructed to an exact token length. The exact symbol remains to be selected by procedural criteria. | Design rationale (this study). Filler is not assumed to be computationally neutral; see Lanham et al. (2023), Pfau et al. (2024), and Brauer et al. (2026). |
| Repetition of the first part of the replaced component | Not adopted | Leaves part of the manipulated information available, making the condition partly readable rather than replacing the component's lexical content. | Design rationale (this study). Zhang et al. (2026) provides a first-repeat replacement as an ablation precedent in a different, non-text-prompt setting. |
| Lorem ipsum or random word sequences | Not adopted | Introduces lexical material that is absent from the baseline and may act as distractor context. | Shi et al. (2023); Zhou et al. (2023). |
| Grammatical but task-irrelevant text | Not adopted | Introduces additional semantic content unrelated to the coding task, creating an irrelevant-context manipulation in addition to the intended component replacement. | Shi et al. (2023). |
| Coherent text on an unrelated topic | Not adopted | Introduces a competing semantic context and therefore an additional potential source of interference. | Shi et al. (2023); Zhou et al. (2023). |
| Explicit omission marker, such as `[definition omitted]` | Not adopted | Identifies what was removed and therefore provides information about the manipulated component. It also does not naturally supply the required replacement length. | Design rationale (this study). |

Sources:

- Brauer, K., Mayrink Verdun, C., & Marks, S. (2026). *Reading Between the Dots: Decoding Hidden Computation across Filler Tokens*. arXiv preprint arXiv:2607.03502.
- Lanham, T., Chen, A., Radhakrishnan, A., Steiner, B., Denison, C., Hernandez, D., Li, D., Durmus, E., Hubinger, E., Kernion, J., Lukošiūtė, K., Nguyen, K., Cheng, N., Joseph, N., Schiefer, N., Rausch, O., Larson, R., McCandlish, S., Kundu, S., Kadavath, S., Yang, S., Henighan, T., Maxwell, T., Telleen-Lawton, T., Hume, T., Hatfield-Dodds, Z., Kaplan, J., Brauner, J., Bowman, S. R., & Perez, E. (2023). *Measuring Faithfulness in Chain-of-Thought Reasoning*. arXiv preprint arXiv:2307.13702.
- Pfau, J., Merrill, W., & Bowman, S. R. (2024). *Let's Think Dot by Dot: Hidden Computation in Transformer Language Models*. Conference on Language Modeling (COLM 2024). arXiv:2404.15758.
- Shi, F., Chen, X., Misra, K., Scales, N., Dohan, D., Chi, E. H., Schärli, N., & Zhou, D. (2023). *Large Language Models Can Be Easily Distracted by Irrelevant Context*. Proceedings of the 40th International Conference on Machine Learning, 202, 31210–31227.
- Zhang, T., Bigverdi, M., & Krishna, R. (2026). *Ablate-to-Validate: Are Vision-Language Models Really Using Continuous Thought Tokens?* arXiv preprint arXiv:2605.21642.
- Zhou, Y., Geng, X., Shen, T., Tao, C., Long, G., Lou, J.-G., & Shen, J. (2023). *Thread of Thought Unraveling Chaotic Contexts*. arXiv preprint arXiv:2311.08734.

### 3.2.3 Token count matching procedure

[proposed 2026-09-08; scope clarified 2026-09-11] Token-count matching is performed separately for each replaced component instance using the tokenizer corresponding to the model used in the experiment. The procedure is defined at the token level because the model receives token IDs produced by the tokenizer rather than raw text directly, and tokenization differs across models (Lee, 2026, pp. 23–28).

The selected model and tokenizer are specified in Section 5.2.1.

Local matching is required because the selected components occur at multiple positions in the manual. Matching only the total token count of a condition could preserve overall prompt length while shifting the positions of content located between replacement spans. Each definition paragraph, example item, and exclusion-rule item is therefore matched separately to its baseline counterpart.

Exact token-count matching is the target. Whether every replacement instance can be matched exactly using the placeholder form selected in 3.2.2 has not yet been established. If exact matching is not possible for some instances, the rule for resolving the mismatch, including whether the filler symbol is changed or a token-count tolerance is permitted, remains unresolved and must be fixed before data collection. [unresolved]

After replacement, the complete researcher-constructed text input is tokenized again using the model-compatible tokenizer to verify:

1. the token count of each replacement instance against its baseline counterpart;
2. the token index, within the researcher-constructed text input, of the first unchanged content following each replacement;
3. the total token count of the researcher-constructed text input against the baseline.

These checks establish condition-to-condition matching within the text content controlled by the study. They do not claim direct observation or reconstruction of the provider's complete internal API serialization or the absolute token positions of all request-structure tokens. The API endpoint, message structure, and output-format configuration will therefore be held identical across experimental conditions so that any request-level structure outside the manipulated text is not intentionally varied between conditions.

For each replacement instance, the original token count, replacement token count, and verification result will be recorded. The location and format of this record have not yet been decided. [unresolved]

Revision note (2026-09-08): Local instance-level matching was made explicit after recognizing that global token-count matching alone does not preserve the positions of content between multiple replacement spans.

Revision note (2026-09-11): The scope of token-position verification was clarified. Local tokenizer access permits verification of the researcher-constructed text input but does not by itself demonstrate reconstruction of the provider's complete internal API token sequence.


Sources:

- Lee, J. (2026). *Large Language Models*. Lecture slides, Seoul National University.

### 3.2.4 Interpretation rules fixed in advance

[proposed 2026-09-08] Condition-specific rules are fixed in 3.1.7.

1. Results are interpreted as effects of the implemented replacement condition, not as pure estimates of the semantic contribution of the replaced component.
2. Token matching controls input length and downstream token positions, but does not establish that the placeholder is behaviorally or computationally neutral.
3. A no-change result in the negative control applies only to the amount and location of filler used in that condition and does not establish placeholder neutrality more generally.
4. No claims are made about whether or how the model internally processes the placeholder.