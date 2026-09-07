## 3.2 Placeholder specification
### 3.2.1 Purpose and scope of placeholder replacement

[proposed 2026-09-07] A placeholder is a string that occupies the position of a replaced manual component without providing information relevant to the coding decision. Target components are replaced rather than deleted for two reasons.

First, placeholder replacement is used to match prompt length across conditions. In this study, prompt length is measured by the number of input tokens, because LLMs process inputs as tokens and context length is defined in token units (Prompt Engineering Part 1, June 2026). Changes in input length can affect model performance (Levy, Jacoby, & Goldberg, 2024). Deleting a manual component would therefore change both its content and the total input length. To avoid this confound, each placeholder is constructed to match the token count of the text it replaces, so that the total input token count is matched across conditions.

Second, placeholder replacement is used to preserve the positions of the manual components that follow the replaced component. Information position can affect LLM performance. Liu et al. (2024) found that performance varies depending on where relevant information appears in the input, with stronger performance near the beginning and end and weaker performance in the middle. Deleting a component would shift all subsequent manual content forward. Replacing it with a token-matched placeholder is intended to keep the starting positions of subsequent components unchanged.

Replacing it with a token-matched placeholder is intended to keep the starting positions of subsequent components unchanged. As noted in recent methodological studies (e.g., Zhang et al., 2026), isolating structural confounds—such as token budget preservation and positional anchoring—is critical when manipulating prompt components, ensuring that experimental controls target structural integrity rather than conflating content utilization with length effects.

Placeholder replacement does not control, and does not reveal, whether the model reads a given component, or how the model uses the information that remains when it produces a label. These response-process questions are outside the scope of the manipulation.

Sources:
- Levy, M., Jacoby, A., & Goldberg, Y. (2024). Same Task, More Tokens: the Impact of Input Length on the Reasoning Performance of Large Language Models. Proceedings of ACL 2024, 15339–15353.
- Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M., Petroni, F., & Liang, P. (2024). Lost in the Middle: How Language Models Use Long Contexts. Transactions of the Association for Computational Linguistics, 12, 157–173.
- Park, W. (2026). Prompt Engineering Part 1: Historically Important Techniques (2022–2024). Lecture slides, SNU KDT, June 2026.
- Zhang, T., Bigverdi, M., & Krishna, R. (2026). Ablate-to-Validate: Are Vision-Language Models Really Using Continuous Thought Tokens? arXiv preprint arXiv:2605.21642.

### 3.2.2 Placeholder form

[proposed 2026-09-07] The placeholder form is not yet decided. Six candidates have been raised. Each candidate is listed with the review points recorded so far. No candidate has been rejected.

Candidates:

1. Repetition of one character (e.g., `xxxx`).
   - Carries no coding-relevant content.
   - Is recognizable as a redaction mark. The model receives the signal that something was here and is unreadable.
   - Recent large models can perform computation over content-free repeated tokens (Brauer et al., 2026). The placeholder position may therefore be used for computation that cannot be observed. Earlier results were negative for some models (Lanham et al., 2023) and positive only with specific training (Pfau et al., 2024).
   - Runs of repeated characters tokenize in chunks, so an exact token-count match may not be reachable.
   - Closest precedent: the constant/zero replacement in Zhang et al. (2026). In their discrete-token setting, constant/zero replacement lowered accuracy (LLaVA 77.69 → 73.66; Qwen 71.24 → 58.87), and in two off-the-shelf systems (Mirage, CoVT) zero replacement lowered accuracy more than distribution-matched random replacement. Their replacements were in embedding space, not in prompt text; the precedent is for the design, not evidence about text placeholders.

2. Repetition of the first part of the replaced component.
   - Closest precedent: the first-repeat replacement in Zhang et al. (2026).
   - Some content of the component remains. The condition would be "partly readable", not "unreadable".

3. Text with neither meaning nor grammar (e.g., lorem ipsum, random word lists).
   - May act as a distractor. Zhou et al. (2023) locate LLM difficulty in distractors rather than in long irrelevant context. An agreement drop could then not be separated from filler interference.
   - Earlier record (September 2026): risk of the model reconstructing a scenario from the filler.

4. Grammatical text with no coding-relevant content.
   - Raised 2026-09-07. Not yet reviewed.

5. Coherent text on an unrelated topic.
   - Content interference. Earlier record (September 2026) cites Chatziveroglou et al. (2025); the citation is to be verified before use.

6. A marker naming the omission (e.g., `[definition omitted]`).
   - Is short, so token count cannot be matched.
   - Names what was removed, which invites the model to infer or supply the content.

Points that apply to every candidate:
- Whether the model reads the placeholder position, or uses it for computation, cannot be observed.
- If the placeholder differs in formatting from the surrounding manual text, the formatting difference is itself a variable (Sclar et al., 2024).
- Whether the chosen form breaks the model's output format at the required length is a procedure check for the pilot. Changing the character or text within the chosen form is allowed in the pilot; changing the condition set is not.

Sources:
- Brauer, K., Mayrink Verdun, C., & Marks, S. (2026). Reading Between the Dots: Decoding Hidden Computation across Filler Tokens. arXiv preprint arXiv:2607.03502.
- Lanham, T., et al. (2023). Measuring Faithfulness in Chain-of-Thought Reasoning. arXiv preprint arXiv:2307.13702.
- Pfau, J., Merrill, W., & Bowman, S. R. (2024). Let's Think Dot by Dot: Hidden Computation in Transformer Language Models. Conference on Language Modeling (COLM). arXiv:2404.15758.
- Sclar, M., Choi, Y., Tsvetkov, Y., & Suhr, A. (2024). Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design or: How I learned to start worrying about prompt formatting. ICLR 2024. arXiv:2310.11324.
- Zhang, T., Bigverdi, M., & Krishna, R. (2026). Ablate-to-Validate: Are Vision-Language Models Really Using Continuous Thought Tokens? arXiv preprint arXiv:2605.21642.
- Zhou, Y., Geng, X., Shen, T., Tao, C., Long, G., Lou, J.-G., & Shen, J. (2023). Thread of Thought Unraveling Chaotic Contexts. arXiv preprint arXiv:2311.08734. Abstract as reproduced in Park, W. (2026), Prompt Engineering Part 2, lecture slides, SNU KDT.
- Park, W. (2026). Prompt Engineering Part 1: Historically Important Techniques (2022–2024). Lecture slides, SNU KDT. S2A section: slide claim, without primary citation, that current models often answer correctly despite irrelevant context.
- Chatziveroglou et al. (2025): cited in an earlier record; not verified.
### 3.2.3 Token count matching procedure

### 3.2.4 Interpretation rules fixed in advance