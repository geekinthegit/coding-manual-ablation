"""Scorer: run-completeness check (6.1.1) and point estimates of κ and Δκ (6.1, 6.2.2).

This module holds require_run_complete() and the point-estimate functions
make_table(), kappa(), standalone() and paired(). The bootstrap, the report,
the CLI and the reading of a run directory into a table are not implemented
here yet. Nothing under the run directory is written by this module.

What is reused, never re-implemented
------------------------------------
* Termination of a call (5.6, Terms; 5.4.7): run_experiment.require_pass_terminated.
* Final-label aggregation (5.4, 5.6.8): parse_attempts.labels_from_records,
  final_rows and write_final_labels.
* The refusal exception: run_experiment.Refused.
* Condition identifiers (3.1.7, 3.3): build_inputs.CONDITIONS.
* Category names (6.1.1): tags.TAG_TO_CATEGORY.
* Final-label statuses (5.6.8): parse_attempts.STATUSES.
"""

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from build_inputs import CONDITIONS
from parse_attempts import (
    PASSES, STATUSES, final_rows, labels_from_records, read_final_labels, read_jsonl_strict,
    write_final_labels,
)
from run_experiment import Refused, manifest_pairs, require_pass_terminated
from tags import TAG_TO_CATEGORY

# The seven canonical categories in tag order (6.1.1; tags.py). "Not coded" is
# a substantive category, never a stand-in for a missing final label.
CATEGORIES: tuple[str, ...] = tuple(TAG_TO_CATEGORY[t] for t in sorted(TAG_TO_CATEGORY))

# Roles within build_inputs.CONDITIONS (3.1.7, 3.3). The names are not
# redefined here; these are lookups into that list.
BASELINE = "baseline"
NAMES_ONLY = "names_only"
assert BASELINE in CONDITIONS and NAMES_ONLY in CONDITIONS
# The three substantive replacements and the negative control: the conditions
# that have a baseline-referenced paired contrast (6.1.2).
PAIRED_CONDITIONS: tuple[str, ...] = tuple(c for c in CONDITIONS if c not in (BASELINE, NAMES_ONLY))

RESOLVED = "resolved"
TIE_PENDING = "tie_pending"
# Terminal missing statuses (5.4.8, 5.6.8): a pair in one of these has no
# final label and is excluded from the analysis set of that condition.
MISSING_STATUSES: tuple[str, ...] = ("unresolved_tie", "insufficient_valid_repeats")
assert set((RESOLVED, TIE_PENDING, *MISSING_STATUSES)) == set(STATUSES)


def present_passes(run_dir: Path) -> list[int]:
    """Pass numbers with a manifest or an attempts file under run_dir (check 0 of 6.1.1)."""
    return [n for n in PASSES
            if (run_dir / f"manifest_pass{n}.json").exists() or (run_dir / f"attempts_pass{n}.jsonl").exists()]


def rederived_final_labels_csv(run_dir: Path, passes: list[int]) -> bytes:
    """final_labels.csv as the parser would write it now, from the attempts files of `passes`.

    Uses the parse_attempts functions in the order parse_run() uses them
    (labels_from_records -> final_rows -> write_final_labels) but writes to a
    temporary directory, so the run directory is only read. Parser errors
    (TruncatedLastLine, CorruptedFile, ValueError) propagate unchanged.
    """
    records: list[dict] = []
    for n in passes:
        records.extend(read_jsonl_strict(run_dir / f"attempts_pass{n}.jsonl"))
    rows = labels_from_records(records)
    run_ids = {r["run_id"] for r in rows}
    if len(run_ids) != 1:
        raise Refused(f"check C (stale file): attempt records carry run_ids {sorted(run_ids)}, expected exactly one")
    finals = final_rows(rows, run_ids.pop())
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "final_labels.csv"
        write_final_labels(finals, path)
        return path.read_bytes()


