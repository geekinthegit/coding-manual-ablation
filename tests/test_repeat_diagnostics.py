"""Checks for repeat_diagnostics (4.2.1-4.2.5) and scorer.load_table (6.1.1, 5.6.8).

The 4.2 case is a hand-computed five-item history for the baseline
condition, entered as attempt-level labels.csv rows and final_labels.csv
rows in the shape parse_attempts.read_labels / read_final_labels return.
Expected values are the hand-computed numbers, written as Fraction literals;
nothing is computed with the code under test. The load_table checks build a
terminated synthetic run with the helpers of tests/test_scorer_entry.py
(real planner, real runner with a fake client, real parser) and a temporary
scoring_labels.csv. No API is called; the data are synthetic.
"""

from fractions import Fraction

import pytest

import parse_attempts as pa
import repeat_diagnostics as rd
import run_experiment as rx
import scorer
from build_inputs import CONDITIONS
from tests.test_scorer_entry import RUN_ID, always, prepare_run, run_pass1

A = "Not coded"
B = "Keeping Everyone Together"
C = "Restating"
BASE = "baseline"
TOL = 1e-12

PASS_OF_REPEAT = {1: 1, 2: 1, 3: 1, 4: 2, 5: 3}


def close(value, expected: Fraction) -> bool:
    return value is not None and abs(value - float(expected)) < TOL


def lab(uid: int, cond: str, repeat: int, attempt: int, category: str, valid: bool) -> dict:
    """One labels.csv row in the read_labels shape (5.6.8)."""
    return {"run_id": "t", "pass": PASS_OF_REPEAT[repeat], "utterance_id": uid, "condition": cond,
            "repeat": repeat, "attempt": attempt, "category": category, "valid": valid}


def invalid_repeat(uid: int, cond: str, repeat: int) -> list[dict]:
    """A repeat exhausted by three invalid attempts: three rows, no category, valid False."""
    return [lab(uid, cond, repeat, a, "", False) for a in (1, 2, 3)]


def fin(uid: int, cond: str, label: str | None, status: str, valid_repeats: int, repeats_used: int) -> dict:
    """One final_labels.csv row in the read_final_labels shape (5.6.8)."""
    return {"run_id": "t", "utterance_id": uid, "condition": cond, "final_label": "" if label is None else label,
            "status": status, "valid_repeats": valid_repeats, "repeats_used": repeats_used}


def five_item_case() -> tuple[list[dict], list[dict]]:
    """The hand-computed baseline history; every other condition is 3/3 A resolved."""
    labels: list[dict] = []
    finals: list[dict] = []
    # Item A (uid 1): 1/1/1, repeat 4 exhausted, repeat 5 valid A -> resolved A.
    labels += [lab(1, BASE, 1, 1, A, True), lab(1, BASE, 2, 1, B, True), lab(1, BASE, 3, 1, C, True)]
    labels += invalid_repeat(1, BASE, 4) + [lab(1, BASE, 5, 1, A, True)]
    finals.append(fin(1, BASE, A, "resolved", 4, 5))
    # Item B (uid 2): 3/3 A -> resolved A.
    labels += [lab(2, BASE, k, 1, A, True) for k in (1, 2, 3)]
    finals.append(fin(2, BASE, A, "resolved", 3, 3))
    # Item C (uid 3): repeat 2 exhausted, A/B tie on two valid repeats, repeat 4 A -> resolved A.
    labels += [lab(3, BASE, 1, 1, A, True)] + invalid_repeat(3, BASE, 2) + [lab(3, BASE, 3, 1, B, True)]
    labels += [lab(3, BASE, 4, 1, A, True)]
    finals.append(fin(3, BASE, A, "resolved", 3, 4))
    # Item D (uid 4): 1/1/1, repeat 4 A, repeat 5 B, still tied -> unresolved_tie.
    labels += [lab(4, BASE, 1, 1, A, True), lab(4, BASE, 2, 1, B, True), lab(4, BASE, 3, 1, C, True)]
    labels += [lab(4, BASE, 4, 1, A, True), lab(4, BASE, 5, 1, B, True)]
    finals.append(fin(4, BASE, None, "unresolved_tie", 5, 5))
    # Item E (uid 5): repeat 1 A, repeats 2 and 3 exhausted -> insufficient_valid_repeats.
    labels += [lab(5, BASE, 1, 1, A, True)] + invalid_repeat(5, BASE, 2) + invalid_repeat(5, BASE, 3)
    finals.append(fin(5, BASE, None, "insufficient_valid_repeats", 1, 3))
    # Other conditions: repeats 1-3 valid A, resolved A.
    for cond in CONDITIONS:
        if cond == BASE:
            continue
        for uid in (1, 2, 3, 4, 5):
            labels += [lab(uid, cond, k, 1, A, True) for k in (1, 2, 3)]
            finals.append(fin(uid, cond, A, "resolved", 3, 3))
    return labels, finals


