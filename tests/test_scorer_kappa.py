"""Point-estimate checks for scorer.make_table / kappa / standalone / paired (6.6).

Every expected value is the hand-checkable number written in
decisions/06-analysis.md 6.6, entered here as a fractions.Fraction literal.
Nothing is computed with the code under test to obtain an expected value.
The examples are synthetic, not research observations; no API is called.

Category letters follow 6.6: A = Not coded (tag 0), B = Keeping Everyone
Together (tag 1). The replacement column of the 6.6 table is placed in the
first PAIRED_CONDITIONS entry; every condition the table does not mention is
filled with a resolved arbitrary category so that only the two sides under
test carry missing labels.
"""

from fractions import Fraction

import pytest

import scorer
from build_inputs import CONDITIONS
from scorer import BASELINE, NAMES_ONLY, PAIRED_CONDITIONS, kappa, make_table, paired, standalone
from tags import TAG_TO_CATEGORY

A = "Not coded"
B = "Keeping Everyone Together"
REPL = PAIRED_CONDITIONS[0]
FILLER = "Restating"           # resolved label for conditions the 6.6 table does not mention
TOL = 1e-12

RESOLVED = "resolved"
UT = "unresolved_tie"
IVR = "insufficient_valid_repeats"


def close(value, expected: Fraction) -> bool:
    """abs(value - float(expected)) < TOL; None never passes."""
    return value is not None and abs(value - float(expected)) < TOL


def row(uid: int, cond: str, label: str | None, status: str) -> dict:
    """One final_labels.csv-shaped row; a missing label is the empty string as the parser writes it."""
    return {"utterance_id": uid, "condition": cond, "final_label": "" if label is None else label,
            "status": status}


def build(items: list[tuple], overrides: dict[tuple[int, str], tuple[str | None, str]] | None = None):
    """Table from (uid, human, (baseline label, status), (replacement label, status)) items.

    Every other condition is resolved FILLER unless `overrides` gives a
    (label, status) for a (uid, condition).
    """
    overrides = overrides or {}
    human = {uid: h for uid, h, _, _ in items}
    rows = []
    for uid, _, base, repl in items:
        for cond in CONDITIONS:
            if cond == BASELINE:
                label, status = base
            elif cond == REPL:
                label, status = repl
            else:
                label, status = overrides.get((uid, cond), (FILLER, RESOLVED))
            rows.append(row(uid, cond, label, status))
    return make_table(human, rows)


# The 6.6 six-item table. A dash in 6.6 is (None, <status>), never category A.
ITEMS_66 = [
    (1, A, (A, RESOLVED), (A, RESOLVED)),
    (2, A, (B, RESOLVED), (A, RESOLVED)),
    (3, B, (B, RESOLVED), (A, RESOLVED)),
    (4, B, (A, RESOLVED), (B, RESOLVED)),
    (5, A, (A, RESOLVED), (None, UT)),
    (6, B, (None, IVR), (B, RESOLVED)),
]


def ab_block(confusion: dict[str, dict[str, int]]) -> list[list[int]]:
    """The (A, B) x (A, B) corner of a confusion table, human rows, predicted columns."""
    return [[confusion[A][A], confusion[A][B]], [confusion[B][A], confusion[B][B]]]


def total(confusion: dict[str, dict[str, int]]) -> int:
    return sum(sum(r.values()) for r in confusion.values())


# --- 1. canonical mapping ---------------------------------------------------

def test_canonical_mapping_matches_6_6():
    expected = {0: "Not coded", 1: "Keeping Everyone Together", 2: "Getting Students to Relate",
                3: "Restating", 4: "Revoicing", 5: "Pressing for Accuracy", 6: "Pressing for Reasoning"}
    assert TAG_TO_CATEGORY == expected
    assert scorer.CATEGORIES == tuple(expected[t] for t in range(7))


# --- 2. paired contrast on the six-item table -------------------------------

def test_paired_six_item_table():
    res = paired(build(ITEMS_66), REPL)
    assert res.original_n == 6
    assert res.paired_n == 4
    assert (res.both, res.baseline_only, res.condition_only, res.neither) == (4, 1, 1, 0)

    assert ab_block(res.baseline.confusion) == [[1, 1], [1, 1]]
    assert ab_block(res.result.confusion) == [[2, 0], [1, 1]]
    assert total(res.baseline.confusion) == 4 and total(res.result.confusion) == 4

    assert res.baseline.n == 4 and res.baseline.agree == 2
    assert close(res.baseline.p_o, Fraction(1, 2))
    assert close(res.baseline.p_e, Fraction(1, 2))
    assert close(res.baseline.kappa, Fraction(0))

    assert res.result.n == 4 and res.result.agree == 3
    assert close(res.result.p_o, Fraction(3, 4))
    assert close(res.result.p_e, Fraction(1, 2))
    assert close(res.result.kappa, Fraction(1, 2))

    assert close(res.delta_kappa, Fraction(1, 2))
    assert res.discordant == 3

    assert res.missing_condition == {UT: 1, IVR: 0}
    assert res.missing_baseline == {UT: 0, IVR: 1}


# --- 3. standalone κ ----------------------------------------------------------

