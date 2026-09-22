"""Repeated-call reliability diagnostics per condition (4.2.1-4.2.5).

Inputs are the two parser outputs of 5.6.8: labels.csv (one row per
attempt_completed: run_id, pass, utterance_id, condition, repeat, attempt,
category, valid) and final_labels.csv (one row per (utterance_id,
condition)). An "item" is one (utterance_id, condition) pair (4.2, Terms).

All indicators are descriptive statistics reported per condition. No
interval, test or between-condition contrast is computed here (4.2), and
nothing is written by this module. The computation functions take in-memory
rows so they can be checked without files; diagnostics_from_run reads the
two files of a run directory with the parse_attempts readers.

Reused, never re-implemented: parse_attempts.read_labels /
read_final_labels and its repeat constants (R_PLANNED, MAX_REPEATS);
scorer.CATEGORIES and the status names; build_inputs.CONDITIONS.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from build_inputs import CONDITIONS
from parse_attempts import MAX_REPEATS, R_PLANNED, STATUSES, read_final_labels, read_labels
from scorer import CATEGORIES, MISSING_STATUSES, RESOLVED, TIE_PENDING

# Repeats 1-3 are the planned initial repeats (5.4.1; 4.2.1 added 2026-09-22);
# repeats 4 and 5 are the tie-break calls (5.4.3; 4.2.3 added 2026-09-22).
INITIAL_REPEATS: tuple[int, ...] = tuple(range(1, R_PLANNED + 1))
TIE_BREAK_REPEATS: tuple[int, ...] = tuple(range(R_PLANNED + 1, MAX_REPEATS + 1))
PATTERNS = ("3/3", "2/1", "1/1/1")

Item = tuple[int, str]


@dataclass(frozen=True)
class ConditionDiagnostics:
    """Descriptive repeated-call indicators of one condition (4.2.1-4.2.5).

    Each ratio is stored next to its denominator so the report can show both;
    a ratio is None when its denominator is zero (4.2.5).

    n_items: items of the condition (rows of final_labels.csv).
    initial_valid_denominator: items whose repeats 1, 2 and 3 are all valid
        (4.2.1, 4.2.5); the denominator of the three patterns and of the
        unanimity rate.
    pattern_3_3 / pattern_2_1 / pattern_1_1_1 and *_share: counts and shares
        of the label pattern of the three initial valid labels within that
        denominator (4.2.5).
    unanimity_rate: pattern_3_3 / initial_valid_denominator (4.2.1).
    items_lacking_all_initial_valid: n_items - initial_valid_denominator
        (4.2.5, reported separately; not a disagreement category).
    items_with_final_label: items with status resolved; the denominator of
        mean_agreement_with_final.
    mean_agreement_with_final: mean over those items of (valid repeats whose
        label equals the final label) / (valid repeats), counting valid
        tie-break repeats (4.2.2).
    items_with_tie: items for which a repeat 4 exists in labels.csv (4.2.3).
    additional_calls_total / calls_repeat_4 / calls_repeat_5: distinct
        (item, repeat) pairs with repeat 4 or 5, exhausted or not (4.2.3,
        4.2.5: logical calls, not attempt rows).
    unresolved_tie / insufficient_valid_repeats: items with that status in
        final_labels.csv (4.2.4).
    """
    condition: str
    n_items: int
    initial_valid_denominator: int
    pattern_3_3: int
    pattern_2_1: int
    pattern_1_1_1: int
    pattern_3_3_share: float | None
    pattern_2_1_share: float | None
    pattern_1_1_1_share: float | None
    unanimity_rate: float | None
    items_lacking_all_initial_valid: int
    items_with_final_label: int
    mean_agreement_with_final: float | None
    items_with_tie: int
    additional_calls_total: int
    calls_repeat_4: int
    calls_repeat_5: int
    unresolved_tie: int
    insufficient_valid_repeats: int


def validate_rows(label_rows: list[dict], final_rows: list[dict]) -> None:
    """Reject inputs the indicators are not defined on (5.6.8, 6.1.1).

    Raises ValueError when: a labels.csv category is non-empty and not in
    CATEGORIES, or a valid row has no category; a final_labels.csv status is
    unknown or tie_pending (an incomplete run, not a terminal state); a
    condition is not in CONDITIONS; or the item sets of the two files differ
    (a stale file).
    """
    for r in label_rows:
        cat = r.get("category") or ""
        if cat and cat not in CATEGORIES:
            raise ValueError(f"labels.csv: unknown category {cat!r} for item {(r['utterance_id'], r['condition'])}")
        if r["valid"] and not cat:
            raise ValueError(f"labels.csv: valid row without a category for item {(r['utterance_id'], r['condition'])}")
        if r["condition"] not in CONDITIONS:
            raise ValueError(f"labels.csv: unknown condition {r['condition']!r}")
    for r in final_rows:
        if r["status"] not in STATUSES:
            raise ValueError(f"final_labels.csv: unknown status {r['status']!r}")
        if r["status"] == TIE_PENDING:
            raise ValueError(f"final_labels.csv: item {(r['utterance_id'], r['condition'])} is tie_pending; "
                             f"the run is not complete")
        if r["condition"] not in CONDITIONS:
            raise ValueError(f"final_labels.csv: unknown condition {r['condition']!r}")
    label_items = {(r["utterance_id"], r["condition"]) for r in label_rows}
    final_items = [(r["utterance_id"], r["condition"]) for r in final_rows]
    dup = sorted(i for i, k in Counter(final_items).items() if k > 1)
    if dup:
        raise ValueError(f"final_labels.csv: more than one row for items {dup[:5]} ({len(dup)} total)")
    if label_items != set(final_items):
        only_labels = sorted(label_items - set(final_items))
        only_finals = sorted(set(final_items) - label_items)
        raise ValueError(f"item sets differ: only in labels.csv {only_labels[:5]} ({len(only_labels)}), "
                         f"only in final_labels.csv {only_finals[:5]} ({len(only_finals)})")


def valid_label_by_repeat(rows: list[dict]) -> dict[int, str]:
    """repeat -> category of its valid attempt, for the attempt rows of one item (5.4.5).

    A repeat is valid when one of its attempts is valid; the runner stops a
    repeat at its first valid attempt, so two valid attempts of one repeat
    raise ValueError as parse_attempts.aggregate does.
    """
    out: dict[int, str] = {}
    for r in rows:
        if r["valid"]:
            if r["repeat"] in out:
                raise ValueError(f"two valid attempts for repeat {r['repeat']} of item "
                                 f"{(r['utterance_id'], r['condition'])}")
            out[r["repeat"]] = r["category"]
    return out


_PATTERN_BY_COUNTS = {(3,): "3/3", (2, 1): "2/1", (1, 1, 1): "1/1/1"}


def initial_pattern(labels: list[str]) -> str:
    """Pattern of three initial valid labels: "3/3", "2/1" or "1/1/1" (4.2.5).

    The pattern is named by the sorted label counts, using the names of 4.2.5
    ("3/3" for three identical labels).
    """
    if len(labels) != R_PLANNED:
        raise ValueError(f"expected {R_PLANNED} initial labels, got {len(labels)}")
    counts = tuple(sorted(Counter(labels).values(), reverse=True))
    return _PATTERN_BY_COUNTS[counts]


def share(numerator: int, denominator: int) -> float | None:
    """numerator / denominator, or None when the denominator is zero (4.2.5)."""
    return None if denominator == 0 else numerator / denominator


def condition_diagnostics(label_rows: list[dict], final_rows: list[dict]) -> dict[str, ConditionDiagnostics]:
    """Compute the 4.2 indicators for every condition in CONDITIONS from in-memory rows.

    label_rows are labels.csv rows as parse_attempts.read_labels returns
    them (utterance_id, repeat, attempt as int; valid as bool); final_rows
    are final_labels.csv rows as read_final_labels returns them. Inputs are
    checked by validate_rows first. Conditions without any item get all
    counts 0 and all ratios None.
    """
    validate_rows(label_rows, final_rows)
    by_item: dict[Item, list[dict]] = defaultdict(list)
    for r in label_rows:
        by_item[(r["utterance_id"], r["condition"])].append(r)
    final_by_item: dict[Item, dict] = {(r["utterance_id"], r["condition"]): r for r in final_rows}

    out: dict[str, ConditionDiagnostics] = {}
    for cond in CONDITIONS:
        items = sorted(i for i in final_by_item if i[1] == cond)
        patterns: Counter[str] = Counter()
        agreement_ratios: list[float] = []
        items_with_tie = 0
        calls_by_repeat: Counter[int] = Counter()
        status_counts: Counter[str] = Counter()
        for item in items:
            rows = by_item[item]
            valid_labels = valid_label_by_repeat(rows)
            repeats_present = {r["repeat"] for r in rows}

            # 4.2.1 / 4.2.5: initial pattern on repeats 1-3, tie-breaks excluded.
            if all(k in valid_labels for k in INITIAL_REPEATS):
                patterns[initial_pattern([valid_labels[k] for k in INITIAL_REPEATS])] += 1

            # 4.2.2: agreement with the final label over all valid repeats, 1-5.
            final = final_by_item[item]
            if final["status"] == RESOLVED:
                n_valid = len(valid_labels)
                n_agree = sum(1 for lab in valid_labels.values() if lab == final["final_label"])
                agreement_ratios.append(n_agree / n_valid)

            # 4.2.3 / 4.2.5: ties and logical tie-break calls.
            if TIE_BREAK_REPEATS[0] in repeats_present:
                items_with_tie += 1
            for k in TIE_BREAK_REPEATS:
                if k in repeats_present:
                    calls_by_repeat[k] += 1

            # 4.2.4: terminal missing statuses.
            status_counts[final["status"]] += 1

        n_items = len(items)
        denom = sum(patterns.values())
        n_final = len(agreement_ratios)
        out[cond] = ConditionDiagnostics(
            condition=cond,
            n_items=n_items,
            initial_valid_denominator=denom,
            pattern_3_3=patterns["3/3"],
            pattern_2_1=patterns["2/1"],
            pattern_1_1_1=patterns["1/1/1"],
            pattern_3_3_share=share(patterns["3/3"], denom),
            pattern_2_1_share=share(patterns["2/1"], denom),
            pattern_1_1_1_share=share(patterns["1/1/1"], denom),
            unanimity_rate=share(patterns["3/3"], denom),
            items_lacking_all_initial_valid=n_items - denom,
            items_with_final_label=n_final,
            mean_agreement_with_final=None if n_final == 0 else sum(agreement_ratios) / n_final,
            items_with_tie=items_with_tie,
            additional_calls_total=sum(calls_by_repeat[k] for k in TIE_BREAK_REPEATS),
            calls_repeat_4=calls_by_repeat[TIE_BREAK_REPEATS[0]],
            calls_repeat_5=calls_by_repeat[TIE_BREAK_REPEATS[1]],
            unresolved_tie=status_counts[MISSING_STATUSES[0]],
            insufficient_valid_repeats=status_counts[MISSING_STATUSES[1]],
        )
    return out


def diagnostics_from_run(run_dir: Path) -> dict[str, ConditionDiagnostics]:
    """Read labels.csv and final_labels.csv of run_dir and compute the 4.2 indicators.

    Uses parse_attempts.read_labels and read_final_labels (5.6.8). The run
    directory is only read. Completeness of the run (termination, stale
    files) is the scorer's entry check (6.1.1) and is not repeated here;
    tie_pending rows are still rejected by validate_rows.
    """
    run_dir = Path(run_dir)
    return condition_diagnostics(read_labels(run_dir / "labels.csv"),
                                 read_final_labels(run_dir / "final_labels.csv"))
