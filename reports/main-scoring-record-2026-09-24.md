# Main scoring record (Roadmap 16)

Scoring executed on 2026-09-24 (source: Roadmap 16-1 original execution report, Section 2).

Record written on 2026-09-25.

Values are rounded for display only; calculations use the unrounded values in score_summary.json.

## 1. Scope

Main-study scoring of run `main-2026-09-24`: 300 utterances, 6 conditions. Held-out evaluation was omitted by a post-freeze decision recorded before scoring: commit `112b4ea`, `reports/heldout-evaluation-decision-2026-09-24.md:10–19`.

The main sample was drawn from the main-experiment sampling frame of 150,627 utterances, which is the eligible target population of 150,644 utterances minus the 17 development targets D, excluded at the target level only. (02-3:13)

"The study's results refer to the development-set eligible target population defined in 2.1.2 and 2.3; no held-out result will be reported." (`reports/heldout-evaluation-decision-2026-09-24.md:19`.)

## 2. Provenance

Input seal commit: `8c6b46c`. Scoring execution commit: `c56ed3327fdaef7302d61328a06edcfb568f5cf3` (`c56ed33`). Script commit in `score_report.txt:3`: `c56ed3327fdaef7302d61328a06edcfb568f5cf3`.

The Roadmap 16-0 original report, Sections 1 and 8, confirmed that the changes from the input seal to the execution HEAD were documentation-only, with scoring code, sealed snapshots and main analysis rules unchanged. Roadmap 16-0 was the scoring-entry eligibility audit, concluding `READY FOR MAIN SCORING`; it was not the main scoring execution. Roadmap 16-1 separately checked the execution shell and ran `score_run.py` exactly once. Sources: the original Roadmap 16-0 and 16-1 reports in this Codex conversation; seal evidence in `reports/completeness-report-2026-09-24.md:111–120` and the history of commit `8c6b46c`.

Line citations in this record refer to repository files at commit `c56ed33`. Among the cited decision documents, only `decisions/02-3-sampling-design.md` differs from its frozen version at `ed13ec2`; the difference is the post-freeze Revision note recorded in `reports/protocol-freeze-record-2026-09-24.md`, which shifts the line numbers after line 13 by two. The text of the cited lines is identical in both versions.

## 3. Environment

Python 3.13.9; NumPy 2.3.5 — `score_report.txt:10–11`, JSON `header.python_version`, `header.numpy_version`. NumPy version and upgrade freeze: `decisions/05-2-model-and-api-parameters.md:95,98`.

pandas 2.3.3 — observed by Codex in the Roadmap 16-1 execution shell; not recorded in the scorer output header. Source: Roadmap 16-1 original execution report, Section 1.

Bootstrap: 10,000 replicates, seed 20260919, 95% pointwise percentile intervals. Specification source: `decisions/06-analysis.md:33`; recorded parameters: JSON `header.n_replicates`, `header.seed` and `score_report.txt:10`. Method (`decisions/06-analysis.md:33`): "Use paired utterance-level bootstrap with two-sided 95% pointwise percentile intervals (2.5th and 97.5th percentiles), 10,000 replicates, and bootstrap seed 20260919." Resampling unit (`decisions/06-analysis.md:61`): "Retain paired utterance-level resampling and the decision against transcript cluster resampling in 2.3.7." Uncertainty scope (`decisions/06-analysis.md:63`): "The bootstrap approximates sampling uncertainty for κ and Δκ from the observed utterance/final-label records under the stipulated sampling and execution assumptions. Those records include realized stochastic outputs, but this procedure does not separately estimate variability from rerunning the API on the same 300 utterances. It is not evidence that the same final labels or Δκ would reproduce under a complete rerun."

## 4. Command and execution

Source: Roadmap 16-1 original execution report, Sections 1–2.

```text
command: python scripts/score_run.py --run-id main-2026-09-24
start: 2026-09-24T18:30:04+09:00
end: 2026-09-24T18:30:11+09:00
exit code: 0
stdout:
wrote <local path>/runs/main-2026-09-24/score_report.txt
wrote <local path>/runs/main-2026-09-24/score_summary.json
stderr: no output
git status --porcelain immediately after execution: no output
```

Both output files were absent before execution. The command was executed exactly once; it was not rerun. Header generation time: `2026-09-24T09:30:11+00:00` (JSON `header.generated_at`; `score_report.txt:2`). No scoring, parser, runner, repeated-call diagnostic or bootstrap computation was rerun to draft this record.

