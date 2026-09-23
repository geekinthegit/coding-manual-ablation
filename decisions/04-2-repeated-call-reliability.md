## 4.2 Repeated-call reliability

[decided 2026-09-24; proposed 2026-09-17; the reporting additions in 4.2.5 were decided 2026-09-19]

This section defines the descriptive indicators used to report the stability of repeated calls under the repetition and aggregation procedure in 5.4. All indicators are reported per condition as descriptive statistics only. No inferential test, interval, or between-condition contrast is computed on them, and they are not part of the primary estimand (Δκ). Their role is to document how the final labels were produced, so that agreement results can be read together with the observed stability of the label-generation procedure.

Terms follow 5.4: "item" means one item-condition, "valid repeat" means a repeat with a valid label under 5.4.5, and "final label" means the plurality label under 5.4.2–5.4.3.

### 4.2.1 Unanimity rate

The proportion of items in which all R valid repeats carry the same label. The denominator is the number of items that have all R = 3 planned repeats valid; items with any invalid repeat are excluded from this indicator and are counted under 4.2.4 or reported separately. Among items in this denominator, those requiring tie-break calls have three valid but non-identical repeats and count as non-unanimous. A tie among only two valid initial repeats (5.4.8) is outside this denominator. The planned repeats are the initial repeats 1–3 (added 2026-09-22): tie-break calls (repeats 4 and 5) are not part of this denominator or numerator, consistent with the initial-pattern reporting in 4.2.5.

### 4.2.2 Mean agreement with the final label

For each item that has a final label, the ratio (number of valid repeats whose label equals the final label) / (number of valid repeats), where valid repeats include any tie-break calls under 5.4.3. The indicator is the mean of this item-level ratio over all items with a final label.

### 4.2.3 Ties and additional calls

The number of items in which a tie occurred under 5.4.3, and the total number of additional tie-break calls made. Both are reported per condition. An item counts as having a tie when a repeat 4 exists for it in `labels.csv` (added 2026-09-22), which covers both the three-way 1/1/1 case and the two-valid-repeat 1/1 case of 5.4.8; the additional-call count is the number of distinct (item, repeat) pairs with repeat 4 or 5 in `labels.csv`, exhausted or not, since that file has one row per attempt and a logical call is a repeat (4.2.5).

### 4.2.4 Items without a final label

The number of items that received no final label, broken down by reason: `unresolved tie` (5.4.3) and `insufficient valid repeats` (5.4.8). Reported per condition, consistent with the completeness report under roadmap step 15.

### 4.2.5 Additional descriptive reporting

[decided 2026-09-19] Retain 4.2.1–4.2.4 and their descriptive-only scope; this addition does not promote their proposed status or change the aggregation procedure (status at 2026-09-19; promoted to [decided] 2026-09-24 at the protocol freeze).

Per condition, report the number of item-conditions with all three initial valid labels and, within that denominator, counts and percentages of 3/3, 2/1, and 1/1/1 patterns. Report items lacking all three initial valid labels separately; an invalid response is not a substantive disagreement category. If the denominator is zero, report the count and mark percentages as unavailable.

Report counts requiring the fourth and fifth logical calls separately, alongside the existing total additional-call count and terminal unresolved-tie/insufficient-valid-repeat counts. Logical calls are repeats, not attempts: exhausted tie-break calls still consume a repeat under 5.4.3. Use `labels.csv` and execution records under 5.6.8 for initial patterns and call history; `final_labels.csv` alone does not contain the initial patterns. These are descriptive diagnostics, not new inferential contrasts. Analysis-set completeness and agreement diagnostics are specified in [6.1.2 and 6.5](06-analysis.md).