# --- 1. hand-computed baseline values (4.2.1-4.2.5) ----------------------------------

def test_baseline_five_item_case():
    d = rd.condition_diagnostics(*five_item_case())[BASE]
    assert d.condition == BASE
    assert d.n_items == 5
    assert d.initial_valid_denominator == 3
    assert (d.pattern_3_3, d.pattern_2_1, d.pattern_1_1_1) == (1, 0, 2)
    assert close(d.pattern_3_3_share, Fraction(1, 3))
    assert close(d.pattern_2_1_share, Fraction(0))
    assert close(d.pattern_1_1_1_share, Fraction(2, 3))
    assert close(d.unanimity_rate, Fraction(1, 3))
    assert d.items_lacking_all_initial_valid == 2
    assert d.items_with_final_label == 3
    assert close(d.mean_agreement_with_final, Fraction(13, 18))
    assert d.items_with_tie == 3
    # Item A's exhausted repeat 4 has three attempt rows but counts once (4.2.3, logical calls).
    assert d.calls_repeat_4 == 3
    assert d.calls_repeat_5 == 2
    assert d.additional_calls_total == 5
    assert d.unresolved_tie == 1
    assert d.insufficient_valid_repeats == 1


# --- 2. the untouched conditions ----------------------------------------------------------

def test_other_conditions_are_all_unanimous():
    result = rd.condition_diagnostics(*five_item_case())
    assert set(result) == set(CONDITIONS)
    for cond in CONDITIONS:
        if cond == BASE:
            continue
        d = result[cond]
        assert d.n_items == 5
        assert d.pattern_3_3 == 5 and d.initial_valid_denominator == 5
        assert (d.pattern_2_1, d.pattern_1_1_1) == (0, 0)
        assert close(d.unanimity_rate, Fraction(1))
        assert d.items_with_final_label == 5
        assert close(d.mean_agreement_with_final, Fraction(1))
        assert d.items_lacking_all_initial_valid == 0
        assert d.items_with_tie == 0
        assert (d.additional_calls_total, d.calls_repeat_4, d.calls_repeat_5) == (0, 0, 0)
        assert (d.unresolved_tie, d.insufficient_valid_repeats) == (0, 0)


# --- 3. initial_pattern (4.2.5) -------------------------------------------------------------

def test_initial_pattern_names():
    assert rd.initial_pattern([A, A, A]) == "3/3"
    assert rd.initial_pattern([A, A, B]) == "2/1"
    assert rd.initial_pattern([A, B, C]) == "1/1/1"
    with pytest.raises(ValueError):
        rd.initial_pattern([A, A])


# --- 4. zero denominator (4.2.5) ----------------------------------------------------------

def test_zero_initial_denominator_gives_none_ratios():
    labels: list[dict] = []
    finals: list[dict] = []
    for cond in CONDITIONS:
        for uid in (1, 2):
            # Repeat 2 exhausted in every item: no item has all three initial repeats valid.
            labels += [lab(uid, cond, 1, 1, A, True)] + invalid_repeat(uid, cond, 2) + [lab(uid, cond, 3, 1, A, True)]
            finals.append(fin(uid, cond, A, "resolved", 2, 3))
    d = rd.condition_diagnostics(labels, finals)[BASE]
    assert d.n_items == 2
    assert d.initial_valid_denominator == 0
    assert d.pattern_3_3_share is None and d.pattern_2_1_share is None and d.pattern_1_1_1_share is None
    assert d.unanimity_rate is None
    assert d.items_lacking_all_initial_valid == d.n_items == 2


# --- 5. refusals (5.6.8, 6.1.1) -------------------------------------------------------------

def test_tie_pending_is_rejected():
    labels, finals = five_item_case()
    finals = [dict(r, status="tie_pending", final_label="") if (r["utterance_id"], r["condition"]) == (4, BASE) else r
              for r in finals]
    with pytest.raises(ValueError):
        rd.condition_diagnostics(labels, finals)