## 5. Input hashes

Input file set: 10 files — seven canonical run artifacts, two archival snapshots, and one human-reference file. This is the set in the Roadmap 16-0 original report Sections 2–3 and Roadmap 16-2 original report Section 2; it matches the candidate set in the Roadmap 16-6 request. The snapshots are archival; the scorer reads the canonical run directory. `prompts.jsonl` is provenance rather than a direct scoring input. Sources: `reports/main-run-record-2026-09-24.md:171–177`; `reports/completeness-report-2026-09-24.md:92–93,103–118`.

Sizes and SHA-256 values were checked when drafting this record. The human-reference file was accessed only for filesystem size and `shasum -a 256`; its label values were not opened.

| File | Size (B) | SHA-256 | Matches recorded value |
| --- | --- | --- | --- |
| runs/main-2026-09-24/manifest_pass1.json | 601435 | faabb4a6c5480bd39f9955b1ea5cb9f746692712ae27cd30ed202855cf528abf | yes |
| runs/main-2026-09-24/manifest_pass2.json | 1848 | 065c7ed568544fc14d10005fb6cc7ae8b670ca56b9b8437f4e90dacf7775a308 | yes |
| runs/main-2026-09-24/prompts.jsonl | 14358858 | 4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140 | yes |
| runs/main-2026-09-24/attempts_pass1.jsonl | 14426505 | c47cc626556ba42af810694c3cab1469b5b116782ce1be62bf8ba69c6e730cbe | yes |
| runs/main-2026-09-24/attempts_pass2.jsonl | 2635 | 374113a1aad2a483724e325b5de3824db59efbce9c34200dbad407790ddc4fb6 | yes |
| runs/main-2026-09-24/labels.csv | 365089 | 13bbc66526a1c686a96eb33f08a20217fa73f25e5dba5e6485d5617a0cfbe5d1 | yes |
| runs/main-2026-09-24/final_labels.csv | 125338 | c1e7af7cc1ec3b3608b40218ab67cc37305f4bc99580821eed696c16bfd24110 | yes |
| analysis-inputs/main-2026-09-24/labels.csv | 365089 | 13bbc66526a1c686a96eb33f08a20217fa73f25e5dba5e6485d5617a0cfbe5d1 | yes |
| analysis-inputs/main-2026-09-24/final_labels.csv | 125338 | c1e7af7cc1ec3b3608b40218ab67cc37305f4bc99580821eed696c16bfd24110 | yes |
| data/scoring_labels.csv | 2269412 | 44e95948c340184e204856bda7d7c56cc17b1b7e7ba9ae8eb3f9f6b583340e58 | yes |

All three input hashes in the raw report header and JSON `header.final_labels_sha256`, `header.labels_sha256`, `header.scoring_labels_sha256` match the corresponding current file hashes above.

## 6. Raw output hashes

| File | Size (B) | SHA-256 | Matches Roadmap 16-1 |
| --- | --- | --- | --- |
| runs/main-2026-09-24/score_report.txt | 11859 | 38df8b28e298eb94037d4c82bdffd55256eda2ca3bc90053c4c88883b68804c9 | yes |
| runs/main-2026-09-24/score_summary.json | 24732 | 89d1ac844326bb5a395cb8021e332acf1a6b4474a6311a939be0b69d71a2cef8 | yes |

The canonical raw outputs remain only under `runs/main-2026-09-24/` and are git-ignored (`git check-ignore` confirmed both paths). They were not copied, sanitized, modified or regenerated. Before drafting, `git grep` found neither output hash in tracked files. This record is the sole repository record intended for version control of these two output hashes; at drafting it is a new, untracked file and has not been committed. Earlier hash reports are in the Codex conversation.

## 7. Integrity checks

