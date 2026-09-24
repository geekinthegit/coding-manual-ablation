# Completeness report: main-2026-09-24 (2026-09-24)

## 1. Scope and inputs

This report records the Roadmap 15 completeness verification of the main run. No scoring was performed, and no human label value was read. The model outputs read are the attempt records, `labels.csv` and `final_labels.csv` of the run; the checks report counts only.

| Item | Value |
| --- | --- |
| Repository HEAD at verification | `ba055e9443e9c0d683a95344125ccce12a0d91dd` |
| Execution commit (`manifest_pass1.json` `git_commit`) | `beb3ef984f1b8bd0ec73f7c9f96171f80cddf1eb` |
| `run_id` | `main-2026-09-24` |
| `samples/main_targets.csv` | sha256 `18ec7cd05b472fb26cbf64c983a9f84614a58dc26a7ec7f4f5b7329fd19553fe`, 300 rows, 300 unique `source_id` |
| Environment | Python 3.13.9, numpy 2.3.5, pandas 2.3.3 |

This report does not record the SHA of the commit that adds it or the hash of the freeze record.

## 2. Parser re-run and determinism

`python scripts/parse_attempts.py --run-id main-2026-09-24`: stdout `wrote …/labels.csv: 5401 attempt rows` / `wrote …/final_labels.csv: 1800 (utterance, condition) rows` / `resolved: 1800`; exit code 0. This is the last parser run of Roadmap 15.

| File | sha256 after this run | `reports/main-run-record-2026-09-24.md` §10 | Match |
| --- | --- | --- | --- |
| labels.csv | `13bbc66526a1c686a96eb33f08a20217fa73f25e5dba5e6485d5617a0cfbe5d1` | `13bbc66526a1c686a96eb33f08a20217fa73f25e5dba5e6485d5617a0cfbe5d1` | yes |
| final_labels.csv | `c1e7af7cc1ec3b3608b40218ab67cc37305f4bc99580821eed696c16bfd24110` | `c1e7af7cc1ec3b3608b40218ab67cc37305f4bc99580821eed696c16bfd24110` | yes |

## 3. Scorer precondition check

Function called: `scorer.require_run_complete(Path("runs/main-2026-09-24"))` (command in the Appendix). It returned `None` without an exception; exit code 0. The function checks pass layout, termination of every call of every present pass, byte identity of `final_labels.csv` with a fresh aggregation of the attempts files (written to a temporary directory), absence of `tie_pending` rows and one row per pass 1 (utterance_id, condition) pair. It does not read human labels. The sha256 of all seven files under `runs/main-2026-09-24/` was identical before and after the call.

## 4. Coverage

| Check | Result |
| --- | --- |
| `manifest_pass1.json` calls unique by (utterance_id, condition, repeat) | 5,400 calls, 5,400 unique |
| Manifest utterance set = `source_id` of `samples/main_targets.csv` | 300 = 300; 0 only in manifest, 0 only in the sample file |
| Condition set | Expected condition set from the prespecified `CONDITIONS` definition (`scripts/build_inputs.py:65-72`) = {baseline, definition_replacement, example_replacement, exclusion_rule_replacement, negative_control, names_only}. Observed condition set in `manifest_pass1` calls = {baseline, definition_replacement, example_replacement, exclusion_rule_replacement, names_only, negative_control}. Difference = 0 → PASS. |
| Calls per repeat | repeat 1: 1,800; repeat 2: 1,800; repeat 3: 1,800 |
| Calls = full 300 × 6 × 3 cross product | 0 missing, 0 extra |

All coverage checks: PASS.

## 5. Raw attempts → labels → final labels

