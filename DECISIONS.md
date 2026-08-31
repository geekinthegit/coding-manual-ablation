# Decision Log

## 1. Research Question
### 1.1 RQ wording
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
### 1.2 Scope of claims

## 2. Data
### 2.1 Dataset selection and scope
### 2.2 Train/test split

## 3. Manipulation
### 3.1 Placeholder substitution
### 3.2 Filler text specification
### 3.3 Condition structure

## 4. Measurement
### 4.1 Context window
### 4.2 Temperature and call unit
### 4.3 Repetition count

## 5. Procedure
### 5.1 Role of the pilot
### 5.2 Negative control

## 6. Analysis
### 6.1 Uncertainty estimation for Δκ

## 7. Interpretive Boundaries
### 7.1 Underdetermined causes of near-zero Δκ
### 7.2 Direction of in-sample bias

## 8. Repository
### 8.1 Name, local folder, data exclusion