| Stage | Recorded result | Source |
| --- | --- | --- |
| 16-0 | READY FOR MAIN SCORING; preflight only. Existing tests: 169 passed. | Original Codex 16-0 report, Sections 6 and 8 |
| 16-1 | Exactly one scoring execution; exit 0. Seven canonical artifacts and two snapshots unchanged before/after execution (9 files). | Original Codex 16-1 report, Sections 2 and 4 |
| 16-2 | SCORING OUTPUT INTEGRITY VERIFIED; 245 metadata/structure/report–JSON checks, including 18 interval structures; mismatch count 0. Text comparison respected four-decimal display formatting. | Original Codex 16-2 report, Sections 5–6 and 8 |
| 16-3 | POINT ESTIMATES INDEPENDENTLY VERIFIED; Fraction-based standard-library calculation without scorer, score_run, tags, bootstrap or other repository module imports; 18 point estimates and 10 n fields, mismatch count 0, maximum absolute difference 3.5344990823027445e-17 (tolerance 1e-12). Bootstrap CIs were not recalculated. | Original Codex 16-3 report, Sections 3–7 |

The original Codex reports cited above are the preceding reports in this conversation, not committed repository reports. They were consulted directly for this record.

Bootstrap implementation test evidence: `tests/test_scorer_bootstrap.py`, added in commit `df0963f` (confirmed by `git log --diff-filter=A` and `git show --stat`). The file covers undefined replicates and withholding (lines 40–79), degenerate intervals (83–118), shared draws (124–141), reproducibility and the specified generator expression (144–159), and varying paired n (162–170). These are synthetic tests. Their historical passing status is recorded in `decisions/06-analysis.md:79`; the 16-0 report records 169 suite tests passing. No tests were rerun during 16-6.

Claude Code boundary checks 16-5a and 16-5b are uncommitted reports. Their conclusions were `BOUNDARY CHECK COMPLETE; CONFLICTS LISTED` and `SUPPLEMENTARY CHECK COMPLETE; CONFLICTS LISTED`. Conflicts were resolved by Jiwon and incorporated into the Section 12 wording. Source: Jiwon’s supplied Roadmap 16-6 request, Section 4.7; these statements are attributed to that supplied account, not to an independently opened copy of those reports.

The Claude Code source check is also an uncommitted report. Its conclusion was `SOURCE CHECK COMPLETE; MISMATCHES OR MISSING SOURCES LISTED`. As supplied by Jiwon, hashes, header and result values matched the raw sources; the listed mismatches or missing sources concerned the bootstrap-seed source location (`decisions/06-analysis.md:33`), absence of a repository record of pandas at scoring time, and absence of a tracked output-hash record. Source: the same Roadmap 16-6 request, Section 4.7.

## 8. Standalone results

Ordinary unweighted Cohen’s κ; all intervals are 95% pointwise percentile intervals. Sources: JSON `standalone.<condition>.{n,kappa,interval}`; specification `decisions/06-analysis.md:17,33,49–57,75`.

| Condition | Analysis n | κ | 95% CI | Undefined / replicates | Undefined proportion | Degenerate |
| --- | --- | --- | --- | --- | --- | --- |
| baseline | 300 | 0.6085 | [0.5266, 0.6846] | 0 / 10000 | 0.0000 | false |
| definition_replacement | 300 | 0.6067 | [0.5252, 0.6824] | 0 / 10000 | 0.0000 | false |
| example_replacement | 300 | 0.5473 | [0.4658, 0.6239] | 0 / 10000 | 0.0000 | false |
| exclusion_rule_replacement | 300 | 0.5023 | [0.4244, 0.5767] | 0 / 10000 | 0.0000 | false |
| negative_control | 300 | 0.5852 | [0.5060, 0.6605] | 0 / 10000 | 0.0000 | false |
| names_only | 300 | 0.2727 | [0.1971, 0.3475] | 0 / 10000 | 0.0000 | false |

Names-only reporting wording is recorded verbatim as R2 in Section 12; its per-condition descriptive diagnostics are included in Sections 10–11.

## 9. Paired Δκ results

The paired-set baseline κ is computed on the same paired set as its condition κ; it is distinct in definition from the standalone baseline κ in Section 8. Δκ = κ_replacement − κ_baseline. Negative control is included alongside the substantive contrasts as context. Sources: JSON `paired.<condition>`; `decisions/06-analysis.md:21,25,33,75`.

| Condition vs baseline | Original n | Paired n | Both | Baseline only | Condition only | Neither | Discordant final labels |
| --- | --- | --- | --- | --- | --- | --- | --- |
| definition_replacement | 300 | 300 | 300 | 0 | 0 | 0 | 16 |
| example_replacement | 300 | 300 | 300 | 0 | 0 | 0 | 24 |
| exclusion_rule_replacement | 300 | 300 | 300 | 0 | 0 | 0 | 39 |
| negative_control | 300 | 300 | 300 | 0 | 0 | 0 | 16 |