| Check | Result |
| --- | --- |
| Exactly one `success` record per manifest call (pass, order_index), passes 1 and 2 | 5,401 manifest calls; 5,401 `attempt_completed` records; 5,401 calls with a success; 0 calls with a number of successes other than 1; 0 records whose (utterance_id, condition, repeat) differs from the manifest call |
| Success count = `labels.csv` rows | 5,401 = 5,401 |
| `labels.csv` (utterance_id, condition, repeat) unique | 5,401 rows, 5,401 unique |
| `labels.csv` `valid` | True 5,401; other 0 |
| `labels.csv` `category` = `category` in `raw_response` of the matching success record (all rows) | 5,401 compared; 0 mismatches; 0 keys on one side only |
| `labels.csv` pass 2 rows = `manifest_pass2.json` calls | 1 = 1 |
| `final_labels.csv` = 300 × 6 pairs, one row each | 1,800 rows; 1,800 unique pairs; 0 missing; 0 extra |
| `valid_repeats` = valid `labels.csv` rows of the pair | 0 mismatches |
| `repeats_used` = number and maximum of the pair's repeats | 0 mismatches |
| `final_label` empty ⇔ `status` ≠ `resolved` | 0 empty; 0 not resolved; 0 disagreeing rows |

All checks in this section: PASS.

## 6. Independent recomputation

Final label and status were recomputed for every (utterance_id, condition) pair from `labels.csv` by code that does not import `parse_attempts` or `scorer`, following only `decisions/05-4-repetition-and-label-aggregation.md` lines 21 (plurality label among valid repeats), 27 (tie: further call up to 5 repeats, then `unresolved tie`) and 80–83 (fewer than 2 valid repeats: `insufficient valid repeats`). Rule order applied: fewer than 2 valid repeats → `insufficient_valid_repeats`; a single label with the largest count → `resolved` with that label; a shared largest count with `repeats_used` < 5 → `tie_pending`; a shared largest count at 5 → `unresolved_tie`.

Result: 1,800 pairs compared with `final_labels.csv`, 0 mismatches in `final_label` or `status`. PASS.

## 7. Final-label status by condition and reason

`decisions/05-4-repetition-and-label-aggregation.md` line 85:

> An item-condition without a final label is never converted to `Not coded` and is never silently dropped from analysis. All such cases are reported, by condition and by reason, in the completeness report produced under roadmap step 15.

| Condition | resolved | tie_pending | unresolved_tie | insufficient_valid_repeats | Total |
| --- | --- | --- | --- | --- | --- |
| baseline | 300 | 0 | 0 | 0 | 300 |
| definition_replacement | 300 | 0 | 0 | 0 | 300 |
| example_replacement | 300 | 0 | 0 | 0 | 300 |
| exclusion_rule_replacement | 300 | 0 | 0 | 0 | 300 |
| names_only | 300 | 0 | 0 | 0 | 300 |
| negative_control | 300 | 0 | 0 | 0 | 300 |

## 8. Consequence for analysis

No missing final labels remain; the planned complete 300-item analysis set is available to the scorer.

`decisions/06-analysis.md` line 27:

> When missing labels remain, the intended complete 300-item primary analysis is incomplete. The prespecified paired complete-case result preserves pairing but does not recover the original finite-population estimand without additional missingness assumptions. Report it as the agreement difference on the observed paired set, with that limitation; do not silently redefine the population in 2.3.1. Different comparison-specific paired sets do not authorize a new contrast between Δκ estimates.

## 9. Human labels

| Item | `data/scoring_labels.csv` | `reports/protocol-freeze-record-2026-09-24.md` line 131 | Match |
| --- | --- | --- | --- |
| Size | 2,269,412 B | 2,269,412 B | yes |
| sha256 | `44e95948c340184e204856bda7d7c56cc17b1b7e7ba9ae8eb3f9f6b583340e58` | `44e95948c340184e204856bda7d7c56cc17b1b7e7ba9ae8eb3f9f6b583340e58` | yes |

Only the size and sha256 of the file were computed; its label values were not read. The human labels are read for the first time by the scorer in Roadmap 16.

## 10. Artifacts and hashes

(a) `runs/main-2026-09-24/`. These files are the canonical provenance of the run and are git-ignored (`.gitignore`: `runs/*`).

