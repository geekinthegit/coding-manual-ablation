# 1. Research Question

## 1.1 RQ wording
- Status: settled (2026-08-29)
- Decision: "How does replacing specific components of a coding
  manual with placeholders change an LLM's agreement with human
  dialogue coding?"
- Revision history (documented retrospectively from working records):

  - v1 (2026-08-24) "Which components of a dialogue coding manual
    drive agreement between LLM and human coding?" — rejected.
    The wording presupposes that each component's contribution can
    be identified separately. The manual's components define
    themselves by reference to one another (complementary category
    definitions split by a single criterion; exclusion rules that
    presuppose all category definitions), so ablating one changes
    the operating conditions of the others. The design cannot
    attribute a Δκ to one component's own contribution.

  - v2 (2026-08-24) "How sensitive is LLM–human coding agreement to
    the removal of individual components from an intact dialogue
    coding manual?" — adopted as the replacement for v1: it
    repositioned the study from identifying important components
    (contribution) to observing how agreement moves under ablation
    (sensitivity), which was judged at the time to better match what the design measures. Superseded on 2026-08-29 for two reasons.
    (a) "How sensitive" can be read as asking for a single sensitivity quantity, such as a rate of change. The design produces per-condition Δκ values rather than a separately defined sensitivity measure, so the wording leaves room for an interpretation not operationalized in the design.
    (b) "Removal" misstated the manipulation from the day v2 was
    adopted. Placeholder substitution had already been settled as
    the design on 2026-08-24: token length and position are
    preserved and only the information content is replaced.
    Removal would mean the content is gone and length and position
    shift. The mismatch was not noticed until 2026-08-29.

  - v3 (drafted 2026-08-25, rejected 2026-08-29) "Can an LLM
    reliably reproduce human dialogue coding when specific
    components of the coding manual are removed?" — a candidate
    written to fit a research-tool question template (task, tool,
    manipulation, criterion, measure). Never adopted; v2 remained
    in force until v4. Rejected for three reasons.
    (a) It is a yes/no question about whether performance holds
    under removal. The design does not measure that; it measures
    how much agreement changes relative to the full manual (Δκ).
    The question form and the measurement did not match.
    (b) "Reliably reproduce" merges two measurements that this
    design keeps separate: reliability, meaning consistency across
    repeated calls with the same input, and agreement, meaning κ
    against human labels. One phrase covering both would make later
    result statements ambiguous about which claim is being made.
    (c) "Reproduce" suggests that replication of human labels is itself the substantive goal. In this design, human labels serve as the reference standard against which agreement is measured.

  - v4 (2026-08-29) current wording — settled. Reached in two
    steps within the same session. An intermediate draft, "How does
    removing specific components of a coding manual affect an LLM's
    agreement with human dialogue coding?", replaced v2's "how
    sensitive" with a change question but inherited "removing" from
    v2. Three further changes were then made to that draft.
    (a) "Removing" was replaced by "replacing ... with placeholders", so that the RQ names the operation actually performed (see v2 (b)). Naming the inserted material also reduces the possibility of reading the observed change as an effect of the component's absence itself, which would move the interpretation back toward the contribution framing rejected in v1.
    (b) "Change" replaced "affect". Both verbs can carry causal
    implications; "change" was judged at the time to state the
    manipulation–outcome relation with less causal force. The level
    of causal claim supported by the design is recorded under Scope
    of claims (1.2).

## 1.2 Scope of claims

### 1.2.1 Level of causal claim
- Status: settled (2026-08-29)
- Decision: The study belongs to the research-tool pathway
  (functional claims about an LLM's agreement with human coding),
  and additionally falls under the exception for experiments on
  the tool itself: it manipulates the prompt (placeholder
  replacement of manual components) and measures the resulting
  change in agreement (Δκ). Causal claims are therefore restricted to the effect of the implemented manipulation on agreement.
- Boundary: No causal claim is made about anything not
  manipulated. The independent causal effect of a component, or a
  component's intrinsic importance, is outside the claim.
- Rationale: The same utterances are evaluated under every condition, allowing within-item comparison. Placeholder replacement is designed to preserve token length and downstream position, while the remaining prompt architecture is held constant.

### 1.2.2 No mechanism claims
- Status: settled (2026-08-24)
- Decision: Agreement is a claim about outputs only. High κ is not
  taken as evidence that the LLM and human coders share a process,
  and Δκ is not taken as evidence about what the LLM understands
  or what human coders relied on.
- Rationale: The data contain human labels and LLM labels. Neither
  the human coders' use of the manual nor the LLM's processing of
  it is observed, so neither can appear as the subject of a result
  statement.

### 1.2.3 Position of the study
- Status: settled (2026-08-24)
- Decision: This is a methodological pre-study for a later
  human–AI interaction study, examining whether LLM-assisted coding
  can be used there. It is not a pilot of that later study's
  research question.
- Boundary: Results on TalkMoves do not generalize to the later study's coding manual. The transferable methodological premise is that a manual developed for human coders should not be assumed, without validation, to function equivalently when used as an LLM prompt.
- Rationale: TalkMoves was chosen as the test site because it
  provides both a manual written for human coders and human-coded
  labels produced with that manual.