| Condition vs baseline | Baseline unresolved_tie | Baseline insufficient_valid_repeats | Condition unresolved_tie | Condition insufficient_valid_repeats |
| --- | --- | --- | --- | --- |
| definition_replacement | 0 | 0 | 0 | 0 |
| example_replacement | 0 | 0 | 0 | 0 |
| exclusion_rule_replacement | 0 | 0 | 0 | 0 |
| negative_control | 0 | 0 | 0 | 0 |

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

Missing records are retained in reports/completeness-report-2026-09-24.md (Roadmap 15).

Conditional reporting: observed-paired-set limitation due to missing final labels — not applicable (0 cases); undefined original κ/Δκ requiring `not estimable` — not applicable (0 cases); CI withholding — not applicable (0 cases); degenerate intervals, including [0, 0] — not applicable (0 cases). Undefined counts and proportions for all 18 bootstrap statistics are explicitly reported in Sections 8–9.

Zero-discordance cases: not applicable (0 cases). A limited-resolution assessment field is not present in score_summary.json. `decisions/02-3-sampling-design.md:35` requires a note for zero or very small discordant counts but does not specify a numerical cutoff for “very small”; no new cutoff or classification is introduced in this record. The recorded discordant counts are shown for all four contrasts.

## 10. Repeated-call diagnostics

Sources: JSON `repeat_diagnostics.<condition>`; definitions and denominators in `decisions/04-2-repeated-call-reliability.md:5,11,15,19,23,29,31`. Shares below are the stored proportions, displayed to four decimal places; no denominator-zero case occurs.

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

Denominator-zero reporting (`unavailable`): not applicable (0 cases). Calls in the tables are logical calls (repeats), not attempts.

## 11. Descriptive diagnostics

Sources: JSON `standalone.<condition>.{n,agree,p_o,p_e}` and `marginals_confusion.<condition>.{n,categories,human_marginal,predicted_marginal,confusion}`; reporting specification `decisions/06-analysis.md:73`. Marginal distributions are reported as stored category counts with the analysis n; no additional proportions or statistics were calculated.

| Condition | Analysis n | Exact agreement count | P_o | P_e |
| --- | --- | --- | --- | --- |
| baseline | 300 | 236 | 0.7867 | 0.4551 |
| definition_replacement | 300 | 235 | 0.7833 | 0.4492 |
| example_replacement | 300 | 223 | 0.7433 | 0.4330 |
| exclusion_rule_replacement | 300 | 209 | 0.6967 | 0.3906 |
| negative_control | 300 | 230 | 0.7667 | 0.4374 |
| names_only | 300 | 167 | 0.5567 | 0.3904 |

### baseline — analysis n = 300

| Category | Human marginal count | Predicted marginal count |
| --- | --- | --- |
| Not coded | 207 | 179 |
| Keeping Everyone Together | 41 | 46 |
| Getting Students to Relate | 1 | 2 |
| Restating | 2 | 4 |
| Revoicing | 4 | 13 |
| Pressing for Accuracy | 42 | 46 |
| Pressing for Reasoning | 3 | 10 |

Confusion matrix: rows = human category; columns = predicted category. Category order is the stored canonical order.

| Human / predicted | Not coded | Keeping Everyone Together | Getting Students to Relate | Restating | Revoicing | Pressing for Accuracy | Pressing for Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Not coded | 171 | 20 | 1 | 0 | 6 | 7 | 2 |
| Keeping Everyone Together | 7 | 22 | 1 | 1 | 4 | 4 | 2 |
| Getting Students to Relate | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Restating | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| Revoicing | 0 | 0 | 0 | 1 | 3 | 0 | 0 |
| Pressing for Accuracy | 1 | 3 | 0 | 0 | 0 | 35 | 3 |
| Pressing for Reasoning | 0 | 0 | 0 | 0 | 0 | 0 | 3 |

### definition_replacement — analysis n = 300

| Category | Human marginal count | Predicted marginal count |
| --- | --- | --- |
| Not coded | 207 | 176 |
| Keeping Everyone Together | 41 | 45 |
| Getting Students to Relate | 1 | 3 |
| Restating | 2 | 7 |
| Revoicing | 4 | 13 |
| Pressing for Accuracy | 42 | 49 |
| Pressing for Reasoning | 3 | 7 |