def test_standalone_baseline_and_replacement():
    table = build(ITEMS_66)
    base = standalone(table, BASELINE)
    assert base.n == 5 and base.result.n == 5
    assert close(base.result.p_o, Fraction(3, 5))
    assert close(base.result.p_e, Fraction(13, 25))
    assert close(base.result.kappa, Fraction(1, 6))

    repl = standalone(table, REPL)
    assert repl.n == 5 and repl.result.n == 5
    assert close(repl.result.p_o, Fraction(4, 5))
    assert close(repl.result.p_e, Fraction(12, 25))
    assert close(repl.result.kappa, Fraction(8, 13))

    # The standalone baseline κ (items 1-5) is not the paired-set baseline κ (items 1-4).
    paired_base = paired(table, REPL).baseline.kappa
    assert abs(base.result.kappa - paired_base) > TOL


# --- 4. names-only missingness does not touch the paired set ----------------

def test_names_only_missing_leaves_pair_unchanged():
    ref = paired(build(ITEMS_66), REPL)
    res = paired(build(ITEMS_66, {(1, NAMES_ONLY): (None, UT)}), REPL)
    assert res.paired_n == ref.paired_n == 4
    assert (res.both, res.baseline_only, res.condition_only, res.neither) == \
        (ref.both, ref.baseline_only, ref.condition_only, ref.neither)
    assert res.missing_baseline == ref.missing_baseline
    assert res.missing_condition == ref.missing_condition
    assert res.discordant == ref.discordant == 3
    assert close(res.baseline.kappa, Fraction(0))
    assert close(res.result.kappa, Fraction(1, 2))
    assert close(res.delta_kappa, Fraction(1, 2))


# --- 5. items 5 and 6 are not imputed into the pair ---------------------------

def test_missing_labels_are_not_counted_as_not_coded():
    res = paired(build(ITEMS_66), REPL)
    assert res.paired_n == 4
    assert total(res.baseline.confusion) == 4
    assert total(res.result.confusion) == 4
    # Item 5 (human A, replacement missing) would add to the (A, Not coded) cell if imputed.
    assert res.result.confusion[A][A] == 2
    # Item 6 (human B, baseline missing) would add to the (B, Not coded) cell if imputed.
    assert res.baseline.confusion[B][A] == 1


# --- 6. undefined statistics -------------------------------------------------

def test_undefined_baseline_kappa_is_none_not_zero():
    items = [(1, A, (A, RESOLVED), (B, RESOLVED)),
             (2, A, (A, RESOLVED), (B, RESOLVED))]
    res = paired(build(items), REPL)
    assert res.paired_n == 2
    assert res.baseline.kappa is None
    assert res.delta_kappa is None
    assert close(res.result.kappa, Fraction(0))
    # Descriptive information is retained for the undefined side (6.2.2).
    assert res.baseline.n == 2 and res.baseline.agree == 2
    assert close(res.baseline.p_o, Fraction(1))
    assert close(res.baseline.p_e, Fraction(1))
    assert ab_block(res.baseline.confusion) == [[2, 0], [0, 0]]
    assert ab_block(res.result.confusion) == [[0, 2], [0, 0]]


def test_empty_paired_set_is_not_estimable():
    items = [(1, A, (None, IVR), (A, RESOLVED)),
             (2, B, (None, UT), (B, RESOLVED))]
    res = paired(build(items), REPL)
    assert res.paired_n == 0
    assert (res.both, res.baseline_only, res.condition_only, res.neither) == (0, 0, 2, 0)
    for k in (res.baseline, res.result):
        assert k.n == 0
        assert k.kappa is None
        assert k.p_o is None
        assert k.p_e is None
    assert res.delta_kappa is None


def test_kappa_empty_input_is_not_estimable():
    k = kappa([], [])
    assert k.n == 0 and k.agree == 0 and k.S == 0
    assert k.kappa is None and k.p_o is None and k.p_e is None


# --- 7. identical labels -------------------------------------------------------

def test_identical_labels():
    items = [(1, A, (A, RESOLVED), (A, RESOLVED)),
             (2, A, (A, RESOLVED), (A, RESOLVED)),
             (3, B, (B, RESOLVED), (B, RESOLVED)),
             (4, B, (B, RESOLVED), (B, RESOLVED))]
    res = paired(build(items), REPL)
    assert res.paired_n == 4
    assert close(res.baseline.kappa, Fraction(1))
    assert close(res.result.kappa, Fraction(1))
    assert close(res.delta_kappa, Fraction(0))
    assert res.discordant == 0


# --- 8-10. make_table refuses inconsistent label/status rows -----------------

def test_resolved_without_label_is_rejected():
    with pytest.raises(ValueError):
        build([(1, A, (None, RESOLVED), (A, RESOLVED))])


@pytest.mark.parametrize("status", [UT, IVR])
def test_missing_status_with_label_is_rejected(status):
    with pytest.raises(ValueError):
        build([(1, A, (A, status), (A, RESOLVED))])


def test_tie_pending_is_rejected():
    with pytest.raises(ValueError):
        build([(1, A, (A, RESOLVED), (None, "tie_pending"))])


# --- 11. paired refuses baseline and names_only --------------------------------

@pytest.mark.parametrize("condition", [BASELINE, NAMES_ONLY])
def test_paired_rejects_non_contrast_conditions(condition):
    table = build(ITEMS_66)
    with pytest.raises(ValueError):
        paired(table, condition)