| File | Size | sha256 | Use by the scoring code |
| --- | --- | --- | --- |
| manifest_pass1.json | 601,435 B | `faabb4a6c5480bd39f9955b1ea5cb9f746692712ae27cd30ed202855cf528abf` | read (termination, coverage, utterance list) |
| manifest_pass2.json | 1,848 B | `065c7ed568544fc14d10005fb6cc7ae8b670ca56b9b8437f4e90dacf7775a308` | read (termination) |
| attempts_pass1.jsonl | 14,426,505 B | `c47cc626556ba42af810694c3cab1469b5b116782ce1be62bf8ba69c6e730cbe` | read (termination, re-aggregation) |
| attempts_pass2.jsonl | 2,635 B | `374113a1aad2a483724e325b5de3824db59efbce9c34200dbad407790ddc4fb6` | read (termination, re-aggregation) |
| labels.csv | 365,089 B | `13bbc66526a1c686a96eb33f08a20217fa73f25e5dba5e6485d5617a0cfbe5d1` | read (repeated-call diagnostics, report header hash) |
| final_labels.csv | 125,338 B | `c1e7af7cc1ec3b3608b40218ab67cc37305f4bc99580821eed696c16bfd24110` | read (analysis input) |
| prompts.jsonl | 14,358,858 B | `4b64c681a9744e37111e26ff00822799d592922f1744f70e5577b75aba1a5140` | not read (provenance artifact) |

(b) `analysis-inputs/main-2026-09-24/`, copied from `runs/main-2026-09-24/` after the parser run in section 2 (`cmp` reported no difference for either file):

| File | Size | sha256 |
| --- | --- | --- |
| labels.csv | 365,089 B | `13bbc66526a1c686a96eb33f08a20217fa73f25e5dba5e6485d5617a0cfbe5d1` |
| final_labels.csv | 125,338 B | `c1e7af7cc1ec3b3608b40218ab67cc37305f4bc99580821eed696c16bfd24110` |

This is a verbatim archival snapshot; the Roadmap 16 scorer reads runs/main-2026-09-24/, not this snapshot.

(c) From Roadmap 15-5 onward, the files under `runs/main-2026-09-24/` and the snapshot are not modified or regenerated. The temporary re-aggregation that the scorer performs for its checks is not a modification.

## Appendix. Verification code

Section 3, run from the repository root:

```
python -c 'import sys; sys.path.insert(0, "scripts"); from pathlib import Path; import scorer; print(scorer.require_run_complete(Path("runs/main-2026-09-24")))'
```

Sections 4–7, run from the repository root as a one-off script (not stored in the repository):