Confusion matrix: rows = human category; columns = predicted category. Category order is the stored canonical order.

| Human / predicted | Not coded | Keeping Everyone Together | Getting Students to Relate | Restating | Revoicing | Pressing for Accuracy | Pressing for Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Not coded | 168 | 18 | 2 | 1 | 8 | 8 | 2 |
| Keeping Everyone Together | 7 | 23 | 1 | 3 | 2 | 5 | 0 |
| Getting Students to Relate | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Restating | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| Revoicing | 0 | 0 | 0 | 1 | 3 | 0 | 0 |
| Pressing for Accuracy | 1 | 3 | 0 | 0 | 0 | 36 | 2 |
| Pressing for Reasoning | 0 | 0 | 0 | 0 | 0 | 0 | 3 |

### example_replacement — analysis n = 300

| Category | Human marginal count | Predicted marginal count |
| --- | --- | --- |
| Not coded | 207 | 169 |
| Keeping Everyone Together | 41 | 48 |
| Getting Students to Relate | 1 | 1 |
| Restating | 2 | 4 |
| Revoicing | 4 | 19 |
| Pressing for Accuracy | 42 | 45 |
| Pressing for Reasoning | 3 | 14 |

Confusion matrix: rows = human category; columns = predicted category. Category order is the stored canonical order.

| Human / predicted | Not coded | Keeping Everyone Together | Getting Students to Relate | Restating | Revoicing | Pressing for Accuracy | Pressing for Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Not coded | 162 | 25 | 1 | 1 | 10 | 4 | 4 |
| Keeping Everyone Together | 6 | 19 | 0 | 1 | 5 | 8 | 2 |
| Getting Students to Relate | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Restating | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| Revoicing | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| Pressing for Accuracy | 1 | 3 | 0 | 0 | 0 | 33 | 5 |
| Pressing for Reasoning | 0 | 0 | 0 | 0 | 0 | 0 | 3 |

### exclusion_rule_replacement — analysis n = 300

| Category | Human marginal count | Predicted marginal count |
| --- | --- | --- |
| Not coded | 207 | 146 |
| Keeping Everyone Together | 41 | 67 |
| Getting Students to Relate | 1 | 3 |
| Restating | 2 | 4 |
| Revoicing | 4 | 19 |
| Pressing for Accuracy | 42 | 49 |
| Pressing for Reasoning | 3 | 12 |

Confusion matrix: rows = human category; columns = predicted category. Category order is the stored canonical order.

| Human / predicted | Not coded | Keeping Everyone Together | Getting Students to Relate | Restating | Revoicing | Pressing for Accuracy | Pressing for Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Not coded | 141 | 40 | 1 | 1 | 10 | 11 | 3 |
| Keeping Everyone Together | 4 | 24 | 1 | 1 | 5 | 4 | 2 |
| Getting Students to Relate | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| Restating | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| Revoicing | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| Pressing for Accuracy | 1 | 3 | 0 | 0 | 0 | 34 | 4 |
| Pressing for Reasoning | 0 | 0 | 0 | 0 | 0 | 0 | 3 |

### negative_control — analysis n = 300

| Category | Human marginal count | Predicted marginal count |
| --- | --- | --- |
| Not coded | 207 | 171 |
| Keeping Everyone Together | 41 | 52 |
| Getting Students to Relate | 1 | 2 |
| Restating | 2 | 4 |
| Revoicing | 4 | 18 |
| Pressing for Accuracy | 42 | 41 |
| Pressing for Reasoning | 3 | 12 |

Confusion matrix: rows = human category; columns = predicted category. Category order is the stored canonical order.

| Human / predicted | Not coded | Keeping Everyone Together | Getting Students to Relate | Restating | Revoicing | Pressing for Accuracy | Pressing for Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Not coded | 165 | 25 | 1 | 0 | 9 | 5 | 2 |
| Keeping Everyone Together | 5 | 23 | 1 | 2 | 5 | 3 | 2 |
| Getting Students to Relate | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Restating | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| Revoicing | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| Pressing for Accuracy | 1 | 3 | 0 | 0 | 0 | 33 | 5 |
| Pressing for Reasoning | 0 | 0 | 0 | 0 | 0 | 0 | 3 |

### names_only — analysis n = 300