def require_run_complete(run_dir: Path) -> None:
    """Refuse analysis unless the run is complete and final_labels.csv is current (6.1.1).

    The checks run in this order and the first failure raises Refused with the
    check name and the reason:

    * Check 0 (pass layout, 5.6.9): a pass is present when its manifest or its
      attempts file exists. Pass 1 must be present and the present passes must
      be 1..k without a gap.
    * Check A (termination, 6.1.1 revision 2026-09-21; 5.6, Terms): every call of
      every present pass must be terminated, i.e. have a valid response or 3
      exhausted attempts (5.4.7). run_experiment.require_pass_terminated decides
      this from the manifest and attempts file of each pass; its Refused is
      propagated unchanged. final_labels.csv cannot show an open call, which is
      why this check reads the attempt records.
    * Check C (stale file, 6.1.1 revision 2026-09-21; 5.6.8): final_labels.csv
      must exist and be byte-identical to what the parser would now write from
      all attempts files present, so a file from an earlier, partial parse is
      not analysed.
    * Check B (coverage, 6.1.1): no row may be tie_pending, and every
      (utterance_id, condition) pair of the pass 1 call list must appear exactly
      once. An absent row is an incomplete record state, not a missing label.

    Returns None when every check passes. Nothing under run_dir is written.
    """
    run_dir = Path(run_dir)

    # Check 0: pass layout.
    passes = present_passes(run_dir)
    if 1 not in passes:
        raise Refused(f"check 0 (pass layout): pass 1 is not present under {run_dir}")
    if passes != list(range(1, len(passes) + 1)):
        raise Refused(f"check 0 (pass layout): present passes {passes} are not contiguous from 1")

    # Check A: termination of every call of every present pass.
    for n in passes:
        require_pass_terminated(run_dir, n)

    # Check C: final_labels.csv equals the current aggregation of the attempts files.
    final_path = run_dir / "final_labels.csv"
    if not final_path.exists():
        raise Refused(f"check C (stale file): {final_path} does not exist; run parse_attempts.py (5.6.8)")
    if final_path.read_bytes() != rederived_final_labels_csv(run_dir, passes):
        raise Refused(f"check C (stale file): {final_path} differs from the aggregation of the attempts "
                      f"files present; rerun parse_attempts.py after the last pass (5.6.8)")

    # Check B: coverage against the pass 1 call list.
    finals = read_final_labels(final_path)
    pending = [(r["utterance_id"], r["condition"]) for r in finals if r["status"] == "tie_pending"]
    if pending:
        raise Refused(f"check B (coverage): {len(pending)} tie_pending rows remain (first {pending[:5]}); "
                      f"the next tie-break pass has not run")
    manifest = json.loads((run_dir / "manifest_pass1.json").read_text(encoding="utf-8"))
    expected = manifest_pairs(manifest)
    counts: dict[tuple[int, str], int] = {}
    for r in finals:
        key = (r["utterance_id"], r["condition"])
        counts[key] = counts.get(key, 0) + 1
    missing = sorted(p for p in expected if counts.get(p, 0) == 0)
    duplicated = sorted(p for p in expected if counts.get(p, 0) > 1)
    if missing or duplicated:
        raise Refused(f"check B (coverage): pass 1 pairs without a final_labels.csv row: {missing[:5]} "
                      f"({len(missing)} total); pairs with more than one row: {duplicated[:5]} "
                      f"({len(duplicated)} total)")
    return None


# ---------------------------------------------------------------------------
# Point estimates of κ and Δκ (6.1.1, 6.1.2, 6.2.2)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Record:
    """One sampled utterance with its human label and its six condition records (6.1.1).

    labels[c] is the final label of condition c (a name in CATEGORIES) or None
    when that condition has no final label; statuses[c] is the status of
    condition c, one of RESOLVED or MISSING_STATUSES (make_table rejects
    tie_pending). A None label is never converted to "Not coded" (6.1.2).
    """
    utterance_id: int
    human: str
    labels: dict[str, str | None]
    statuses: dict[str, str]


@dataclass(frozen=True)
class KappaResult:
    """Unweighted Cohen's κ with its integer building blocks (6.1.1, 6.2.2).

    n, agree and S are exact integers; p_o, p_e and kappa are floats or None
    (not estimable). confusion[h][p] is the number of items with human
    category h and predicted category p, over all seven categories in tag
    order, so the row and column sums are the marginals.
    """
    n: int
    agree: int
    S: int
    p_o: float | None
    p_e: float | None
    kappa: float | None
    confusion: dict[str, dict[str, int]]


@dataclass(frozen=True)
class StandaloneResult:
    """Condition-specific κ on that condition's resolved utterances (6.1.1)."""
    condition: str
    n: int
    result: KappaResult


@dataclass(frozen=True)
class PairedResult:
    """Paired complete-case contrast of one condition against baseline (6.1.2).

    baseline and condition are the κ results recomputed on the same paired
    set; delta_kappa = condition.kappa - baseline.kappa, or None when either
    κ is not estimable (6.2.2). missing_baseline and missing_condition count
    the terminal missing statuses of each side over the original table.
    discordant is the number of paired-set utterances whose baseline and
    condition final labels differ (6.2.3).
    """
    condition: str
    original_n: int
    paired_n: int
    both: int
    baseline_only: int
    condition_only: int
    neither: int
    missing_baseline: dict[str, int]
    missing_condition: dict[str, int]
    discordant: int
    baseline: KappaResult
    result: KappaResult
    delta_kappa: float | None