```python
"""One-off completeness checks for runs/main-2026-09-24 (Roadmap 15-3, step 5).

Run from the repository root. Imports only pandas, json and hashlib; does not
import parse_attempts or scorer. Reads model outputs only; human labels are
not read. Prints counts and PASS/FAIL per check; category names are never
printed.
"""
import hashlib
import json

import pandas as pd

RUN = "runs/main-2026-09-24"
TARGETS = "samples/main_targets.csv"
STATUSES = ["resolved", "tie_pending", "unresolved_tie", "insufficient_valid_repeats"]
MAX_REPEATS = 5        # 05-4:27
MIN_VALID = 2          # 05-4:80-83


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def read_csv(path):
    # Only the empty field is missing; no category or id string is turned into NaN.
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def report(name, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


m1 = json.load(open(f"{RUN}/manifest_pass1.json", encoding="utf-8"))
m2 = json.load(open(f"{RUN}/manifest_pass2.json", encoding="utf-8"))

# ---- 5.1 Coverage -------------------------------------------------------
calls1 = [(int(c["utterance_id"]), c["condition"], int(c["repeat"])) for c in m1["calls"]]
report("5.1a manifest_pass1 calls unique (utterance_id, condition, repeat)",
       len(calls1) == 5400 and len(set(calls1)) == 5400,
       f"calls {len(calls1)}, unique {len(set(calls1))}")
targets = read_csv(TARGETS)
target_ids = {int(x) for x in targets["source_id"]}
utts = {u for u, _, _ in calls1}
print(f"      {TARGETS} sha256 {sha256(TARGETS)}, rows {len(targets)}, unique source_id {len(target_ids)}")
report("5.1b manifest utterance set = samples/main_targets.csv source_id",
       utts == target_ids and len(utts) == 300,
       f"manifest {len(utts)}, targets {len(target_ids)}, only manifest {len(utts - target_ids)}, "
       f"only targets {len(target_ids - utts)}")
conds = sorted({c for _, c, _ in calls1})
report("5.1c condition set has 6 members", len(conds) == 6, f"{len(conds)} conditions: {conds}")
rep_counts = {r: sum(1 for _, _, rr in calls1 if rr == r) for r in sorted({r for _, _, r in calls1})}
report("5.1d repeats 1-3, 1,800 calls each", rep_counts == {1: 1800, 2: 1800, 3: 1800}, f"{rep_counts}")
full = {(u, c, r) for u in utts for c in conds for r in (1, 2, 3)}
report("5.1e calls = full 300 x 6 x 3 cross product", set(calls1) == full,
       f"missing {len(full - set(calls1))}, extra {len(set(calls1) - full)}")

# ---- 5.2 Raw attempts -> labels ------------------------------------------
manifest_calls = {}
for p, m in ((1, m1), (2, m2)):
    for c in m["calls"]:
        manifest_calls[(p, int(c["order_index"]))] = (int(c["utterance_id"]), c["condition"], int(c["repeat"]))
success = {}
n_completed = 0
bad_key = 0
for p in (1, 2):
    for rec in jsonl(f"{RUN}/attempts_pass{p}.jsonl"):
        if rec["event"] != "attempt_completed":
            continue
        n_completed += 1
        call = (rec["pass"], rec["order_index"])
        if manifest_calls.get(call) != (rec["utterance_id"], rec["condition"], rec["repeat"]):
            bad_key += 1
        if rec["outcome"] == "success":
            success.setdefault(call, []).append(rec)
per_call = {call: len(success.get(call, [])) for call in manifest_calls}
not_one = [call for call, n in per_call.items() if n != 1]
report("5.2a exactly one success per manifest call (pass, order_index)",
       not not_one and set(success) == set(manifest_calls) and bad_key == 0,
       f"manifest calls {len(manifest_calls)}, completed records {n_completed}, calls with success {len(success)}, "
       f"calls with != 1 success {len(not_one)}, records not matching manifest call {bad_key}")

labels = read_csv(f"{RUN}/labels.csv")
report("5.2b success count = labels.csv rows", sum(per_call.values()) == len(labels),
       f"success {sum(per_call.values())}, labels rows {len(labels)}")
lkey = list(zip(labels["utterance_id"].astype(int), labels["condition"], labels["repeat"].astype(int)))
report("5.2c labels.csv (utterance_id, condition, repeat) unique", len(set(lkey)) == len(lkey),
       f"rows {len(lkey)}, unique {len(set(lkey))}")
report("5.2d labels.csv valid all True", (labels["valid"] == "True").all(),
       f"True {(labels['valid'] == 'True').sum()}, other {(labels['valid'] != 'True').sum()}")

raw_cat = {}
for call, recs in success.items():
    rec = recs[0]
    content = json.loads(rec["raw_response"])["choices"][0]["message"]["content"]
    raw_cat[(rec["pass"], rec["utterance_id"], rec["condition"], rec["repeat"])] = json.loads(content)["category"].strip()
lab_cat = {(int(r["pass"]), int(r["utterance_id"]), r["condition"], int(r["repeat"])): r["category"]
           for _, r in labels.iterrows()}
mismatch = sum(1 for k in lab_cat if raw_cat.get(k) != lab_cat[k])
report("5.2e labels.csv category = raw_response category (all rows)",
       set(lab_cat) == set(raw_cat) and mismatch == 0,
       f"compared {len(lab_cat)}, mismatches {mismatch}, keys only in labels {len(set(lab_cat) - set(raw_cat))}, "
       f"keys only in raw {len(set(raw_cat) - set(lab_cat))}")
pass2_rows = {(int(r["utterance_id"]), r["condition"], int(r["repeat"]))
              for _, r in labels[labels["pass"] == "2"].iterrows()}
pass2_calls = {(int(c["utterance_id"]), c["condition"], int(c["repeat"])) for c in m2["calls"]}
report("5.2f labels.csv pass 2 rows = manifest_pass2 calls", pass2_rows == pass2_calls,
       f"pass 2 rows {len(pass2_rows)}, manifest_pass2 calls {len(pass2_calls)}")

# ---- 5.3 labels -> final_labels ------------------------------------------
final = read_csv(f"{RUN}/final_labels.csv")
fkey = list(zip(final["utterance_id"].astype(int), final["condition"]))
full_pairs = {(u, c) for u in utts for c in conds}
report("5.3a final_labels.csv = 300 x 6 pairs, one row each",
       len(final) == 1800 and len(set(fkey)) == len(fkey) and set(fkey) == full_pairs,
       f"rows {len(final)}, unique pairs {len(set(fkey))}, missing {len(full_pairs - set(fkey))}, "
       f"extra {len(set(fkey) - full_pairs)}")

by_pair = {}
for _, r in labels.iterrows():
    by_pair.setdefault((int(r["utterance_id"]), r["condition"]), []).append(r)
vr_bad = ru_bad = 0
for _, f in final.iterrows():
    rows = by_pair.get((int(f["utterance_id"]), f["condition"]), [])
    valid_n = sum(1 for r in rows if r["valid"] == "True")
    repeats = {int(r["repeat"]) for r in rows}
    if int(f["valid_repeats"]) != valid_n:
        vr_bad += 1
    if not repeats or int(f["repeats_used"]) != len(repeats) or int(f["repeats_used"]) != max(repeats):
        ru_bad += 1
report("5.3b valid_repeats = valid labels.csv rows of the pair", vr_bad == 0, f"mismatches {vr_bad}")
report("5.3c repeats_used = number (and maximum) of repeats of the pair", ru_bad == 0, f"mismatches {ru_bad}")
empty = final["final_label"] == ""
not_resolved = final["status"] != "resolved"
report("5.3d final_label empty <=> status != resolved", (empty == not_resolved).all(),
       f"empty {int(empty.sum())}, status != resolved {int(not_resolved.sum())}, "
       f"disagreeing rows {int((empty != not_resolved).sum())}")

# ---- 5.4 Independent recomputation (05-4:21, 27, 80-83) ------------------
diff = []
for _, f in final.iterrows():
    pair = (int(f["utterance_id"]), f["condition"])
    rows = by_pair.get(pair, [])
    counts = {}
    for r in rows:
        if r["valid"] == "True":
            counts[r["category"]] = counts.get(r["category"], 0) + 1
    repeats_used = max(int(r["repeat"]) for r in rows)
    if sum(counts.values()) < MIN_VALID:
        label, status = "", "insufficient_valid_repeats"
    else:
        top = max(counts.values())
        leaders = [k for k, v in counts.items() if v == top]
        if len(leaders) == 1:
            label, status = leaders[0], "resolved"
        elif repeats_used < MAX_REPEATS:
            label, status = "", "tie_pending"
        else:
            label, status = "", "unresolved_tie"
    if (label, status) != (f["final_label"], f["status"]):
        diff.append(pair)
report("5.4 recomputed final_label and status = final_labels.csv", not diff,
       f"compared {len(final)}, mismatches {len(diff)}" + (f", pairs {diff}" if diff else ""))

# ---- 5.5 Condition x status ----------------------------------------------
unknown = sorted(set(final["status"]) - set(STATUSES))
report("5.5 every status is one of the four", not unknown, f"unknown {unknown}")
print("condition | " + " | ".join(STATUSES) + " | total")
for c in conds:
    sub = final[final["condition"] == c]
    print(f"{c} | " + " | ".join(str(int((sub['status'] == s).sum())) for s in STATUSES) + f" | {len(sub)}")
```

Section 4, condition-set check (added in the Roadmap 15-3 addendum; source text read only, no `scripts/` module imported or executed), run from the repository root:

```
git grep -n "CONDITIONS" -- scripts/
sed -n '60,74p' scripts/build_inputs.py | nl -ba -v60
sed -n '30,40p' scripts/check_inputs.py | nl -ba -v30
python -c 'import json; e={"baseline","definition_replacement","example_replacement","exclusion_rule_replacement","negative_control","names_only"}; o={c["condition"] for c in json.load(open("runs/main-2026-09-24/manifest_pass1.json"))["calls"]}; print(sorted(o)); print("expected-observed", sorted(e-o), "observed-expected", sorted(o-e))'
```

`CONDITIONS` is defined only in `scripts/build_inputs.py` (lines 65–72); `scripts/check_inputs.py:35`, `scripts/repeat_diagnostics.py:23`, `scripts/run_experiment.py:53`, `scripts/score_run.py:37` and `scripts/scorer.py:34` import it from `build_inputs`.