| Category | Human marginal count | Predicted marginal count |
| --- | --- | --- |
| Not coded | 207 | 150 |
| Keeping Everyone Together | 41 | 65 |
| Getting Students to Relate | 1 | 7 |
| Restating | 2 | 30 |
| Revoicing | 4 | 3 |
| Pressing for Accuracy | 42 | 31 |
| Pressing for Reasoning | 3 | 14 |

Confusion matrix: rows = human category; columns = predicted category. Category order is the stored canonical order.

| Human / predicted | Not coded | Keeping Everyone Together | Getting Students to Relate | Restating | Revoicing | Pressing for Accuracy | Pressing for Reasoning |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Not coded | 131 | 39 | 5 | 18 | 1 | 10 | 3 |
| Keeping Everyone Together | 10 | 15 | 2 | 5 | 1 | 6 | 2 |
| Getting Students to Relate | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Restating | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| Revoicing | 0 | 0 | 0 | 3 | 1 | 0 | 0 |
| Pressing for Accuracy | 9 | 10 | 0 | 2 | 0 | 15 | 6 |
| Pressing for Reasoning | 0 | 0 | 0 | 0 | 0 | 0 | 3 |

## 12. Interpretation boundaries

Citation abbreviations below refer to `decisions/`: `01-research-question.md`; `03-1` = `03-1-manual-component-definition.md`; `03-3` = `03-3-names-only-diagnostic.md`; `02-3` = `02-3-sampling-design.md`; `04-2` = `04-2-repeated-call-reliability.md`; `06` = `06-analysis.md`. All specified source lines were reopened during drafting. C1/C2 were checked against the unrounded JSON delta values and interval bounds. The following wording is supplied by Jiwon in the Roadmap 16-6 request, Section 8.

### Prespecified boundaries

- C1. Under the implemented replacement procedure, agreement with the human labels was lower than the paired-set baseline in the example-replacement and exclusion-rule-replacement conditions: the baseline-referenced Δκ and its 95% interval were both below zero in each. The causal claim is restricted to the effect of the implemented manipulation on agreement. (01-research-question.md:73; 03-1:144, :146)

- C2. For definition replacement and the negative control, the 95% interval for Δκ includes zero. No direction or magnitude is claimed, and this is not interpreted as evidence of no effect, maintained agreement, or equivalence between the baseline and replacement conditions. A small or uncertain negative-control Δκ does not establish general filler neutrality. (03-1:146, :150)

- R1. All prespecified estimates and intervals are reported (Sections 8–11).

- R2. Names-only is reported with its standalone descriptive κ, its 95% interval, and the per-condition descriptive diagnostics; no baseline-referenced Δκ and no inferential contrast with the experimental conditions is made. It is reported as agreement obtained under the names-only reference prompt, with no substantive manual text supplied in the request, not as agreement produced using only category names. It is not a chance baseline or a lower bound, and prior model exposure to TalkMoves or related material remains possible. No "close to names-only" or "clearly above names-only" rules are used. (06:21, :75; 03-3:5, :11, :13)

- R3. No direct contrast between substantive conditions was performed. Each interval is an individual-statistic interval referenced to the paired-set baseline, not simultaneous coverage across contrasts. No multiplicity adjustment is specified in decisions/06-analysis.md. (06:27, :33, :69)

- R4. Confusion matrices, marginals, and raw agreement are descriptive only. No inferential claim is made about category-specific effects, and no baseline-to-replacement transition analysis is added. (02-3:31; 06:73)

- R5. No claim is made about mechanisms, which information the model used, what the human coders relied on, a component's independent contribution or intrinsic importance, whether a replaced component is necessary, equivalence, or noninferiority. (01-research-question.md:74–88; 03-1:148, :152, :154)

- R6. The negative control replaces background text judged task-irrelevant and is much smaller in volume than the substantive replacements. Its κ, Δκ, and interval are reported alongside the substantive Δκ estimates as context. It is not subtracted from those estimates, not used to adjust them, and not used as a pass/fail criterion. Its interpretation is limited to the specific passage replaced, the amount and location of filler, and the execution conditions used. A change in agreement in the control does not by itself invalidate the substantive replacement results. (03-1:150, :152; 06:75)

- R7. Each condition's estimated change in agreement is interpreted in light of the residual manual information recorded for that condition under 3.1.7, including label semantics, redundancy among manual components, and other possible routes to agreement. (03-1:130, :148)