def make_table(human_labels: dict[int, str], final_labels: Iterable[dict]) -> list[Record]:
    """Join human labels and final-label rows into one Record per utterance (6.1.1, 6.1.2).

    human_labels maps utterance_id to the human category name. final_labels
    are rows with the keys utterance_id, condition, final_label and status, as
    parse_attempts.read_final_labels returns them; final_label may be "" or
    None when the pair has no label. Other keys are ignored.

    Raises ValueError when: a human label or a final label is not one of the
    seven CATEGORIES; a status is not in STATUSES; a status is tie_pending
    (incomplete execution, not a missing label; require_run_complete guards
    this for real runs); a resolved row has no label or a row with a terminal
    missing status has a label; an utterance does not have exactly one row per
    condition in CONDITIONS; a row belongs to an utterance without a human
    label. Missing labels stay None: they are not imputed and not converted
    to "Not coded" (6.1.2).

    The table is sorted by utterance_id so that its row order, which the
    bootstrap draws index into (6.2.1), is deterministic.
    """
    for uid, h in human_labels.items():
        if h not in CATEGORIES:
            raise ValueError(f"utterance {uid}: human label {h!r} is not a canonical category")
    seen: dict[int, dict[str, tuple[str | None, str]]] = {uid: {} for uid in human_labels}
    for row in final_labels:
        uid, cond = row["utterance_id"], row["condition"]
        if uid not in seen:
            raise ValueError(f"final-label row for utterance {uid} which has no human label")
        if cond not in CONDITIONS:
            raise ValueError(f"utterance {uid}: unknown condition {cond!r}")
        if cond in seen[uid]:
            raise ValueError(f"utterance {uid}: more than one row for condition {cond!r}")
        status = row["status"]
        if status not in STATUSES:
            raise ValueError(f"utterance {uid}, {cond}: unknown status {status!r}")
        if status == TIE_PENDING:
            raise ValueError(f"utterance {uid}, {cond}: status tie_pending is an incomplete state, not a label")
        label = row.get("final_label")
        label = None if label in (None, "") else label
        if status == RESOLVED:
            if label is None:
                raise ValueError(f"utterance {uid}, {cond}: status resolved without a final label")
            if label not in CATEGORIES:
                raise ValueError(f"utterance {uid}, {cond}: final label {label!r} is not a canonical category")
        elif label is not None:
            raise ValueError(f"utterance {uid}, {cond}: status {status} with a final label {label!r}")
        seen[uid][cond] = (label, status)
    table: list[Record] = []
    for uid in sorted(human_labels):
        conds = seen[uid]
        if set(conds) != set(CONDITIONS):
            absent = sorted(set(CONDITIONS) - set(conds))
            raise ValueError(f"utterance {uid}: no final-label row for conditions {absent}")
        table.append(Record(utterance_id=uid, human=human_labels[uid],
                            labels={c: conds[c][0] for c in CONDITIONS},
                            statuses={c: conds[c][1] for c in CONDITIONS}))
    return table