def test_item_set_mismatch_is_rejected():
    labels, finals = five_item_case()
    finals = [r for r in finals if (r["utterance_id"], r["condition"]) != (5, BASE)]
    with pytest.raises(ValueError):
        rd.condition_diagnostics(labels, finals)


def test_two_valid_attempts_in_one_repeat_are_rejected():
    labels, finals = five_item_case()
    labels = labels + [lab(2, BASE, 1, 2, A, True)]   # item B already has a valid attempt 1 of repeat 1
    with pytest.raises(ValueError):
        rd.condition_diagnostics(labels, finals)


def test_unknown_category_is_rejected():
    labels, finals = five_item_case()
    labels = [dict(r, category="Foo") if (r["utterance_id"], r["condition"], r["repeat"]) == (2, BASE, 1) else r
              for r in labels]
    with pytest.raises(ValueError):
        rd.condition_diagnostics(labels, finals)


def test_valid_row_without_category_is_rejected():
    labels, finals = five_item_case()
    labels = [dict(r, category="") if (r["utterance_id"], r["condition"], r["repeat"]) == (2, BASE, 1) else r
              for r in labels]
    with pytest.raises(ValueError):
        rd.condition_diagnostics(labels, finals)


# --- 6-8. load_table on a terminated synthetic run (6.1.1, 5.6.8) ---------------------------

def write_scoring_labels(path, rows: list[tuple[int, int, int]]) -> None:
    """scoring_labels.csv with columns source_id, source_row_id, Tag."""
    path.write_text("source_id,source_row_id,Tag\n" + "".join(f"{s},{r},{t}\n" for s, r, t in rows),
                    encoding="utf-8")


def completed_run(tmp_path, monkeypatch):
    """A pass 1 run for utterances 1 and 2, every call Not coded, parsed (5.6.8)."""
    run_dir = prepare_run(tmp_path, monkeypatch, ids=(1, 2))
    run_pass1(run_dir, always("Not coded"))
    pa.parse_run(run_dir, RUN_ID)
    return run_dir


def test_load_table_reads_run_and_human_labels(tmp_path, monkeypatch):
    run_dir = completed_run(tmp_path, monkeypatch)
    labels_path = tmp_path / "scoring_labels.csv"
    write_scoring_labels(labels_path, [(1, 1, 0), (2, 2, 1)])
    loaded = scorer.load_table(run_dir, labels_path)
    assert loaded.run_dir == run_dir
    assert len(loaded.table) == 2
    assert [r.utterance_id for r in loaded.table] == [1, 2]
    assert [r.human for r in loaded.table] == ["Not coded", "Keeping Everyone Together"]
    for rec in loaded.table:
        assert set(rec.statuses) == set(CONDITIONS)
        assert all(s == "resolved" for s in rec.statuses.values())
        assert all(lab == "Not coded" for lab in rec.labels.values())
    for digest in (loaded.final_labels_sha256, loaded.scoring_labels_sha256):
        assert len(digest) == 64 and all(ch in "0123456789abcdef" for ch in digest)


def test_load_table_propagates_refusal_of_unparsed_run(tmp_path, monkeypatch):
    run_dir = prepare_run(tmp_path, monkeypatch, ids=(1, 2))
    run_pass1(run_dir, always("Not coded"))           # terminated, but parse_run not run: no final_labels.csv
    labels_path = tmp_path / "scoring_labels.csv"
    write_scoring_labels(labels_path, [(1, 1, 0), (2, 2, 1)])
    with pytest.raises(rx.Refused):
        scorer.load_table(run_dir, labels_path)


@pytest.mark.parametrize("rows", [
    [(1, 1, 0)],                       # utterance 2 has no row
    [(1, 1, 0), (2, 2, 1), (2, 3, 1)],  # duplicated source_id
    [(1, 1, 0), (2, 2, 7)],            # Tag 7 is not in tags.TAG_TO_CATEGORY
])
def test_load_table_rejects_bad_scoring_labels(tmp_path, monkeypatch, rows):
    run_dir = completed_run(tmp_path, monkeypatch)
    labels_path = tmp_path / "scoring_labels.csv"
    write_scoring_labels(labels_path, rows)
    with pytest.raises(ValueError):
        scorer.load_table(run_dir, labels_path)