- U6. Repeated-call indicators are reported per condition as descriptive statistics only; no inferential test, interval, or between-condition contrast is computed on them, and they are not part of the primary estimand. An invalid response is not a substantive disagreement category. Logical calls are repeats, not attempts. (04-2:5, :29, :31)

- U11. The main sample was drawn from the main-experiment sampling frame of 150,627 utterances, which is the eligible target population of 150,644 utterances minus the 17 development targets D, excluded at the target level only. (02-3:13) "The study's results refer to the development-set eligible target population defined in 2.1.2 and 2.3; no held-out result will be reported." (reports/heldout-evaluation-decision-2026-09-24.md:19)

### Post-result reporting restriction

- P1. Post-result reporting restriction added at 16-4: Δκ is not interpreted as a percentage-point change in accuracy.

## 13. AI/tool division of labor

Source: the original Codex stage reports for 16-0–16-4 and Jiwon’s supplied Roadmap 16-6 request, Section 4.13, for the subsequent assignments and cross-review roles.

| Stage / role | Responsible party |
| --- | --- |
| 16-0 preflight; 16-1 execution; 16-2 integrity check; 16-3 independent recomputation; 16-4 result report | Codex |
| 16-4 interpretation decisions | Jiwon |
| 16-5a, 16-5b boundary checks and source check | Claude Code |
| Cross-review of prompts and reports | Claude (claude.ai project chat) |
| 16-6 record drafting | Codex |
| 16-8 commit | Jiwon (assigned; not performed in 16-6) |

Roadmap 16-7: independent audit performed by Claude Code on the draft of this record (sha256 5ab80308cd3f30cabee9447ade72715cb7058f91d2c140f5f3b6e5da4c551182); post-audit revisions were verified by Claude Code (sha256 f922aff22371558b8862cd075c4681a4ded3206cbb9b12c7003e1ca3c5ed15a6); result: READY TO COMMIT. The only change after that verification is this sentence.

## Appendix A. Extraction procedure

Values were programmatically extracted from score_summary.json; no manual transcription.

An inline `python -B - <<'PY' ... PY` command used only the standard library (`json`, `pathlib`, `subprocess`, `re`, `hashlib`); no repository module was imported. It read the canonical JSON once, selected the key paths below, formatted κ/Δκ/interval bounds with `.4f`, retained integer counts, and assembled the Markdown tables in memory. C1/C2 sign and zero-inclusion checks used unrounded stored values. It did not recompute any point estimate, bootstrap interval, repeated-call indicator or confusion matrix. Only this record was written, using exclusive creation. The extraction code was not saved as a separate file.

Input/output sizes came from filesystem metadata; SHA-256 values came from `shasum -a 256`. The human-reference file was not parsed or displayed. After writing, every generated table was checked for exact inclusion in the record, the complete record bytes were compared with the in-memory extraction output, and the input/output hashes were checked again.

| Record section | JSON key paths used |
| --- | --- |
| 1–4 | header.run_id; header.n_records; header.git_commit; header.generated_at; header.python_version; header.numpy_version; header.n_replicates; header.seed |
| 5 | header.final_labels_sha256; header.labels_sha256; header.scoring_labels_sha256 |
| 8 | standalone.<condition>.n; .kappa; .interval.{lower,upper,n_replicates,undefined_count,undefined_proportion,withheld_reason,degenerate} |
| 9 | paired.<condition>.{original_n,paired_n,both,baseline_only,condition_only,neither,discordant}; .missing_baseline; .missing_condition; .baseline.{kappa,interval}; .condition.{kappa,interval}; .delta.{value,interval} |
| 10 | repeat_diagnostics.<condition>.{n_items,initial_valid_denominator,items_lacking_all_initial_valid,pattern_3_3,pattern_3_3_share,pattern_2_1,pattern_2_1_share,pattern_1_1_1,pattern_1_1_1_share,unanimity_rate,items_with_final_label,mean_agreement_with_final,items_with_tie,additional_calls_total,calls_repeat_4,calls_repeat_5,unresolved_tie,insufficient_valid_repeats} |
| 11 | standalone.<condition>.{n,agree,p_o,p_e}; marginals_confusion.<condition>.{n,categories,human_marginal,predicted_marginal,confusion} |
| 12 C1/C2 checks | paired.<condition>.delta.value; paired.<condition>.delta.interval.lower; paired.<condition>.delta.interval.upper |