def kappa(human: list[str], predicted: list[str]) -> KappaResult:
    """Unweighted Cohen's κ of predicted against human over CATEGORIES (6.1.1, 6.2.2).

    Both lists hold category names from CATEGORIES and have the same length;
    any other value or a length mismatch raises ValueError. Category tag
    numbers define no distances or weights (6.1.1).

    Computation rules fixed for this scorer (and reused unchanged by the
    bootstrap, so there is one κ implementation, not one per use):

    1. Results p_o, p_e and kappa are floats; n, agree and S are integers.
       agree is the number of items where human == predicted and S is the
       sum over categories of (human count × predicted count).
    2. Whether κ is undefined is decided on integers, never by comparing
       floats: κ is undefined when n == 0 (empty set) or n*n == S
       (P_e = 1), as 6.2.2 defines.
    3. κ is computed from the integer form κ = (agree*n − S) / (n*n − S):
       the numerator and denominator are formed as integers and divided once.
       Likewise P_o = agree/n and P_e = S/(n*n), each a single division.
    4. fractions.Fraction is not used here; exact rationals are for the
       expected values in the tests, not for the implementation.

    When κ is undefined it is None, never 0. When n == 0, p_o and p_e are
    also None. n, agree, S and the confusion counts are returned in every
    case so that descriptive information is retained (6.2.2).
    """
    if len(human) != len(predicted):
        raise ValueError(f"human has {len(human)} labels, predicted has {len(predicted)}")
    confusion: dict[str, dict[str, int]] = {h: {p: 0 for p in CATEGORIES} for h in CATEGORIES}
    for h, p in zip(human, predicted):
        if h not in CATEGORIES:
            raise ValueError(f"human label {h!r} is not a canonical category")
        if p not in CATEGORIES:
            raise ValueError(f"predicted label {p!r} is not a canonical category")
        confusion[h][p] += 1
    n = len(human)
    agree = sum(confusion[c][c] for c in CATEGORIES)
    human_marginal = {c: sum(confusion[c].values()) for c in CATEGORIES}
    predicted_marginal = {c: sum(confusion[h][c] for h in CATEGORIES) for c in CATEGORIES}
    S = sum(human_marginal[c] * predicted_marginal[c] for c in CATEGORIES)
    if n == 0:
        return KappaResult(n=0, agree=0, S=0, p_o=None, p_e=None, kappa=None, confusion=confusion)
    p_o = agree / n
    p_e = S / (n * n)
    k = None if n * n == S else (agree * n - S) / (n * n - S)
    return KappaResult(n=n, agree=agree, S=S, p_o=p_o, p_e=p_e, kappa=k, confusion=confusion)


def standalone(table: list[Record], condition: str) -> StandaloneResult:
    """κ of one condition against the human labels on its resolved utterances (6.1.1).

    Any of the six CONDITIONS is allowed, including baseline and names_only.
    The analysis set is the records whose status in `condition` is resolved;
    the returned n is its size. Missing labels are excluded, not imputed.
    """
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition {condition!r}")
    rows = [r for r in table if r.statuses[condition] == RESOLVED]
    result = kappa([r.human for r in rows], [r.labels[condition] for r in rows])
    return StandaloneResult(condition=condition, n=result.n, result=result)


def paired(table: list[Record], condition: str) -> PairedResult:
    """Paired complete-case κ_baseline, κ_condition and Δκ for one contrast (6.1.2, 6.2.2).

    `condition` must be one of PAIRED_CONDITIONS (the three substantive
    replacements and the negative control); baseline itself and names_only
    raise ValueError, because names_only has no baseline-referenced contrast
    (3.3) and baseline has no contrast with itself.

    The paired set is the records resolved in both baseline and `condition`.
    Both κ values are recomputed on that same set with kappa(), and
    Δκ = κ_condition − κ_baseline; Δκ is None when either κ is None. Missing
    labels in any other condition, including names_only, do not affect the
    paired set. The counts both / baseline_only / condition_only / neither
    partition the original table by which of the two sides is resolved; the
    missing-status counts of each side and the condition-discordant count on
    the paired set are reported as 6.1.2 and 6.2.3 require.
    """
    if condition not in PAIRED_CONDITIONS:
        raise ValueError(f"{condition!r} has no baseline-referenced paired contrast; "
                         f"expected one of {list(PAIRED_CONDITIONS)}")
    both = baseline_only = condition_only = neither = 0
    missing_baseline = {s: 0 for s in MISSING_STATUSES}
    missing_condition = {s: 0 for s in MISSING_STATUSES}
    pair_rows: list[Record] = []
    for r in table:
        b_ok = r.statuses[BASELINE] == RESOLVED
        c_ok = r.statuses[condition] == RESOLVED
        if not b_ok:
            missing_baseline[r.statuses[BASELINE]] += 1
        if not c_ok:
            missing_condition[r.statuses[condition]] += 1
        if b_ok and c_ok:
            both += 1
            pair_rows.append(r)
        elif b_ok:
            baseline_only += 1
        elif c_ok:
            condition_only += 1
        else:
            neither += 1
    human = [r.human for r in pair_rows]
    k_base = kappa(human, [r.labels[BASELINE] for r in pair_rows])
    k_cond = kappa(human, [r.labels[condition] for r in pair_rows])
    discordant = sum(1 for r in pair_rows if r.labels[BASELINE] != r.labels[condition])
    delta = None if k_base.kappa is None or k_cond.kappa is None else k_cond.kappa - k_base.kappa
    return PairedResult(condition=condition, original_n=len(table), paired_n=len(pair_rows),
                        both=both, baseline_only=baseline_only, condition_only=condition_only,
                        neither=neither, missing_baseline=missing_baseline,
                        missing_condition=missing_condition, discordant=discordant,
                        baseline=k_base, result=k_cond, delta_kappa=delta)
